from app.database import Base, SessionLocal, engine
from app.models import Email
from app.services.triage import triage

SAMPLES = [
    ("customer@example.test", "Invoice question", "Hello, I was charged twice for my monthly plan. Could you check the duplicate payment?"),
    ("partner@example.test", "Can we schedule a call?", "Are you available for a 30 minute meeting next Tuesday to discuss the proposal?"),
    ("user@example.test", "Urgent: login error", "Our team cannot log in and this is blocking work. Please help ASAP."),
]

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    if db.query(Email).count() == 0:
        for sender, subject, body in SAMPLES:
            result = triage(subject, body)
            db.add(Email(sender=sender, subject=subject, body=body, **result))
        db.commit()
print("Sample inbox loaded. Open http://127.0.0.1:8000/docs")
