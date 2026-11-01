import base64
from email.message import EmailMessage
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import settings


def _service():
    token_path = Path(settings.google_token_file)
    creds = Credentials.from_authorized_user_file(str(token_path), settings.gmail_scopes.split()) if token_path.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        secret = Path(settings.google_client_secret_file)
        if not secret.exists():
            raise FileNotFoundError("Google OAuth client file not found. See README setup instructions.")
        flow = InstalledAppFlow.from_client_secrets_file(str(secret), settings.gmail_scopes.split())
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")


def _plain_text(payload: dict) -> str:
    body = payload.get("body", {}).get("data")
    if payload.get("mimeType") == "text/plain" and body:
        return _decode(body)
    for part in payload.get("parts", []):
        text = _plain_text(part)
        if text:
            return text
    return ""


def sync_inbox(limit: int) -> list[dict]:
    service = _service()
    # Keep the demo restricted to messages explicitly labeled for testing.
    # Create this label in Gmail and apply it only to fake/test emails.
    listed = service.users().messages().list(userId="me", q="label:EmailTriage-Test", maxResults=limit).execute(num_retries=2)
    items = []
    for ref in listed.get("messages", []):
        msg = service.users().messages().get(userId="me", id=ref["id"], format="full").execute(num_retries=2)
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        payload = msg.get("payload", {})
        body = _plain_text(payload)
        items.append({"gmail_id": msg["id"], "thread_id": msg.get("threadId"),
                      "original_message_id": headers.get("message-id"),
                      "sender": headers.get("from", "unknown"),
                      "subject": headers.get("subject", "(no subject)"), "body": body or "(No plain text body available.)"})
    return items


def _draft_message(email: dict, reply: str) -> dict:
    message = EmailMessage()
    message["To"] = email["sender"]
    message["Subject"] = email["subject"] if email["subject"].lower().startswith("re:") else f"Re: {email['subject']}"
    if email.get("original_message_id"):
        message["In-Reply-To"] = email["original_message_id"]
        message["References"] = email["original_message_id"]
    message.set_content(reply)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    return {"message": {"raw": raw, "threadId": email.get("thread_id")}}


def create_gmail_draft(email: dict, reply: str) -> str:
    result = _service().users().drafts().create(userId="me", body=_draft_message(email, reply)).execute(num_retries=2)
    return result["id"]


def update_gmail_draft(draft_id: str, email: dict, reply: str) -> str:
    result = _service().users().drafts().update(userId="me", id=draft_id,
                                                body=_draft_message(email, reply)).execute(num_retries=2)
    return result["id"]
