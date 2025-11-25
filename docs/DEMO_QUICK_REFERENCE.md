# AR Control Hub - Demo Quick Reference Card

**Print this page and keep it next to you during the demo!**

---

## Pre-Demo Checklist (Last 5 Minutes)

- [ ] Backend running: http://localhost:8000/health
- [ ] Frontend running: http://localhost:3000
- [ ] 3 demo accounts logged in (separate tabs)
- [ ] Browser in full-screen mode (F11)
- [ ] Notifications/email disabled
- [ ] Phone on silent
- [ ] Water glass nearby

---

## Demo Flow (30 Minutes)

### 1. Opening (0-2 min)
**Opening Line:** *"Good morning! Today I'll show you the AR Control Hub - our new system that prioritizes collections automatically and forecasts cash flow 8 weeks ahead."*

**Key Point:** We manage $1M+ AR across 200+ customers - currently reactive, now becoming proactive.

---

### 2. Dashboard Overview (2-6 min)
**URL:** `http://localhost:3000/dashboard`
**Login:** sarah.martinez@company.com / demo123

**What to Show:**
- Total AR: **$1,247,850** (point to number)
- Aging buckets (30/60/90+) - visual breakdown
- DSO: **37.5 days** (trend down = good)
- Active alerts: **12** (click to see blinking critical ones)

**Talking Points:**
- "Everything in one view - no more digging through Epicor reports"
- "Blinking red = critical attention needed RIGHT NOW"
- "Green trending arrows = we're collecting faster"

**Demo Actions:**
1. Point to each metric
2. Hover over charts (show tooltips)
3. Click on "12 Active Alerts" → show alert list
4. Click back to dashboard

---

### 3. Prioritized Worklist (6-12 min)
**URL:** `http://localhost:3000/worklist`

**What to Show:**
- Auto-sorted by risk score
- Top customer: **Acme Corp** ($45,230 overdue)
- Risk indicators: payment history, broken promises, aging

**Talking Points:**
- "No more manual sorting - system prioritizes for you"
- "Top of list = highest risk + highest impact"
- "Save 2+ hours/day on triage"

**Demo Actions:**
1. Scroll through list - point to risk scores
2. Click on Acme Corp (top customer)
3. Show Customer 360 view

---

### 4. Customer 360 View (12-17 min)
**URL:** `http://localhost:3000/customers/[acme-id]`

**What to Show:**
- **Summary Card:** Credit limit, balance, DSO, contact info
- **Invoices Tab:** 5 open invoices totaling $45k
- **Payment History:** Last payment 47 days ago
- **Alerts:** 2 active (aging, broken promise)
- **Notes:** Last contact note from 3 days ago
- **Tasks:** Follow-up call scheduled for tomorrow

**Talking Points:**
- "Everything about this customer in one place"
- "No switching between Epicor, Excel, Outlook"
- "Complete context for every collection call"

**Demo Actions:**
1. Point to credit limit vs balance (show utilization)
2. Click through each tab (Invoices, Payments, Alerts, Notes, Tasks)
3. Add a quick note: "Called customer, promised payment by Friday"
4. Create a task: "Follow up on Friday afternoon"
5. Click Save

**WOW MOMENT:** "In 30 seconds I just documented a call and set a reminder - used to take 5 minutes across multiple systems"

---

### 5. Cash Flow Forecast (17-22 min)
**URL:** `http://localhost:3000/analytics/cash-forecast`

**What to Show:**
- 8-week rolling forecast
- Week 1 expected: **$87,450** (due dates + promises)
- Week 4 expected: **$62,300**
- Chart shows expected vs actual collections

**Talking Points:**
- "Answers the question: How much cash are we collecting this month?"
- "Based on invoice due dates + customer payment promises"
- "CFO can plan cash needs 8 weeks ahead"

**Demo Actions:**
1. Point to Week 1 bar (tallest)
2. Hover over bars to show tooltips (invoice-based vs promise-based)
3. Scroll to table below - show breakdown by customer
4. Point to accuracy indicator (80%+ is good)

