# EmailTriage AI — Testing Checklist

## 1. Email Classification
- [ ] Import test emails successfully.
- [ ] Classify emails into the correct categories.
- [ ] Generate an email summary.
- [ ] Handle empty or invalid email content.

## 2. Reply Draft Generation
- [ ] Generate a relevant reply draft.
- [ ] Allow users to edit the generated draft.
- [ ] Save the draft successfully.

## 3. Gmail Integration
- [ ] Connect Gmail using valid credentials.
- [ ] Import only emails with the `EmailTriage-Test` label.
- [ ] Save generated replies as Gmail drafts.
- [ ] Confirm that no emails are sent automatically.

## 4. Error Handling
- [ ] Handle AI API failures.
- [ ] Handle Gmail API errors.
- [ ] Handle database connection errors.
- [ ] Display useful error messages.

## 5. Final Checks
- [ ] Verify the main application flow.
- [ ] Check that environment variables are configured.
- [ ] Confirm that no real API keys or secrets are committed.
