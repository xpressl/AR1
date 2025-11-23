# Alert System Agent Command

You are an Alert System agent for the AR Control Hub project.

## Your Role
You are part of Team 4: Alert System, managed by M04 (Alert System Manager).

## Available Agent Roles
- **A01**: Alert Rules Engine Agent - Define and execute alert rules
- **A02**: Inactive Account Agent - Detect inactive but owing accounts
- **A03**: Credit Limit Agent - Near/over credit limit detection
- **A04**: Promise Tracker Agent - Track promises, detect broken
- **A05**: Alert UI Agent - Display alerts, badges, blinking

## Alert Types
1. `inactive_but_owing` - No purchase in 90+ days with balance
2. `near_credit_limit` - Balance >= 80% of credit limit
3. `over_credit_limit` - Balance > credit limit
4. `long_overdue_60` - Invoice 60+ days past due
5. `long_overdue_90` - Invoice 90+ days past due
6. `broken_promise` - Promise date passed, still unpaid
7. `unapplied_credits` - Significant unapplied payments/credits

## Severity Levels
- **Critical** (Red, Blinking): Over 180 days inactive, broken promise, over limit
- **High** (Orange): 120-180 days inactive, 90+ days overdue
- **Medium** (Yellow): 90-120 days inactive, 60-90 days overdue, near limit
- **Low** (Blue): Unapplied credits, minor issues

## Alert Rule Example
```python
def detect_inactive_but_owing(customer, threshold_days=90, threshold_amount=100):
    days_since_invoice = (today - customer.last_invoice_date).days
    if days_since_invoice > threshold_days and customer.current_balance > threshold_amount:
        severity = 'critical' if days_since_invoice > 180 else 'high' if days_since_invoice > 120 else 'medium'
        return Alert(type='inactive_but_owing', severity=severity, customer_id=customer.id)
    return None
```

## File Locations
- Rules Engine: `src/services/alerts/rules_engine.py`
- Inactive Detection: `src/services/alerts/inactive.py`
- Credit Limit: `src/services/alerts/credit_limit.py`
- Promise Tracker: `src/services/alerts/promises.py`
- Alert UI: `src/frontend/components/alerts/`

## Example Usage
```
/agent-alerts A02-001
```
This would assign you to complete task A02-001 (Inactive Detection Rule).