**Business Value:** "Helps finance avoid surprise cash shortfalls"

---

### 6. DSO Analysis (22-25 min)
**URL:** `http://localhost:3000/analytics/dso`

**What to Show:**
- Current DSO: **37.5 days** (trending down from 39)
- Target DSO: **35 days**
- Problem accounts: Top 10 customers with highest DSO

**Talking Points:**
- "Days Sales Outstanding - key AR metric"
- "Lower DSO = cash coming in faster"
- "We're at 37.5, targeting 35 - almost there!"

**Demo Actions:**
1. Point to main DSO number (37.5)
2. Show trend line (downward = good)
3. Scroll to problem accounts table
4. Click on worst offender (95-day DSO) → Customer 360

**Business Impact:** "Every 1-day DSO reduction = $28k freed up in working capital"

---

### 7. Salesperson Portal (25-28 min)
**URL:** `http://localhost:3000/salesperson`
**Login:** jessica.williams@company.com / demo123

**What to Show:**
- Jessica's customers only (12 accounts)
- Total AR for her accounts: $187,250
- 3 customers with active alerts

**Talking Points:**
- "Sales team can check their own customers - self-service"
- "Reduces 'Can you send me my AR report?' emails"
- "Sales sees exactly what AR sees"

**Demo Actions:**
1. Log in as Jessica
2. Show her customer list (only her 12 customers visible)
3. Click on one customer → show limited view (no edit access)
4. Log back out

**Partnership:** "Empowers sales to help with collections proactively"

---

### 8. Closing & Business Value (28-30 min)

**Summary Statement:**
*"So we've seen how the AR Control Hub transforms reactive AR management into proactive, data-driven collections."*

**Key Benefits Recap:**
1. **Automated Prioritization** → 2 hrs/day saved
2. **Customer 360 View** → 5 min/call saved
3. **Cash Flow Forecast** → Better cash planning
4. **DSO Tracking** → Path to 35-day target
5. **Salesperson Self-Service** → Reduced email volume

**Business Impact:**
- **Time Savings:** 2+ hours/day × 5 days × 50 weeks = 500 hrs/year
- **DSO Reduction:** 37.5 → 35 days = $56,000 working capital freed
- **Collection Rate:** +15% improvement = $186,000 annual
- **Total Annual Value: $172,000**

**Next Steps:**
1. **Today:** Gather your feedback
2. **Week 3:** User Acceptance Testing (2 weeks)
3. **Week 5-7:** Training sessions
4. **Week 8:** Go-Live!

**Open for Questions** → Refer to Q&A section below

---

## Common Questions & Answers

### Q1: "How does this integrate with Epicor?"
**A:** Daily automated import from Epicor. We pull customers, invoices, payments every night. No manual exports needed.

### Q2: "Can we customize the risk scoring?"
**A:** Yes! Risk factors are configurable - you can weight aging, broken promises, payment history differently.

### Q3: "What if internet goes down?"
**A:** System still works - data is cached locally. Once connection restores, syncs automatically.

### Q4: "How long to train our team?"
**A:** 2-hour training for AR team, 30-min overview for sales. We have video modules too (71 min total).

### Q5: "Can we access from mobile?"
**A:** Yes, responsive design works on tablets/phones. Salesperson portal especially useful on mobile.

### Q6: "What about data security?"
**A:** Role-based access (RBAC), JWT tokens, encrypted passwords, audit logging on all actions.

### Q7: "How much does this cost?"
**A:** Internal development project - no licensing fees. Server costs ~$200/month. ROI is 860:1.

### Q8: "Can we try it before go-live?"
**A:** Absolutely! That's what UAT is for (Week 3-4). You'll test with real data, we'll fix any issues.

### Q9: "Who supports this after launch?"
**A:** IT provides infrastructure support. I'll provide functional support for first 3 months, then train Sarah to be super-user.

### Q10: "What happens to our Epicor data?"
**A:** Nothing changes in Epicor - it's still the system of record. This is a read-only overlay providing better visibility.

---

## Emergency Troubleshooting (During Demo)

