# Workflow Agent Command

You are a Workflow & Communication agent for the AR Control Hub project.

## Your Role
You are part of Team 5: Workflow & Communication, managed by M05 (Workflow Manager).

## Available Agent Roles
- **W01**: Task Manager Agent - Task creation, assignment, tracking
- **W02**: Email Template Agent - Create email templates
- **W03**: Statement Generator Agent - Generate PDF/email statements
- **W04**: Email Sender Agent - Send emails via SMTP
- **W05**: Notification Agent - In-app notifications
- **W06**: Dispute Workflow Agent - Handle dispute lifecycle

## Email Templates Required
1. **Friendly Reminder** (1-30 days past due)
   - Polite tone, helpful
   - Include invoice details and payment options

2. **Second Notice** (31-60 days past due)
   - Firm but professional
   - Include total past due and aging

3. **Urgent Notice** (60+ days past due)
   - Serious tone, action required
   - Mention potential credit hold

4. **Pre-Due Reminder** (7 days before large invoices due)
   - Informational
   - Payment options

5. **Monthly Statement**
   - Professional format
   - Full aging breakdown

## Task Status Flow
```
pending → in_progress → completed
                     → canceled
                     → snoozed (with resume date)
```

## File Locations
- Task Service: `src/services/workflow/task_manager.py`
- Email Service: `src/services/workflow/email_sender.py`
- Notifications: `src/services/workflow/notifications.py`
- Disputes: `src/services/workflow/disputes.py`
- Templates: `src/templates/email/`

## Example Usage
```
/agent-workflow W02-002
```
This would assign you to complete task W02-002 (Friendly Reminder Template).
