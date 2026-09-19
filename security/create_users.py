from database.db import get_db_connection
from security.auth import hash_password


users = [
    {
        "full_name": "Dr. Aisha Bello",
        "username": "doctor1",
        "password": "Doctor123",
        "role": "Doctor",
        "department": "General Medicine",
        "ward": "Ward A"
    },
    {
        "full_name": "Mary Ibrahim",
        "username": "nurse1",
        "password": "Nurse123",
        "role": "Nurse",
        "department": "Nursing",
        "ward": "Ward A"
    },
    {
        "full_name": "John Musa",
        "username": "records1",
        "password": "Records123",
        "role": "Records Officer",
        "department": "Medical Records",
        "ward": "Records"
    },
    {
        "full_name": "Ahmed Sani",
        "username": "security1",
        "password": "Security123",
        "role": "Security Administrator",
        "department": "IT Security",
        "ward": "Administration"
    }
]


connection = get_db_connection()

for user in users:
    password_hash = hash_password(user["password"])

    try:
        connection.execute(
            """
            INSERT INTO users
            (full_name, username, password_hash, role, department, ward)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user["full_name"],
                user["username"],
                password_hash,
                user["role"],
                user["department"],
                user["ward"]
            )
        )

        print(f"Created user: {user['username']}")

    except Exception as error:
        print(f"Could not create {user['username']}: {error}")

connection.commit()
connection.close()

print("User creation completed.")