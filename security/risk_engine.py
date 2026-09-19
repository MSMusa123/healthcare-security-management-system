def calculate_risk_score(user, patient, decision):
    """
    Calculate a risk score between 0 and 100
    for a patient record access attempt.
    """

    score = 0
    reasons = []

    role = user["role"]
    user_ward = user["ward"]
    patient_ward = patient["ward"]
    assigned_doctor_id = patient["assigned_doctor_id"]
    user_id = user["id"]

    # --------------------------------
    # 1. Security Administrator
    # --------------------------------

    if role == "Security Administrator":
        score += 5
        reasons.append("Security Administrator access")

    # --------------------------------
    # 2. Assigned Doctor
    # --------------------------------

    elif role == "Doctor" and assigned_doctor_id == user_id:
        score += 5
        reasons.append("Doctor is assigned to the patient")

    # --------------------------------
    # 3. Same Ward
    # --------------------------------

    elif user_ward == patient_ward:
        score += 30
        reasons.append("User and patient are in the same ward")

    # --------------------------------
    # 4. Different Ward
    # --------------------------------

    else:
        score += 60
        reasons.append("Patient is outside user's assigned ward")

    # --------------------------------
    # 5. Access Decision
    # --------------------------------

    if decision["decision"] == "BLOCK":
        score += 30
        reasons.append("Access was blocked by security policy")

    elif decision["decision"] == "RESTRICT":
        score += 15
        reasons.append("Access was restricted by security policy")

    # --------------------------------
    # Maximum score
    # --------------------------------

    if score > 100:
        score = 100

    # --------------------------------
    # Risk level
    # --------------------------------

    if score <= 30:
        level = "LOW"

    elif score <= 70:
        level = "MEDIUM"

    else:
        level = "HIGH"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }