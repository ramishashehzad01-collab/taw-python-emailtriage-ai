from fastapi import Depends, FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.database import ensure_schema, get_db
from app.models import Email
from app.schemas import DraftUpdate, EmailCreate, EmailRead
from app.services.triage import triage

ensure_schema()
app = FastAPI(title=settings.app_name, version="0.1.0", description="Human-reviewed email classification and reply drafting.", docs_url=None, redoc_url=None)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/docs", include_in_schema=False)
def api_docs():
    """Serve Swagger UI with the same visual identity as the web app."""
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.app_name} · API Reference",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='7' fill='%236e68ed'/%3E%3Cpath d='M4 7l8 6 8-6M5 5h14v14H5z' fill='none' stroke='white' stroke-width='1.7' stroke-linejoin='round'/%3E%3C/svg%3E",
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "filter": True,
        },
    )
    page = response.body.decode("utf-8")
    brand = """<header class=\"docs-header\"><div class=\"docs-nav\"><a class=\"docs-brand\" href=\"/\"><span class=\"docs-mark\" aria-hidden=\"true\">✉</span><span>EmailTriage <b>AI</b></span></a><a class=\"docs-home\" href=\"/\">← Back to app</a></div><div class=\"docs-intro\"><span class=\"docs-eyebrow\">DEVELOPER REFERENCE</span><h1>EmailTriage API</h1><p>Explore the endpoints that classify messages, prepare reply drafts, and connect your test Gmail inbox.</p><span class=\"docs-pill\"><i></i> API v0.1.0 · Human-reviewed · No automatic sending</span></div></header>"""
    page = page.replace("</head>", '<link rel="stylesheet" href="/static/docs.css"></head>', 1)
    return HTMLResponse(page.replace("<body>", f"<body>{brand}", 1))


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health", tags=["System"])
def health():
    mode = "local_fallback" if settings.ai_provider.lower() == "local" else settings.ai_provider.lower()
    return {"status": "ok", "ai_mode": mode, "gmail_enabled": settings.gmail_enabled}


@app.post("/api/emails", response_model=EmailRead, status_code=201, tags=["Email triage"])
def add_email(payload: EmailCreate, db: Session = Depends(get_db)):
    try:
        result = triage(payload.subject, payload.body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Email triage failed. Please retry or use local fallback.") from exc
    email = Email(sender=payload.sender, subject=payload.subject, body=payload.body,
                  category=result["category"], priority=result["priority"], summary=result["summary"], draft_reply=result["draft_reply"])
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@app.get("/api/emails", response_model=list[EmailRead], tags=["Email triage"])
def list_emails(category: str | None = None, db: Session = Depends(get_db)):
    query = select(Email).order_by(Email.created_at.desc())
    if category:
        query = query.where(Email.category == category)
    return list(db.scalars(query))


@app.get("/api/emails/{email_id}", response_model=EmailRead, tags=["Email triage"])
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@app.patch("/api/emails/{email_id}/draft", response_model=EmailRead, tags=["Email triage"])
def edit_draft(email_id: int, payload: DraftUpdate, db: Session = Depends(get_db)):
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.draft_reply = payload.draft_reply
    db.commit()
    db.refresh(email)
    return email


@app.post("/api/gmail/sync", response_model=list[EmailRead], tags=["Gmail"])
def gmail_sync(db: Session = Depends(get_db)):
    if not settings.gmail_enabled:
        raise HTTPException(status_code=503, detail="Gmail OAuth is disabled for this hosted demo. Use the local test setup.")
    try:
        from app.services.gmail import sync_inbox
        messages = sync_inbox(settings.max_emails_per_sync)
        created = []
        for message in messages:
            if db.scalar(select(Email).where(Email.gmail_id == message["gmail_id"])):
                continue
            result = triage(message["subject"], message["body"])
            item = Email(**message, category=result["category"], priority=result["priority"], summary=result["summary"], draft_reply=result["draft_reply"])
            db.add(item)
            created.append(item)
        db.commit()
        for item in created:
            db.refresh(item)
        return created
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Gmail sync failed. Check OAuth setup and retry.") from exc


@app.post("/api/emails/{email_id}/gmail-draft", tags=["Gmail"])
def save_gmail_draft(email_id: int, db: Session = Depends(get_db)):
    if not settings.gmail_enabled:
        raise HTTPException(status_code=503, detail="Gmail OAuth is disabled for this hosted demo. Use the local test setup.")
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.gmail_draft_id:
        try:
            from app.services.gmail import update_gmail_draft
            update_gmail_draft(email.gmail_draft_id,
                               {"sender": email.sender, "subject": email.subject,
                                "thread_id": email.thread_id,
                                "original_message_id": email.original_message_id}, email.draft_reply)
            return {"status": "draft_saved", "gmail_draft_id": email.gmail_draft_id,
                    "message": "Updated the existing Gmail draft; nothing was sent."}
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Could not update the Gmail draft. Check OAuth access and retry.") from exc
    if email.status == "draft_saved":
        return {"status": "draft_saved", "gmail_draft_id": None,
                "message": "This email was previously saved to Gmail Drafts. Check Drafts before saving again; no extra copy was created."}
    try:
        from app.services.gmail import create_gmail_draft
        draft_id = create_gmail_draft({"sender": email.sender, "subject": email.subject,
                                       "thread_id": email.thread_id,
                                       "original_message_id": email.original_message_id}, email.draft_reply)
        email.gmail_draft_id = draft_id
        email.status = "draft_saved"
        db.commit()
        return {"status": "draft_saved", "gmail_draft_id": draft_id, "message": "Saved to Gmail Drafts; nothing was sent."}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Could not save Gmail draft. Check OAuth access and retry.") from exc
