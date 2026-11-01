# EmailTriage AI Demo Script (60–90 seconds)

Record the local app using its built-in fake sample email. Keep the **Synthetic samples** filter selected. Do not show Gmail, personal addresses, API keys, `.env`, OAuth files, or real messages. The app sends email text to the configured AI provider for classification and reply drafting, so use only sample content.

## Recording flow

**0–12 seconds — Welcome screen**

Show the welcome screen and click **Open your workspace**.

“Hi, I’m Ramisha. This is EmailTriage AI. It helps sort incoming messages, summarize them, and prepare reply drafts for a person to review.”

**12–25 seconds — Inbox overview and sample**

Show the overview cards and the pre-filled fake invoice email. Click **Triage this email**.

“I’m using a sample email only. The overview shows the inbox totals, urgent items, and saved drafts for the selected filter.”

**25–50 seconds — Classification and draft**

Show the new inbox card and point out its category, priority, summary, and editable reply draft. Optionally edit a few words and click **Save edited draft**.

“The app classifies the message, summarizes the issue, and suggests a reply. A person can review and change the draft before saving it.”

**50–72 seconds — Save a Gmail draft**

On the fake sample card, click **Save to Gmail Drafts** and show the success message. Keep Gmail off-screen.

“I can save this reviewed sample as a Gmail draft. It stays in Drafts; the app does not send email automatically.”

**72–85 seconds — Close**

Show the inbox overview or API reference link briefly, then return to the app.

“The project includes a FastAPI API, PostgreSQL storage, Groq-based triage, and Gmail draft support. Thank you for watching.”

## Recording checklist

- Keep the recording between 60 and 90 seconds.
- The screen recording can be silent, but a short narration makes the demo clearer.
- Use the app's built-in `example.test` sample only; do not type or paste a real email.
- Do not open Gmail or show personal account details during the recording.
- Do not click **Send**. The demo should show the draft workflow only.
