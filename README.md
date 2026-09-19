# Healthcare Security Management System (HSMS)

## ICSC 2026 University Hackathon — Track C1

### Healthcare Security Management System

HSMS is a functional prototype designed to improve the security and accountability of electronic healthcare records.

The system uses context-aware access control to determine whether access to a patient record is appropriate based on factors such as the user's role, assigned ward, patient relationship and security context.

---

## 1. Problem

Healthcare institutions are increasingly moving from paper-based records to digital systems. However, healthcare records contain highly sensitive information and can be exposed through excessive permissions, shared accounts, inappropriate access and weak auditing.

HSMS addresses the challenge of providing healthcare workers with necessary access while making inappropriate access detectable and accountable.

---

## 2. Proposed Solution

HSMS introduces a context-aware healthcare security layer.

Instead of relying only on:

"Is this user authorized?"

the system considers:

"Is this access appropriate in the current context?"

Access decisions consider:

- User role
- Assigned ward
- Patient relationship
- Security risk
- Previous access behaviour
- Emergency circumstances

---

## 3. Key Features

### Context-Aware Access Control

Patient access is evaluated using the user's role, ward and relationship with the patient.

### Risk Scoring

Each access decision receives a risk score and security level.

Risk levels include:

- LOW
- MEDIUM
- HIGH

### Emergency Break-Glass Access

Authorized healthcare personnel can request emergency access when normal access restrictions prevent immediate patient care.

Emergency access:

- Requires a reason
- Is time-limited
- Receives a high risk score
- Creates an audit record
- Generates a security alert

### Behaviour Anomaly Detection

HSMS monitors patient-record access activity and detects unusually high access patterns using rule-based behavioural analysis.

### Tamper-Evident Audit Logs

Security events are stored using SHA-256 hash chaining.

Each audit record is linked to the previous record, allowing the system to detect modifications to the audit chain.

### Offline Emergency Mode

The prototype provides an offline emergency mechanism for recording emergency access when normal network connectivity is unavailable.

Offline events can later be synchronized into the main audit system.

### Security Dashboard

Security administrators can monitor:

- Users
- Patients
- Security alerts
- Emergency access
- Audit events
- Offline events
- High-risk activity

---

## 4. System Architecture

The system follows this security flow:

User
↓
Authentication
↓
Context-Aware Access Engine
↓
Risk & Security Engine
↓
Access Decision
↓
Audit Logging
↓
Security Monitoring

Possible decisions include:

- ALLOW
- RESTRICT
- BLOCK
- EMERGENCY_ALLOW

---

## 5. Technology Stack

Frontend:
- HTML
- CSS
- JavaScript

Backend:
- Python
- Flask

Database:
- SQLite

Security:
- Werkzeug password hashing
- SHA-256 hash chaining
- Flask sessions
- Rule-based behavioural anomaly detection

---

## 6. Project Structure

HSMS/

├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── db.py
│   ├── schema.sql
│   └── hsms.db
│
├── security/
│   ├── auth.py
│   ├── access_control.py
│   ├── risk_engine.py
│   ├── emergency.py
│   ├── anomaly_detector.py
│   ├── alerts.py
│   ├── audit_log.py
│   └── offline_mode.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── patient.html
│   ├── emergency.html
│   ├── alerts.html
│   └── ...
│
└── static/
    └── css/
        └── style.css

---

## 7. Running the Prototype

### 1. Create a virtual environment

Windows:

python -m venv venv

### 2. Activate the environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1

### 3. Install dependencies

pip install -r requirements.txt

### 4. Start the application

python app.py

### 5. Open the application

http://127.0.0.1:5000

---

## 8. Demonstration Accounts

### Doctor

Username:
doctor1

Password:
Doctor123

Role:
Doctor

Ward:
Ward A

---

### Nurse

Username:
nurse1

Password:
Nurse123

Role:
Nurse

Ward:
Ward A

---

### Records Officer

Username:
records1

Password:
Records123

Role:
Records Officer

---

### Security Administrator

Username:
security1

Password:
Security123

Role:
Security Administrator

---

## 9. Demonstration Flow

The recommended demonstration sequence is:

1. Login
2. Open Dashboard
3. Access an authorized patient record
4. Attempt restricted/blocked access
5. Request emergency access
6. Open Security Alerts
7. View Audit Logs
8. Verify Audit Integrity
9. Demonstrate Offline Emergency Mode
10. Open Security Dashboard

---

## 10. Data and Privacy

HSMS is a hackathon prototype.

The system uses synthetic patient information for demonstration purposes.

No real patient information should be entered into the prototype.

---

## 11. Limitations

HSMS is a functional prototype and is not a production hospital information system.

The current anomaly detection mechanism uses rule-based behavioural analysis rather than advanced machine learning.

The system has not been deployed in a real hospital environment.

The offline mode is a prototype mechanism for recording and synchronizing emergency events.

---

## 12. Future Improvements

Future versions could include:

- Advanced machine-learning anomaly detection
- Multi-factor authentication
- Stronger identity management
- Hospital-wide deployment
- More detailed duty and shift scheduling
- Encryption of sensitive database fields
- Distributed tamper-evident audit storage
- More sophisticated offline synchronization
- Integration with existing hospital information systems

---

## 13. Conclusion

HSMS demonstrates how healthcare record security can move beyond simple role-based permissions toward context-aware and accountable access.

The system allows legitimate access, restricts inappropriate access, supports emergency situations, detects unusual behaviour, records security events and provides tamper-evident auditing.

The goal is not to make patient records inaccessible.

The goal is to make access:

**Appropriate. Accountable. Detectable.**

---

## ICSC 2026 University Hackathon

Track:
C1 — Health & Medical Systems

Project:
Healthcare Security Management System (HSMS)

Team:
[Tob Brainers]

Source Code:
[ADD GITHUB LINK]