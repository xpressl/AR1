# AR Control Hub - User Acceptance Testing (UAT) Scenarios

**UAT Period:** Weeks 3-4 after demo
**Participants:** AR Team members (Sarah Martinez, etc.)
**Environment:** UAT Database with 100 customers
**Duration:** 10 business days

---

## UAT Objectives

✅ Validate system meets business requirements
✅ Ensure workflows match current processes
✅ Identify any bugs or usability issues
✅ Confirm data accuracy and integrity
✅ Verify performance with realistic data volumes
✅ Build user confidence before go-live

---

## UAT Environment Setup

### Prepare UAT Environment

```bash
# Generate UAT data (100 customers, more realistic volume)
python scripts/seed_demo_data.py --scenario uat

# Create UAT-specific database
export DATABASE_URL="postgresql+asyncpg://ar_user:ar_dev_password@localhost:5432/ar_uat"

# Users can log in with:
# - Their actual email addresses
# - Temporary password: UAT2025!
```

### UAT Data Characteristics
- 100 customers (realistic distribution)
- 600 invoices ($3M+ AR)
- 300 payments
- Mix of current, overdue, and problem accounts
- Various alert types and severities
- Incomplete tasks and broken promises

---

## Test Scenario 1: Daily Morning Routine (AR Specialist)

**User:** Sarah Martinez (AR Specialist)
**Duration:** 30 minutes
**Objective:** Complete typical morning workflow

### Steps:

1. **Login and Dashboard Review**
   - [ ] Log in successfully
   - [ ] Dashboard loads within 3 seconds
   - [ ] Total AR balance displayed correctly
   - [ ] Aging breakdown shows Current, 30, 60, 90+ buckets
   - [ ] DSO value reasonable (30-45 days range)
   - [ ] Active alerts count displayed

**Expected Result:** Dashboard provides clear AR health snapshot

2. **Review Prioritized Worklist**
   - [ ] Worklist displays with priority scores
   - [ ] Sort by priority (highest first)
   - [ ] Critical alerts have blinking animation
   - [ ] Can filter by aging bucket
   - [ ] Can search for specific customer

**Expected Result:** Top 10 priority accounts clearly identified

3. **Work Top Priority Account**
   - [ ] Click on #1 priority customer
   - [ ] Customer 360 view loads completely
   - [ ] All sections visible (invoices, notes, alerts, tasks)
   - [ ] Invoice aging displayed correctly
   - [ ] Alert description clear and actionable

**Expected Result:** Complete customer information available

4. **Document Collection Call**
   - [ ] Click "Add Note" button
   - [ ] Select "Phone Call" note type
   - [ ] Enter content: "Spoke with AP manager, will send check by Friday"
   - [ ] Save note successfully
   - [ ] Note appears in customer timeline

**Expected Result:** Note saved and visible immediately

5. **Log Payment Promise**
   - [ ] Click "Add Note" again
   - [ ] Select "Promise to Pay" type
   - [ ] Set promise date (next Friday)
   - [ ] Set promise amount ($5,000)
   - [ ] Save promise
   - [ ] Promise tracked in system

**Expected Result:** Promise logged and will be monitored

6. **Send Payment Reminder**
   - [ ] Click "Send Email" button
   - [ ] Select "Payment Reminder" template
   - [ ] Review auto-populated fields (correct customer, balance)
   - [ ] Preview email looks professional
   - [ ] Send email (or save draft)
   - [ ] Email logged in customer history

**Expected Result:** Email sent successfully and logged

7. **Create Follow-Up Task**
   - [ ] Click "Create Task" button
   - [ ] Enter title: "Follow up if payment not received"
   - [ ] Set due date (next Monday)
   - [ ] Set priority: High
   - [ ] Assign to self
   - [ ] Save task
   - [ ] Task appears on dashboard

**Expected Result:** Task created and visible

8. **Complete Task from Yesterday**
   - [ ] Go to "My Tasks" view
   - [ ] Find task due today
   - [ ] Mark as "Completed"
   - [ ] Task moves to completed section
   - [ ] Task count on dashboard decreases

**Expected Result:** Task completion tracked correctly

### Success Criteria
- ✅ All steps completed without errors
- ✅ Workflow feels natural and efficient
- ✅ Time to complete: < 10 minutes per account
- ✅ Data accuracy: 100%
- ✅ User satisfaction: 4+/5

---

## Test Scenario 2: Promise Tracking & Broken Promises (AR Specialist)

