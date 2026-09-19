from datetime import datetime

from database.db import get_db_connection
from security.audit_log import create_audit_log


def create_offline_emergency_access(user_id, patient_id, reason):
    """
    Record emergency access that occurred while the
    main HSMS system was unavailable.
    """

    if not reason or not reason.strip():
        return {
            "success": False,
            "message": "Emergency reason is required."
        }

    if len(reason.strip()) < 15:
        return {
            "success": False,
            "message": "Emergency reason must contain at least 15 characters."
        }

    connection = get_db_connection()

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

    created_at = datetime.now().isoformat()

    connection.execute(
        """
        INSERT INTO offline_emergency_access
        (
            user_id,
            patient_id,
            reason,
            access_type,
            synced,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            patient_id,
            reason.strip(),
            "OFFLINE_EMERGENCY",
            0,
            created_at
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Offline emergency access recorded.",
        "created_at": created_at
    }


def get_unsynced_offline_access():
    """
    Return offline emergency events that have not
    yet been synchronized.
    """

    connection = get_db_connection()

    records = connection.execute(
        """
        SELECT
            offline_emergency_access.*,
            users.full_name AS user_name,
            patients.patient_number,
            patients.full_name AS patient_name
        FROM offline_emergency_access
        LEFT JOIN users
            ON offline_emergency_access.user_id = users.id
        LEFT JOIN patients
            ON offline_emergency_access.patient_id = patients.id
        WHERE offline_emergency_access.synced = 0
        ORDER BY offline_emergency_access.id ASC
        """
    ).fetchall()

    connection.close()

    return records


def synchronize_offline_access():
    """
    Synchronize offline emergency events with the
    tamper-evident audit log.
    """

    connection = get_db_connection()

    records = connection.execute(
        """
        SELECT *
        FROM offline_emergency_access
        WHERE synced = 0
        ORDER BY id ASC
        """
    ).fetchall()

    connection.close()

    synchronized = 0

    # Create audit records after the first database
    # connection has been closed.
    for record in records:

        create_audit_log(
            record["user_id"],
            "OFFLINE_EMERGENCY_ACCESS",
            record["patient_id"],
            (
                f"Offline emergency access synchronized. "
                f"Reason: {record['reason']} | "
                f"Original time: {record['created_at']}"
            )
        )

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE offline_emergency_access
            SET synced = 1
            WHERE id = ?
            """,
            (record["id"],)
        )

        connection.commit()
        connection.close()

        synchronized += 1

    return synchronized