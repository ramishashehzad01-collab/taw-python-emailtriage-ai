# EmailTriage AI — Testing Checklist

## 1. Core Application
- [ ] Health endpoint returns HTTP 200.
- [ ] Empty email body is rejected with HTTP 422.
- [ ] Billing email is classified correctly.
- [ ] Email is saved in the database.
- [ ] Emails appear in the inbox.
- [ ] Generate an email summary.
- [ ] Draft replies can be edited and updated.
- [ ] Unknown email IDs return HTTP 404.

## 2. Email Classification
- [ ] Import test emails successfully.
- [ ] Classify emails into the correct categories.
- [ ] Handle empty or invalid email content.

## 3. Reply Draft Generation
- [ ] Generate a relevant reply draft.
- [ ] Allow users to edit the generated draft.
- [ ] Save the draft successfully.

## 4. Gmail Integration
- [ ] Connect Gmail using valid credentials.
- [ ] Import only emails with the `EmailTriage-Test` label.
- [ ] Labeled test emails are imported successfully.
- [ ] Save generated replies as Gmail drafts.
- [ ] Confirm that no emails are sent automatically.

## 5. Error Handling
- [ ] Handle AI API failures.
- [ ] Handle Gmail API errors.
- [ ] Handle database connection errors.
- [ ] Display useful error messages.

## 6. Final Checks
- [ ] Verify the main application flow.
- [ ] Check that environment variables are configured.
- [ ] Confirm that no real API keys or secrets are committed.