**User:** Sarah Martinez
**Duration:** 15 minutes
**Objective:** Verify promise tracking works correctly

### Setup:
Create 3 promises with different statuses:
1. Promise due today (pending)
2. Promise from last week (should be marked broken if not paid)
3. Promise from last month that was kept (paid)

### Steps:

1. **Review Promises Dashboard**
   - [ ] Navigate to Promises page
   - [ ] See pending promises count
   - [ ] See overdue promises count (blinking if > 0)
   - [ ] See kept promises count
   - [ ] Promise keeping rate percentage displayed

**Expected Result:** Clear view of all promise statuses

2. **Check Promise Due Today**
   - [ ] Find promise due today
   - [ ] Status shows "Pending"
   - [ ] Due date highlighted (due today)
   - [ ] Can click to view customer detail

**Expected Result:** Today's promises easily identifiable

3. **Handle Broken Promise**
   - [ ] Filter for "Overdue" promises
   - [ ] See promises past due date (3+ days)
   - [ ] System automatically marked as "Broken"
   - [ ] Alert generated for broken promise
   - [ ] Can add note explaining why broken

**Expected Result:** Broken promises flagged automatically

4. **Mark Promise as Kept**
   - [ ] Find promise that customer paid
   - [ ] Click "Mark as Kept"
   - [ ] Status changes to "Kept"
   - [ ] Promise keeping rate updates
   - [ ] Customer gets credit for keeping promise

**Expected Result:** Promise status updated correctly

5. **Review Promise Performance**
   - [ ] Navigate to Promise Performance report
   - [ ] See breakdown by salesperson
   - [ ] See overall promise keeping rate
   - [ ] Identify salespeople with low rates

**Expected Result:** Performance metrics accurate

### Success Criteria
- ✅ Promises tracked automatically
- ✅ Broken promises detected (3+ days overdue)
- ✅ Manual status updates work
- ✅ Performance metrics accurate
- ✅ Alerts generated for broken promises

---

## Test Scenario 3: Cash Flow Forecasting (AR Manager)

**User:** Michael Chen (AR Manager)
**Duration:** 20 minutes
**Objective:** Use forecasting for monthly planning

### Steps:

1. **Access Cash Flow Forecast**
   - [ ] Navigate to Analytics > Cash Flow Forecast
   - [ ] 8-week forecast displays
   - [ ] Weekly breakdown visible
   - [ ] Total forecast amount shown

**Expected Result:** Forecast loads and displays correctly

2. **Analyze Weekly Forecast**
   - [ ] Review Week 1 projected collections
   - [ ] See breakdown (invoice-based vs promise-based)
   - [ ] Identify low collection weeks (< $50k)
   - [ ] Note which weeks need attention

**Expected Result:** Clear view of upcoming 8 weeks

3. **Toggle Promise Inclusion**
   - [ ] Turn OFF promise-based forecast
   - [ ] See invoice-only forecast
   - [ ] Turn ON promise-based forecast
   - [ ] See combined forecast (higher)
   - [ ] Understand impact of promises

**Expected Result:** Can compare scenarios easily

4. **Change Forecast Period**
   - [ ] Change from 8 weeks to 12 weeks
   - [ ] Forecast extends to 12 weeks
   - [ ] Change back to 8 weeks
   - [ ] Forecast returns to 8 weeks

**Expected Result:** Flexible forecast periods

5. **Review Forecast Accuracy**
   - [ ] Navigate to Forecast Accuracy view
   - [ ] See historical accuracy percentage
   - [ ] Review variance by week
   - [ ] Note trend (improving or declining)

**Expected Result:** Accuracy tracking visible

6. **Export Forecast Data**
   - [ ] Click "Export to CSV"
   - [ ] File downloads successfully
   - [ ] Open in Excel
   - [ ] Data formatted correctly
   - [ ] Can create charts from data

**Expected Result:** Export works for leadership reporting

### Success Criteria
- ✅ Forecast calculations accurate
- ✅ Scenarios (with/without promises) clear
- ✅ Historical accuracy tracked
- ✅ Export functionality works
- ✅ Useful for management planning

---

## Test Scenario 4: DSO Analysis & Problem Accounts (AR Manager)

**User:** Michael Chen
**Duration:** 20 minutes
**Objective:** Identify and address DSO issues

### Steps:

1. **Review Current DSO**
   - [ ] Navigate to Analytics > DSO Analysis
   - [ ] See current DSO (30/60/90 day basis)
   - [ ] Compare to target (35 days)
   - [ ] Understand if above or below target

