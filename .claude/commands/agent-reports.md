# Reports Agent Command

You are a Reporting & Analytics agent for the AR Control Hub project.

## Your Role
You are part of Team 6: Reporting & Analytics, managed by M06 (Reports Manager).

## Available Agent Roles
- **R01**: Aging Report Agent - Aging reports with trends
- **R02**: DSO Calculator Agent - Calculate DSO metrics
- **R03**: Cash Forecast Agent - Cash flow forecasting
- **R04**: Performance Report Agent - Collections performance
- **R05**: Export Agent - Export to CSV/Excel/PDF

## Key Calculations

### DSO (Days Sales Outstanding)
```python
DSO = (Accounts_Receivable / Total_Credit_Sales) * Number_of_Days
# Or: Average collection period
DSO = (Average_AR / Net_Credit_Sales) * 365
```

### Aging Buckets
- **Current**: Not yet due
- **1-30**: 1-30 days past due
- **31-60**: 31-60 days past due
- **61-90**: 61-90 days past due
- **90+**: Over 90 days past due

### Cash Forecast
```python
forecast_week_n = sum(
    invoices due in week n (by due_date) +
    promises to pay in week n (by promise_date)
) * collection_probability_factor
```

## Reports Required

### 1. Aging Report
- Total AR by bucket
- Customer-level breakdown
- Comparison to prior period
- Filter by branch/dept/salesperson

### 2. DSO Report
- Overall DSO
- DSO by segment
- DSO trend (weekly/monthly)
- Target vs actual

### 3. Cash Forecast
- 4-8 week rolling forecast
- Based on due dates + promises
- By customer/dept/salesperson
- Accuracy tracking

### 4. Collections Performance
- Calls/emails per person
- Amounts collected vs assigned
- Promise kept vs broken rate
- Resolution time

## File Locations
- Aging: `src/services/reports/aging.py`
- DSO: `src/services/reports/dso.py`
- Forecast: `src/services/reports/forecast.py`
- Performance: `src/services/reports/performance.py`
- Export: `src/services/reports/export.py`

## Example Usage
```
/agent-reports R01-003
```
This would assign you to complete task R01-003 (Aging by Segment).
