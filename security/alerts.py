from database.db import get_db_connection


def create_security_alert(
    user_id,
    alert_type,
    severity,
    description,
    risk_score
):
    connection = get_db_connection()

    # Check whether an open alert of this type
    # already exists for this user
    existing_alert = connection.execute(
        """
        SELECT id
        FROM security_alerts
        WHERE user_id = ?
        AND alert_type = ?
        AND status = 'open'
        LIMIT 1
        """,
        (
            user_id,
            alert_type
        )
    ).fetchone()

    # Do not create a duplicate alert
    if existing_alert:
        connection.close()
        return False

    # Create a new alert
    connection.execute(
        """
        INSERT INTO security_alerts
        (
            user_id,
            alert_type,
            severity,
            description,
            risk_score
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            alert_type,
            severity,
            description,
            risk_score
        )
    )

    connection.commit()
    connection.close()

    return True