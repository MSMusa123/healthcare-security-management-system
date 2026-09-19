import hashlib
from datetime import datetime

from database.db import get_db_connection


def create_audit_log(user_id, action, patient_id=None, details=""):
    """
    Create a tamper-evident audit log entry.

    Each log contains the hash of the previous log,
    creating a cryptographic chain.
    """

    connection = get_db_connection()

    previous_log = connection.execute(
        """
        SELECT current_hash
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if previous_log:
        previous_hash = previous_log["current_hash"]
    else:
        previous_hash = "GENESIS"

    created_at = datetime.now().isoformat()

    log_data = (
        f"{user_id}|"
        f"{action}|"
        f"{patient_id}|"
        f"{details}|"
        f"{created_at}|"
        f"{previous_hash}"
    )

    current_hash = hashlib.sha256(
        log_data.encode("utf-8")
    ).hexdigest()

    connection.execute(
        """
        INSERT INTO audit_logs
        (
            user_id,
            action,
            patient_id,
            details,
            previous_hash,
            current_hash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            patient_id,
            details,
            previous_hash,
            current_hash,
            created_at
        )
    )

    connection.commit()
    connection.close()


def verify_audit_log_integrity():
    """
    Verify the cryptographic hash chain of all audit logs.
    """

    connection = get_db_connection()

    logs = connection.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id ASC
        """
    ).fetchall()

    connection.close()

    previous_hash = "GENESIS"

    for log in logs:

        # Check that this log points to the correct
        # previous log.
        if log["previous_hash"] != previous_hash:

            return {
                "valid": False,
                "message": (
                    f"Audit chain broken at log ID {log['id']}."
                ),
                "log_id": log["id"]
            }

        # Recreate the data that was originally hashed.
        log_data = (
            f"{log['user_id']}|"
            f"{log['action']}|"
            f"{log['patient_id']}|"
            f"{log['details']}|"
            f"{log['created_at']}|"
            f"{previous_hash}"
        )

        expected_hash = hashlib.sha256(
            log_data.encode("utf-8")
        ).hexdigest()

        # Compare the newly calculated hash with
        # the stored hash.
        if log["current_hash"] != expected_hash:

            return {
                "valid": False,
                "message": (
                    f"Audit record {log['id']} "
                    f"appears to have been modified."
                ),
                "log_id": log["id"]
            }

        previous_hash = log["current_hash"]

    return {
        "valid": True,
        "message": (
            "Audit log integrity verified. "
            "No tampering detected."
        ),
        "log_id": None
    }