**Expected Result:** Current DSO clearly displayed

2. **Analyze DSO Trend**
   - [ ] Review 6-month DSO trend chart
   - [ ] Identify trend (improving/declining)
   - [ ] Note specific months above target (red bars)
   - [ ] Note specific months on target (green bars)

**Expected Result:** Visual trend easy to interpret

3. **Identify Problem Accounts**
   - [ ] Click "Problem Accounts" tab
   - [ ] See customers with DSO 50%+ above average
   - [ ] Sort by DSO (highest first)
   - [ ] Note top 5 problem accounts

**Expected Result:** Problem accounts clearly identified

4. **Drill into Problem Customer**
   - [ ] Click on top problem account
   - [ ] See customer DSO (e.g., 72 days)
   - [ ] See company average (e.g., 38 days)
   - [ ] See variance (e.g., 89% above average)
   - [ ] Review customer invoices and aging

**Expected Result:** Root cause visible

5. **Create Action Plan**
   - [ ] From problem account view, create task
   - [ ] Title: "Address high DSO with [Customer]"
   - [ ] Assign to AR specialist
   - [ ] Set priority: High
   - [ ] Due date: This week

**Expected Result:** Action taken on problem accounts

6. **Review DSO by Segment**
   - [ ] Click "By Salesperson" view
   - [ ] See DSO breakdown by each salesperson
   - [ ] Identify salesperson with highest DSO
   - [ ] Compare to company average

**Expected Result:** Segment analysis reveals patterns

### Success Criteria
- ✅ DSO calculated correctly (Countback Method)
- ✅ Trend analysis intuitive
- ✅ Problem accounts easily identified
- ✅ Can drill down to customer level
- ✅ Actionable insights for improvement

---

## Test Scenario 5: Salesperson Portal (Sales Team)

**User:** Jessica Williams (Salesperson SP001)
**Duration:** 10 minutes
**Objective:** Monitor assigned customers independently

### Steps:

1. **Login to Salesperson Portal**
   - [ ] Navigate to salesperson portal URL
   - [ ] Authenticate with X-Salesperson-ID header (or login)
   - [ ] Dashboard shows only assigned customers
   - [ ] Cannot see other salespeople's customers

**Expected Result:** Access restricted to assigned customers only

2. **Review Customer List**
   - [ ] See all assigned customers
   - [ ] View AR summary (total balance, past due)
   - [ ] See credit utilization bars
   - [ ] See alert indicators

**Expected Result:** Clear view of portfolio

3. **Identify Credit Issues**
   - [ ] Filter for customers > 80% credit utilization
   - [ ] See customers approaching limit
   - [ ] Note customers over limit (red indicator)

**Expected Result:** Proactive credit visibility

4. **Check Customer Before Call**
   - [ ] Select customer "XYZ Builders"
   - [ ] Review AR balance and days overdue
   - [ ] Check for active alerts
   - [ ] Decide if need to discuss AR on call

**Expected Result:** Informed before customer interaction

5. **Attempt to Make Changes (Should Fail)**
   - [ ] Try to add a note (button should not exist)
   - [ ] Try to send email (button should not exist)
   - [ ] Try to create task (button should not exist)
   - [ ] Confirm read-only access

**Expected Result:** No modification capabilities (read-only)

6. **Know When to Escalate**
   - [ ] Find customer with critical alert
   - [ ] Note alert type and severity
   - [ ] Contact AR team with question
   - [ ] Get response from AR specialist

**Expected Result:** Clear escalation path

### Success Criteria
- ✅ Only sees assigned customers (SP001)
- ✅ AR data accurate and current
- ✅ Credit warnings visible
- ✅ Read-only access enforced
- ✅ Helps proactive customer management

---

## Test Scenario 6: Alert Management (AR Specialist)

**User:** Sarah Martinez
**Duration:** 15 minutes
**Objective:** Respond to and manage alerts

### Steps:

1. **Review Active Alerts**
   - [ ] Navigate to Alerts page
   - [ ] See all active alerts sorted by severity
   - [ ] Critical alerts have blinking animation
   - [ ] Filter by alert type
   - [ ] Filter by severity

**Expected Result:** Alerts prioritized and easy to filter

2. **Respond to Critical Alert**
   - [ ] Click on critical "Inactive Account" alert
   - [ ] Read alert description
   - [ ] Navigate to customer
   - [ ] Review account status
   - [ ] Take appropriate action (call, email, task)

**Expected Result:** Alert provides actionable information

