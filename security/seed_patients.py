from database.db import get_db_connection


patients = [
    {
        "patient_number": "P001",
        "full_name": "Ibrahim Yusuf",
        "date_of_birth": "1998-04-15",
        "blood_group": "O+",
        "allergies": "Penicillin",
        "medical_conditions": "Hypertension",
        "medication": "Amlodipine",
        "ward": "Ward A",
        "assigned_doctor_id": 1
    },

    {
        "patient_number": "P002",
        "full_name": "Fatima Abdullahi",
        "date_of_birth": "2001-08-22",
        "blood_group": "A+",
        "allergies": "None",
        "medical_conditions": "Asthma",
        "medication": "Salbutamol",
        "ward": "Ward A",
        "assigned_doctor_id": 1
    },

    {
        "patient_number": "P003",
        "full_name": "Musa Bello",
        "date_of_birth": "1987-02-10",
        "blood_group": "B+",
        "allergies": "Aspirin",
        "medical_conditions": "Diabetes",
        "medication": "Metformin",
        "ward": "Ward B",
        "assigned_doctor_id": None
    },

    {
        "patient_number": "P004",
        "full_name": "Amina Sani",
        "date_of_birth": "1995-11-03",
        "blood_group": "AB+",
        "allergies": "None",
        "medical_conditions": "Migraine",
        "medication": "Paracetamol",
        "ward": "Ward B",
        "assigned_doctor_id": None
    }
]


connection = get_db_connection()


for patient in patients:

    try:

        connection.execute(
            """
            INSERT INTO patients
            (
                patient_number,
                full_name,
                date_of_birth,
                blood_group,
                allergies,
                medical_conditions,
                medication,
                ward,
                assigned_doctor_id
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                patient["patient_number"],
                patient["full_name"],
                patient["date_of_birth"],
                patient["blood_group"],
                patient["allergies"],
                patient["medical_conditions"],
                patient["medication"],
                patient["ward"],
                patient["assigned_doctor_id"]
            )
        )

        print(f"Created patient: {patient['patient_number']}")

    except Exception as error:

        print(
            f"Could not create "
            f"{patient['patient_number']}: {error}"
        )


connection.commit()
connection.close()

print("Patient creation completed.")