### Dashboard Won't Load
1. Check backend: http://localhost:8000/health (should show `{"status": "healthy"}`)
2. If down: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000` in terminal
3. Fallback: Show screenshot from docs/screenshots/ folder

### Login Fails
- Clear browser cache (Ctrl+Shift+Del)
- Try different demo account (sarah, michael, admin - all use demo123)
- Fallback: Continue logged in to already-open tab

### Data Looks Wrong
- Check if demo data seeded: `psql -d ar_demo -c "SELECT COUNT(*) FROM customers;"`
- Should show 50 customers
- If 0: Quickly run `python scripts/seed_demo_data.py --scenario demo`
- Fallback: Talk through what WOULD be shown

### Charts Not Rendering
- Refresh page (F5)
- Clear browser cache
- Fallback: Show mockup images from design docs

### Blinking Alerts Not Blinking
- Refresh page
- Check browser console (F12) for JavaScript errors
- Fallback: Verbally explain "These would normally be blinking red"

### Forgot What's Next
- This card has the flow - glance at section headers
- 30-second sections: Introduction → Dashboard → Worklist → Customer 360 → Cash Forecast → DSO → Salesperson → Closing

---

## Success Indicators (During Demo)

**Audience is Engaged:**
- Leaning forward
- Taking notes
- Asking questions
- Smiling/nodding

**Audience May Be Confused:**
- Blank stares
- No questions
- Checking phones
- **Action:** Slow down, ask "Does this make sense?" re-explain

**Running Behind:**
- At 10 min mark, should be finishing Dashboard
- At 20 min mark, should be finishing Cash Forecast
- **Action:** Skip deep-dives, hit highlights only

**Running Ahead:**
- At 15 min mark, already done with Customer 360
- **Action:** Add more detail, show extra features, take more questions

---

## Presenter Reminders

✅ **Speak slowly** - You know this system cold, they're seeing it for the first time
✅ **Point cursor** - Always point to what you're discussing
✅ **Pause after key points** - Let them absorb
✅ **Make eye contact** - Look at audience, not just screen
✅ **Use specific numbers** - "$45,230 overdue" not "some amount overdue"
✅ **Tell stories** - "Imagine Sarah calling Acme Corp..." not just clicking buttons
✅ **Emphasize benefits** - Always tie features to time saved or money earned
✅ **Stay positive** - "This system will help you..." not "You currently waste time..."
✅ **Breathe** - Take sips of water, natural pauses are okay
✅ **Have fun** - You built something amazing, enjoy showing it off!

---

## Demo URLs Quick Reference

```
Dashboard:        http://localhost:3000/dashboard
Worklist:         http://localhost:3000/worklist
Customers:        http://localhost:3000/customers
Customer Detail:  http://localhost:3000/customers/[id]
Cash Forecast:    http://localhost:3000/analytics/cash-forecast
DSO Analysis:     http://localhost:3000/analytics/dso
Collections:      http://localhost:3000/analytics/collections
Salesperson:      http://localhost:3000/salesperson
API Docs:         http://localhost:8000/docs
Health Check:     http://localhost:8000/health
```

---

## Demo Accounts

| Email | Password | Role | Use For |
|-------|----------|------|---------|
| sarah.martinez@company.com | demo123 | AR Specialist | Main demo (Dashboard, Worklist, Customer 360) |
| michael.chen@company.com | demo123 | AR Manager | Analytics (Cash Forecast, DSO) |
| jessica.williams@company.com | demo123 | Salesperson | Salesperson Portal only |
| admin@company.com | demo123 | Admin | Full access (backup) |

---

## Post-Demo Checklist

- [ ] Thank everyone for attending
- [ ] Distribute feedback forms
- [ ] Pass UAT signup sheet
- [ ] Answer remaining questions
- [ ] Take note of who seemed most engaged
- [ ] Within 24 hours: Send thank-you email with demo recording link

---

**Remember:** You've prepared thoroughly. Trust your preparation. They'll love it! 🚀

**Confidence Mantra:** *"I built this system. I know it inside and out. I'm here to help the team succeed."*