3. **Dismiss Resolved Alert**
   - [ ] Find alert that's been resolved
   - [ ] Click "Dismiss" button
   - [ ] Add dismissal reason
   - [ ] Alert moves to dismissed status
   - [ ] Alert count decreases

**Expected Result:** Alerts can be dismissed when resolved

4. **Review Alert Summary**
   - [ ] View alert summary dashboard
   - [ ] See count by type (inactive, broken promise, etc.)
   - [ ] See count by severity (critical, high, medium, low)
   - [ ] Understand overall alert health

**Expected Result:** Summary provides big picture view

5. **Verify Alert Generation**
   - [ ] Manually trigger alert detection (if admin)
   - [ ] OR wait for nightly import
   - [ ] New alerts generated for qualifying accounts
   - [ ] Alert criteria applied correctly

**Expected Result:** Alerts generated automatically

### Success Criteria
- ✅ Alerts prioritized by severity
- ✅ Blinking animation works for critical
- ✅ Alert information actionable
- ✅ Can dismiss when resolved
- ✅ Automatic generation works

---

## Test Scenario 7: Email Communication (AR Specialist)

**User:** Sarah Martinez
**Duration:** 15 minutes
**Objective:** Send emails using templates

### Steps:

1. **Send Statement Email**
   - [ ] Navigate to customer
   - [ ] Click "Send Email"
   - [ ] Select "Statement" template
   - [ ] Verify auto-populated data (customer name, balance, aging)
   - [ ] Preview email
   - [ ] Send email

**Expected Result:** Email sent with correct data

2. **Send Payment Reminder**
   - [ ] Select customer with overdue invoice
   - [ ] Click "Send Email"
   - [ ] Select "Payment Reminder" template
   - [ ] Verify overdue amount correct
   - [ ] Customize message (add personal note)
   - [ ] Send email

**Expected Result:** Template allows customization

3. **Send Custom Email**
   - [ ] Click "Send Email"
   - [ ] Select "Custom" template
   - [ ] Enter subject and body
   - [ ] Add customer-specific details
   - [ ] Send email

**Expected Result:** Custom emails supported

4. **Verify Email Logging**
   - [ ] Navigate to customer notes
   - [ ] Find email note (auto-created)
   - [ ] See email subject and timestamp
   - [ ] Note type is "email_sent"

**Expected Result:** All emails logged automatically

5. **Review Email History**
   - [ ] Filter notes by type: "Email Sent"
   - [ ] See all emails sent to customer
   - [ ] Review dates and subjects
   - [ ] Understand communication frequency

**Expected Result:** Complete email history visible

### Success Criteria
- ✅ Templates work correctly
- ✅ Data auto-populated accurately
- ✅ Customization allowed
- ✅ Emails logged automatically
- ✅ History easily accessible

---

## Test Scenario 8: Task Management (AR Specialist)

**User:** Sarah Martinez
**Duration:** 15 minutes
**Objective:** Manage collection tasks effectively

### Steps:

1. **View My Tasks**
   - [ ] Navigate to "My Tasks" view
   - [ ] See all assigned tasks
   - [ ] Filter by status (Open, In Progress, Completed)
   - [ ] Filter by due date (Overdue, Today, This Week)

**Expected Result:** Clear view of all tasks

2. **Create New Task**
   - [ ] Click "Create Task"
   - [ ] Enter title: "Call ABC Construction re: invoice INV-001"
   - [ ] Set due date (tomorrow)
   - [ ] Set priority: High
   - [ ] Add description
   - [ ] Save task

**Expected Result:** Task created successfully

3. **Update Task Status**
   - [ ] Find task in progress
   - [ ] Change status to "In Progress"
   - [ ] Add progress note
   - [ ] Save changes

**Expected Result:** Status updated correctly

4. **Complete Task**
   - [ ] Find completed task
   - [ ] Mark as "Completed"
   - [ ] Task moves to completed section
   - [ ] Completion timestamp recorded

**Expected Result:** Task completion tracked

5. **Review Team Tasks (Manager)**
   - [ ] Switch to Michael Chen account
   - [ ] Navigate to "Team Tasks" view
   - [ ] See all tasks for AR team
   - [ ] Filter by assigned person
   - [ ] Review completion rates

**Expected Result:** Manager can monitor team workload

### Success Criteria
- ✅ Tasks easy to create and manage
- ✅ Filtering works correctly
- ✅ Status updates tracked
- ✅ Completion recorded
- ✅ Team view available for managers

---

## Test Scenario 9: Data Import & Sync (IT Admin)

