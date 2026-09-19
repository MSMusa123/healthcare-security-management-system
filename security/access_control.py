def check_patient_access(user, patient):
    """
    Decide whether a user should be allowed
    to access a patient's record.
    """

    role = user["role"]
    user_ward = user["ward"]

    patient_ward = patient["ward"]
    assigned_doctor_id = patient["assigned_doctor_id"]

    user_id = user["id"]


    # Security Administrator can access records
    # for security and monitoring purposes.
    if role == "Security Administrator":
        return {
            "decision": "ALLOW",
            "reason": "Security Administrator access"
        }


    # Doctor assigned to the patient
    if role == "Doctor" and assigned_doctor_id == user_id:
        return {
            "decision": "ALLOW",
            "reason": "Doctor is assigned to this patient"
        }


    # User and patient are in the same ward
    if user_ward == patient_ward:
        return {
            "decision": "RESTRICT",
            "reason": "User is in the patient's ward but is not the assigned doctor"
        }


    # Different ward
    return {
        "decision": "BLOCK",
        "reason": "Patient is outside the user's assigned ward"
    }