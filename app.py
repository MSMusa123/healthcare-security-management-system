from flask import Flask, render_template, request, redirect, url_for, session
from database.db import get_db_connection
from security.auth import verify_password
from security.access_control import check_patient_access
from security.audit_log import create_audit_log, verify_audit_log_integrity
from security.risk_engine import calculate_risk_score
from security.anomaly_detector import detect_unusual_access
from security.alerts import create_security_alert
from security.emergency import (
    grant_emergency_access,
    check_emergency_access,
    update_expired_emergency_access
)
from security.offline_mode import (
    get_unsynced_offline_access,
    synchronize_offline_access
)

app = Flask(__name__)

app.secret_key = "hsms-development-secret-key"


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and verify_password(password, user["password_hash"]):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["ward"] = user["ward"]

            return redirect(url_for("dashboard"))

        return "Invalid username or password"


    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Update expired emergency access
    update_expired_emergency_access()

    connection = get_db_connection()

    # Total users
    total_users = connection.execute(
        "SELECT COUNT(*) AS count FROM users"
    ).fetchone()["count"]

    # Total patients
    total_patients = connection.execute(
        "SELECT COUNT(*) AS count FROM patients"
    ).fetchone()["count"]

    # Open security alerts
    open_alerts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM security_alerts
        WHERE status = 'open'
        """
    ).fetchone()["count"]

    # Total audit logs
    total_audit_logs = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM audit_logs
        """
    ).fetchone()["count"]

    # Active emergency access
    active_emergency = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM emergency_access
        WHERE status = 'ACTIVE'
        """
    ).fetchone()["count"]

    # High-risk alerts
    high_risk_alerts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM security_alerts
        WHERE severity = 'HIGH'
        AND status = 'open'
        """
    ).fetchone()["count"]

    # Recent audit activity
    recent_logs = connection.execute(
        """
        SELECT
            audit_logs.*,
            users.full_name AS user_name
        FROM audit_logs
        LEFT JOIN users
            ON audit_logs.user_id = users.id
        ORDER BY audit_logs.id DESC
        LIMIT 8
        """
    ).fetchall()

    connection.close()

    # Offline emergency events waiting for synchronization
    from security.offline_mode import get_unsynced_offline_access

    unsynced_offline = get_unsynced_offline_access()

    return render_template(
        "dashboard.html",
        full_name=session["full_name"],
        role=session["role"],
        ward=session["ward"],
        total_users=total_users,
        total_patients=total_patients,
        open_alerts=open_alerts,
        total_audit_logs=total_audit_logs,
        active_emergency=active_emergency,
        high_risk_alerts=high_risk_alerts,
        recent_logs=recent_logs,
        unsynced_offline=len(unsynced_offline)
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/patients")
def patients():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    patient_list = connection.execute(
        "SELECT * FROM patients"
    ).fetchall()

    connection.close()

    return render_template(
        "patients.html",
        patients=patient_list,
        full_name=session["full_name"],
        role=session["role"]
    )
@app.route("/audit")
def audit_logs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    logs = connection.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "audit.html",
        logs=logs
    )
@app.route("/verify-audit")
def verify_audit():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Security Administrator":
        return "Access denied. Security Administrator privileges required.", 403

    result = verify_audit_log_integrity()

    return render_template(
        "audit_verification.html",
        result=result
    )
