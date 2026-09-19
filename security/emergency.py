from datetime import datetime, timedelta

from database.db import get_db_connection
from security.audit_log import create_audit_log
from security.alerts import create_security_alert


def grant_emergency_access(user_id, patient_id, reason):
    """
    Grant temporary emergency access to a patient record.

    Emergency access is deliberately high-risk and is always
    recorded in the audit trail.
    """

    # Check emergency reason
    if not reason or not reason.strip():
        return {
            "success": False,
            "message": "Emergency access requires a reason."
        }

    # Require a meaningful reason
    if len(reason.strip()) < 15:
        return {
            "success": False,
            "message": "Emergency reason must contain at least 15 characters."
        }

    connection = get_db_connection()

    # Check that the patient exists
    patient = connection.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    if patient is None:
        connection.close()

        return {
            "success": False,
            "message": "Patient not found."
        }

    # Check for existing active emergency access
    existing_emergency = connection.execute(
        """
        SELECT id
        FROM emergency_access
        WHERE user_id = ?
        AND patient_id = ?
        AND status = 'ACTIVE'
        LIMIT 1
        """,
        (user_id, patient_id)
    ).fetchone()

    if existing_emergency:
        connection.close()

        return {
            "success": False,
            "message": "You already have active emergency access to this patient."
        }

    # Emergency access lasts for 30 minutes
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=30)

    # Store emergency access
    connection.execute(
        """
        INSERT INTO emergency_access
        (
            user_id,
            patient_id,
            reason,
            risk_score,
            status,
            created_at,
            expires_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            patient_id,
            reason.strip(),
            90,
            "ACTIVE",
            created_at.isoformat(),
            expires_at.isoformat()
        )
    )

    connection.commit()
    connection.close()

    # Create tamper-evident audit record
    create_audit_log(
        user_id,
        "EMERGENCY_ACCESS_GRANTED",
        patient_id,
        (
            f"Emergency access granted. "
            f"Reason: {reason.strip()} | "
            f"Risk: 90 | "
            f"Expires: {expires_at.isoformat()}"
        )
    )

    # Create security alert
    create_security_alert(
        user_id,
        "EMERGENCY_ACCESS",
        "HIGH",
        (
            f"Emergency access granted for patient "
            f"{patient['patient_number']}. "
            f"Reason: {reason.strip()}"
        ),
        90
    )

    return {
        "success": True,
        "message": "Emergency access granted.",
        "expires_at": expires_at.isoformat()
    }


def check_emergency_access(user_id, patient_id):
    """
    Check whether a user's emergency access
    to a patient is still active.
    """

    connection = get_db_connection()

    emergency = connection.execute(
        """
        SELECT *
        FROM emergency_access
        WHERE user_id = ?
        AND patient_id = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, patient_id)
    ).fetchone()

    if emergency is None:
        connection.close()

        return {
            "active": False,
            "message": "No active emergency access found."
        }

    expires_at = datetime.fromisoformat(
        emergency["expires_at"]
    )

    current_time = datetime.now()

    if current_time >= expires_at:

        connection.execute(
            """
            UPDATE emergency_access
            SET status = 'EXPIRED'
            WHERE id = ?
            """,
            (emergency["id"],)
        )

        connection.commit()
        connection.close()

        create_audit_log(
            user_id,
            "EMERGENCY_ACCESS_EXPIRED",
            patient_id,
            "Emergency access expired after the permitted time."
        )

        return {
            "active": False,
            "message": "Emergency access has expired."
        }

    connection.close()

    return {
        "active": True,
        "message": "Emergency access is still active.",
        "expires_at": emergency["expires_at"]
    }


def update_expired_emergency_access():
    """
    Mark all expired emergency access records as EXPIRED.
    """

    connection = get_db_connection()

    current_time = datetime.now().isoformat()

    expired_records = connection.execute(
        """
        SELECT *
        FROM emergency_access
        WHERE status = 'ACTIVE'
        AND expires_at <= ?
        """,
        (current_time,)
    ).fetchall()

    # First update the database records
    for record in expired_records:

        connection.execute(
            """
            UPDATE emergency_access
            SET status = 'EXPIRED'
            WHERE id = ?
            """,
            (record["id"],)
        )

    connection.commit()
    connection.close()

    # Create audit logs AFTER closing the first connection
    for record in expired_records:

        create_audit_log(
            record["user_id"],
            "EMERGENCY_ACCESS_EXPIRED",
            record["patient_id"],
            "Emergency access automatically expired."
        )

    return len(expired_records)