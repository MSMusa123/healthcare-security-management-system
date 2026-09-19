from database.db import get_db_connection


def detect_unusual_access(user_id):
    """
    Detect unusually high patient-record access
    by a single user.
    """

    connection = get_db_connection()

    result = connection.execute(
        """
        SELECT COUNT(*) AS access_count
        FROM audit_logs
        WHERE user_id = ?
        AND action LIKE 'PATIENT_ACCESS_%'
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    access_count = result["access_count"]

    # --------------------------------
    # Determine risk
    # --------------------------------

    if access_count <= 10:

        return {
            "anomaly": False,
            "risk_score": 10,
            "severity": "LOW",
            "message": "Normal patient record access pattern"
        }

    elif access_count <= 25:

        return {
            "anomaly": True,
            "risk_score": 50,
            "severity": "MEDIUM",
            "message": "Higher than normal patient record access"
        }

    else:

        return {
            "anomaly": True,
            "risk_score": 90,
            "severity": "HIGH",
            "message": "Unusually high patient record access detected"
        }