**User:** IT Admin
**Duration:** 20 minutes
**Objective:** Verify Epicor data sync works

### Steps:

1. **Review Import History**
   - [ ] Navigate to Admin > Imports
   - [ ] See list of recent imports
   - [ ] View import details (date, status, records processed)
   - [ ] Check for any failed imports

**Expected Result:** Complete import history visible

2. **Trigger Manual Import**
   - [ ] Click "Trigger Import" button
   - [ ] Import process starts
   - [ ] Progress indicator shows
   - [ ] Import completes successfully

**Expected Result:** Manual trigger works

3. **Review Import Details**
   - [ ] Click on completed import
   - [ ] See records imported by type (customers, invoices, payments)
   - [ ] See validation results
   - [ ] See any errors or warnings

**Expected Result:** Detailed import information

4. **Check Data Quality**
   - [ ] Spot-check imported customers
   - [ ] Verify balances match Epicor
   - [ ] Verify invoice dates correct
   - [ ] Verify payment applications correct

**Expected Result:** Data accuracy 100%

5. **Handle Import Failure**
   - [ ] Simulate import failure (corrupt CSV file)
   - [ ] Import should fail gracefully
   - [ ] Error message clear and actionable
   - [ ] Retry logic should work

**Expected Result:** Errors handled gracefully

6. **Verify Alert Generation**
   - [ ] After import, alerts generated automatically
   - [ ] Check that new alerts appear
   - [ ] Verify alert criteria applied correctly

**Expected Result:** Alerts generated post-import

### Success Criteria
- ✅ Imports run successfully
- ✅ Data accuracy verified
- ✅ Manual trigger works
- ✅ Error handling robust
- ✅ Post-import processes (alerts) work

---

## Test Scenario 10: Performance with Large Data Volume

**User:** Any user
**Duration:** 15 minutes
**Objective:** Verify performance acceptable

### Steps:

1. **Dashboard Load Time**
   - [ ] Navigate to dashboard
   - [ ] Time page load
   - [ ] Should load in < 3 seconds

**Expected Result:** Fast load time

2. **Customer Search**
   - [ ] Search for customer by name
   - [ ] Results appear in < 1 second
   - [ ] Search is case-insensitive
   - [ ] Partial matches work

**Expected Result:** Search is fast and accurate

3. **Worklist Sorting**
   - [ ] Sort worklist by priority
   - [ ] Sort by customer name
   - [ ] Sort by balance
   - [ ] Each sort completes in < 2 seconds

**Expected Result:** Sorting is responsive

4. **Large Customer (100+ Invoices)**
   - [ ] Navigate to customer with many invoices
   - [ ] Customer 360 loads in < 3 seconds
   - [ ] All invoices display
   - [ ] Can scroll through invoice list smoothly

**Expected Result:** Handles large data gracefully

5. **Analytics Calculation**
   - [ ] Navigate to DSO Analysis
   - [ ] Calculation completes in < 5 seconds
   - [ ] Chart renders smoothly
   - [ ] Can interact with chart

**Expected Result:** Analytics performant

### Success Criteria
- ✅ All pages load in < 3 seconds
- ✅ Searches complete in < 1 second
- ✅ No lag or freezing
- ✅ Smooth user experience
- ✅ Handles 100 customers easily

---

## UAT Completion Checklist

### For Each Scenario

- [ ] Scenario completed successfully
- [ ] All expected results achieved
- [ ] No bugs encountered (or bugs logged)
- [ ] User satisfied with workflow
- [ ] Performance acceptable
- [ ] Feedback documented

### Overall UAT

- [ ] All 10 scenarios completed
- [ ] Bug log created (if any issues found)
- [ ] User satisfaction survey completed
- [ ] UAT sign-off obtained from AR Manager
- [ ] System approved for production
- [ ] Training can proceed

---

## Bug Reporting Template

**Bug ID:** UAT-[Number]
**Severity:** Critical / High / Medium / Low
**Scenario:** [Which scenario]
**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Result:**
**Actual Result:**
**Screenshots:** [Attach if applicable]
**Workaround:** [If any]
**Status:** Open / In Progress / Resolved / Won't Fix

---

## UAT Sign-Off

**I certify that the AR Control Hub has been tested and meets business requirements for production use.**

**AR Manager:** _________________________ Date: _______
**AR Specialist:** _______________________ Date: _______
**IT Manager:** _________________________ Date: _______
**Finance VP:** _________________________ Date: _______

---

**UAT Success = Confidence in System = Smooth Go-Live! 🚀**