@app.route("/patient/<int:patient_id>")
def patient_detail(patient_id):

    # Make sure user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    # Get logged-in user
    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    # Get requested patient
    patient = connection.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    connection.close()

    # Patient does not exist
    if patient is None:

        create_audit_log(
            session["user_id"],
            "PATIENT_NOT_FOUND",
            patient_id,
            "Attempted to access a patient record that does not exist"
        )

        return "Patient not found", 404

      # --------------------------------
    # CHECK ACTIVE EMERGENCY ACCESS
    # --------------------------------

    emergency = check_emergency_access(
        session["user_id"],
        patient_id
    )

    if emergency["active"]:

        create_audit_log(
            session["user_id"],
            "PATIENT_ACCESS_EMERGENCY",
            patient_id,
            (
                "Patient accessed through active emergency access | "
                f"Expires: {emergency['expires_at']}"
            )
        )

        return render_template(
            "patient.html",
            patient=patient,
            decision={
                "decision": "EMERGENCY_ALLOW",
                "reason": "Active emergency access"
            },
            risk={
                "score": 90,
                "level": "HIGH",
                "reasons": [
                    "Patient accessed through emergency break-glass access"
                ]
            }
        )
    # --------------------------------
    # ACCESS CONTROL
    # --------------------------------

    decision = check_patient_access(user, patient)

    # --------------------------------
    # RISK ANALYSIS
    # --------------------------------

    risk = calculate_risk_score(
        user,
        patient,
        decision
    )

    # --------------------------------
    # INSIDER THREAT DETECTION
    # --------------------------------

    anomaly = detect_unusual_access(
        session["user_id"]
    )

    if anomaly["anomaly"]:

        create_security_alert(
            session["user_id"],
            "UNUSUAL_PATIENT_ACCESS",
            anomaly["severity"],
            anomaly["message"],
            anomaly["risk_score"]
        )

    # --------------------------------
    # AUDIT LOG
    # --------------------------------

    create_audit_log(
        session["user_id"],
        f"PATIENT_ACCESS_{decision['decision']}",
        patient_id,
        f"{decision['reason']} | Risk: {risk['score']} | Level: {risk['level']}"
    )

    # --------------------------------
    # ACCESS BLOCKED OR RESTRICTED
    # --------------------------------

    if decision["decision"] != "ALLOW":

        return render_template(
            "access_denied.html",
            decision=decision,
            patient=patient,
            risk=risk
        )

    # --------------------------------
    # ACCESS ALLOWED
    # --------------------------------

    return render_template(
        "patient.html",
        patient=patient,
        decision=decision,
        risk=risk
    )
@app.route("/alerts")
def alerts():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    alert_list = connection.execute(
        """
        SELECT *
        FROM security_alerts
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "alerts.html",
        alerts=alert_list
    )
@app.route("/emergency/<int:patient_id>", methods=["GET", "POST"])
def emergency_access(patient_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    patient = connection.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    connection.close()

    if patient is None:
        return "Patient not found", 404

    if request.method == "POST":

        reason = request.form.get("reason", "").strip()

        result = grant_emergency_access(
            session["user_id"],
            patient_id,
            reason
        )

        if not result["success"]:
            return render_template(
                "emergency.html",
                patient=patient,
                error=result["message"]
            )

        return render_template(
            "emergency.html",
            patient=patient,
            success=result["message"],
            expires_at=result["expires_at"]
        )

    return render_template(
        "emergency.html",
        patient=patient
    )
@app.route("/emergency-management")
def emergency_management():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only Security Administrators can view
    # emergency access records
    if session["role"] != "Security Administrator":
        return "Access denied. Security Administrator privileges required.", 403

    # Update expired emergency access records
    update_expired_emergency_access()

    connection = get_db_connection()

    emergency_list = connection.execute(
        """
        SELECT
            emergency_access.id,
            emergency_access.user_id,
            emergency_access.patient_id,
            emergency_access.reason,
            emergency_access.risk_score,
            emergency_access.status,
            emergency_access.created_at,
            emergency_access.expires_at,
            users.full_name AS user_name,
            users.role AS user_role,
            patients.patient_number,
            patients.full_name AS patient_name
        FROM emergency_access
        JOIN users
            ON emergency_access.user_id = users.id
        JOIN patients
            ON emergency_access.patient_id = patients.id
        ORDER BY emergency_access.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "emergency_management.html",
        emergency_list=emergency_list
    )
@app.route("/offline-management", methods=["GET", "POST"])
def offline_management():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Security Administrator":
        return "Access denied. Security Administrator privileges required.", 403

    message = None

    if request.method == "POST":

        synchronized = synchronize_offline_access()

        message = (
            f"{synchronized} offline event(s) synchronized successfully."
        )

    offline_records = get_unsynced_offline_access()

    return render_template(
        "offline_management.html",
        offline_records=offline_records,
        message=message
    )
@app.route("/offline-emergency/<int:patient_id>", methods=["GET", "POST"])
def offline_emergency(patient_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    patient = connection.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    connection.close()

    if patient is None:
        return "Patient not found", 404

    if request.method == "POST":

        reason = request.form.get("reason", "").strip()

        from security.offline_mode import create_offline_emergency_access

        result = create_offline_emergency_access(
            session["user_id"],
            patient_id,
            reason
        )

        if not result["success"]:

            return render_template(
                "offline_emergency.html",
                patient=patient,
                error=result["message"]
            )

        return render_template(
            "offline_emergency.html",
            patient=patient,
            success=result["message"],
            created_at=result["created_at"]
        )

    return render_template(
        "offline_emergency.html",
        patient=patient
    )
if __name__ == "__main__":
    app.run(debug=True)
   