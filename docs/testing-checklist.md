# EmailTriage AI - Testing Checklist

## Core Application
- [ ] Health endpoint returns HTTP 200.
- [ ] Empty email body is rejected with HTTP 422.
- [ ] Billing email is classified correctly.
- [ ] Email is saved in the database.
- [ ] Emails appear in the inbox.
- [ ] Draft replies can be edited and updated.
- [ ] Unknown email IDs return HTTP 404.

## Gmail Integration
- [ ] Labeled test emails are imported successfully.
- [ ] Reply drafts are saved in Gmail Drafts.
- [ ] Saving an edited draft updates the existing draft.
- [ ] Repeated sync does not create duplicate emails.
- [ ] No email is sent automatically.

## Error Handling
- [ ] Invalid OAuth configuration returns a safe error.
- [ ] Invalid API configuration returns a retry-friendly error.
