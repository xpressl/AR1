# AR Control Hub - Demo Preparation Guide

**Demo Date:** [To Be Scheduled]
**Duration:** 30 minutes
**Audience:** AR Team, Finance Leadership, IT Management
**Presenter:** [Your Name]

---

## Table of Contents

1. [Demo Overview](#demo-overview)
2. [Sample Data Setup](#sample-data-setup)
3. [Demo Script](#demo-script)
4. [Key Talking Points](#key-talking-points)
5. [Live Demo Checklist](#live-demo-checklist)
6. [Anticipated Questions & Answers](#anticipated-questions--answers)
7. [Success Metrics to Highlight](#success-metrics-to-highlight)

---

## Demo Overview

### Objective
Demonstrate the AR Control Hub's ability to streamline accounts receivable operations, automate routine tasks, and provide actionable insights for better cash flow management.

### Key Messages
1. **Saves Time:** Automated worklists eliminate manual sorting and prioritization
2. **Catches Issues Early:** Proactive alerts prevent small problems from becoming large ones
3. **Improves Collections:** Promise tracking and DSO analysis drive better results
4. **Increases Visibility:** Management dashboards provide real-time AR health snapshot

### Demo Flow (30 minutes)
- **0-2 min:** Introduction & business problem
- **2-10 min:** Dashboard & prioritized worklist walkthrough
- **10-18 min:** Customer 360 view & collection workflow
- **18-24 min:** Analytics & forecasting capabilities
- **24-28 min:** Salesperson portal demonstration
- **28-30 min:** Q&A and next steps

---

## Sample Data Setup

### Creating Realistic Demo Data

Run this script to populate the database with realistic sample data:

```bash
# Location: scripts/seed_demo_data.py
python scripts/seed_demo_data.py --scenario demo
```

### Sample Data Includes:

**50 Customers** representing realistic AR portfolio:
- 10 customers with critical alerts (inactive 120+ days, over credit limit)
- 15 customers with overdue invoices (30-90+ days)
- 10 customers with payment promises (some kept, some broken)
- 10 customers current and in good standing
- 5 customers with recent disputes

**200 Invoices** across aging buckets:
- Current: 80 invoices ($400,000)
- 1-30 Days: 50 invoices ($250,000)
- 31-60 Days: 40 invoices ($200,000)
- 61-90 Days: 20 invoices ($100,000)
- 90+ Days: 10 invoices ($80,000)
- **Total AR:** $1,030,000

**100 Payments** with realistic patterns:
- On-time payments (60%)
- Late payments (30%)
- Partial payments (10%)
- Average days to pay: 38 days

**150 Notes** documenting interactions:
- Phone calls (60)
- Emails sent (40)
- Promises to pay (30)
- General notes (20)

**25 Active Alerts:**
- Critical (8): Inactive accounts 120+ days, broken promises
- High (10): Invoices 90+ days overdue
- Medium (7): Over credit limit, high risk accounts

**40 Tasks:**
- Overdue (5): Follow-ups that need immediate attention
- Due Today (8): Tasks scheduled for today
- This Week (12): Upcoming collection activities
- Future (15): Scheduled callbacks and reviews

### Demo Personas

**1. Sarah Martinez (AR Specialist)**
- Uses dashboard daily to prioritize work
- Manages 30-40 accounts
- Focuses on accounts 60+ days past due

**2. Michael Chen (AR Manager)**
- Reviews analytics dashboards
- Monitors team performance
- Uses forecasts for cash planning

**3. Jessica Williams (Salesperson - SP001)**
- Checks salesperson portal weekly
- Monitors credit utilization
- Responds to customer alerts proactively

---

## Demo Script

### PART 1: Introduction (0-2 minutes)

**Opening:**
> "Good [morning/afternoon], everyone. Today I'm excited to show you the AR Control Hub - our new system designed to modernize how we manage accounts receivable.
>
> Before we dive in, let me quickly frame the business problem we're solving:
>
> - Our AR team currently manages $1M+ in receivables across 200+ customers
> - Collections are reactive - we chase the loudest customer, not the riskiest
> - Critical issues hide in spreadsheets until they become major problems
> - Cash flow forecasting is manual and time-consuming
> - Sales team has limited visibility into customer AR status
>
> The AR Control Hub changes all of this. Let me show you how."

### PART 2: Dashboard & Worklist (2-10 minutes)

**[Navigate to Dashboard]**

> "This is what an AR specialist sees when they log in each morning. The dashboard gives an instant snapshot of AR health."

**Point out key metrics:**
- Total AR: $1,030,000
- Overdue Amount: $380,000 (37%)
- Current DSO: 38 days (target: 35 days)
- Active Alerts: 25 (8 critical)

> "Notice the aging breakdown - we can see exactly how much is current versus past due. The color coding makes it easy to spot problems."

**[Scroll to Worklist]**

> "But here's where it gets powerful - the prioritized worklist. Every account is automatically scored based on:
> - Days past due
> - Total overdue balance
> - Credit utilization
> - Alert severity
> - Broken promise history
>
> This means Sarah [AR specialist] doesn't waste time deciding who to call first - the system tells her."

**[Click on top priority account - "ABC Construction Supply"]**

> "Let's look at this one - ABC Construction Supply. High priority score of 87 because they have $45,000 overdue for 75 days AND they broke a promise to pay last week."

### PART 3: Customer 360 View (10-18 minutes)

**[Show Customer 360 page]**

> "This is the Customer 360 view - everything about ABC Construction in one place."

**Walk through sections:**

**1. Customer Header**
- Credit limit: $50,000
- Current balance: $45,000 (90% utilization)
- Status: Active, but flagged

**2. Active Alerts (Blinking!)**
> "See this red pulsing alert? That's by design - critical alerts blink to grab attention. This customer has been inactive for 120+ days, which is our threshold for escalation."

**3. Invoice List**
- Show aging buckets
- Point out oldest invoice (75 days)
- Demonstrate drill-down to invoice detail

**4. Notes & Communication History**
> "Every interaction is logged here. Last contact was 2 weeks ago - a phone call where they promised to pay $10,000 by last Friday. They didn't, which is why we have a broken promise alert."

**5. Quick Actions**
> "From here, Sarah can take immediate action:"

**[Demo Add Note]**
- Click "Add Note"
- Select "Phone Call"
- Enter: "Spoke with John - promises $15,000 by next Friday"
- Set promise date and amount
- Save

> "That's it - the promise is now tracked, and if they don't pay by Friday, the system will automatically flag it as broken."

**[Demo Send Email]**
- Click "Send Email"
- Select "Payment Reminder" template
- Show auto-populated fields (customer name, balance, overdue amount)
- Preview email
- (Don't actually send in demo)

> "Email templates save time and ensure consistency. All sent emails are logged automatically."

**[Demo Create Task]**
- Click "Create Task"
- Title: "Follow up if no payment received"
- Due date: Next Monday
- Priority: High
- Assign to: Sarah Martinez
- Save

> "Tasks ensure nothing falls through the cracks. Sarah will see this on her dashboard Monday morning if the payment doesn't arrive."

### PART 4: Analytics & Forecasting (18-24 minutes)

**[Navigate to Analytics > Cash Flow Forecast]**

> "Now let's look at the management view. This is the 8-week cash flow forecast."

**Point out:**
- Blue bars: Invoice-based forecast (based on due dates)
- Green bars: Promise-based forecast (based on payment promises)
- Week-by-week breakdown
- Total forecast: $450,000 over next 8 weeks

> "This helps Michael [AR Manager] answer the CFO's favorite question: 'How much cash are we collecting this month?'
>
> The system tracks forecast accuracy too - we're currently at 87% accuracy, which improves as we feed it more historical data."

**[Navigate to Analytics > DSO Analysis]**

> "DSO - Days Sales Outstanding - is our key performance metric. Industry standard for building supplies is 35 days."

**Show DSO dashboard:**
- Current DSO: 38 days (3 days above target)
- 6-month trend chart
- Color coding: green months (on target), red months (above target)

> "We can see DSO creeping up over the past 3 months - from 34 days to 38 days. That's $120,000 tied up longer than it should be."

**[Click "Problem Accounts"]**

> "The system automatically identifies accounts dragging down our DSO. These 8 customers have DSO 50%+ above our company average."

**Point to specific account:**
> "XYZ Builders - 72-day DSO versus company average of 38. That's a red flag for the collections team."

### PART 5: Salesperson Portal (24-28 minutes)

**[Switch to Salesperson Portal view]**
**[Use Jessica Williams - SP001 credentials]**

> "One unique feature is the Salesperson Portal. Sales reps can monitor their customers' AR status without bothering the AR team."

**Show features:**
- Customer list (filtered by salesperson assignment)
- AR summary for Jessica's portfolio
- Credit utilization bars
- Alert indicators

> "Jessica can see that 3 of her customers are over credit limit. She can proactively reach out before they try to place an order and get declined.
>
> This is read-only access - she can't make changes, just stay informed."

**[Click on a customer]**

> "She can drill into details, see which invoices are overdue, and understand why her customer might be flagged."

> "This creates accountability - sales owns the relationship, so they should help with collections when needed."

### PART 6: Wrap-Up & Next Steps (28-30 minutes)

**Summary:**
> "To summarize what we've seen:
>
> ✅ **Automated Prioritization** - No more guessing who to call first
> ✅ **Proactive Alerts** - Catch problems before they escalate
> ✅ **Complete Customer View** - Everything in one place
> ✅ **Promise Tracking** - Hold customers accountable
> ✅ **Cash Flow Forecasting** - Better planning for management
> ✅ **DSO Analysis** - Identify problem accounts quickly
> ✅ **Salesperson Visibility** - Sales team stays informed
>
> This system transforms AR from reactive firefighting to proactive management."

**Next Steps:**
> "We're ready for the next phase:
> 1. User Acceptance Testing (2 weeks) - AR team tests with real data
> 2. Training Sessions (1 week) - Hands-on training for all users
> 3. Production Deployment (1 day) - Go live!
> 4. Monitoring & Support (ongoing) - We'll track adoption and results
>
> Questions?"

---

## Key Talking Points

### For AR Team
- **"Saves 2+ hours per day"** - No more manual spreadsheet sorting
- **"Never miss a broken promise"** - Automatic tracking and alerts
- **"Know exactly who to call first"** - Priority scoring eliminates guesswork
- **"All customer history in one place"** - No more hunting through emails

### For Finance Leadership
- **"Real-time AR health visibility"** - Know where you stand instantly
- **"8-week cash flow forecast"** - Plan with confidence
- **"DSO tracking and trending"** - Measure what matters
- **"Reduce DSO by 10%"** - Target: 35 days (currently 38)
- **"Improve collection rates by 15%"** - Through better prioritization

### For IT Management
- **"Built on modern tech stack"** - FastAPI, React, PostgreSQL
- **"Secure and scalable"** - JWT authentication, RBAC, SSL/TLS ready
- **"Integrates with Epicor"** - Daily automated data sync
- **"Comprehensive documentation"** - Deployment guide, API docs, runbooks
- **"Production-ready"** - Already tested and secured

### For Sales Team
- **"Stay informed without bothering AR"** - Self-service portal
- **"Prevent order holds"** - See credit issues before customers do
- **"Help your customers"** - Know when to reach out proactively
- **"Read-only access"** - No risk of accidental changes

---

## Live Demo Checklist

### 1 Week Before Demo

- [ ] Schedule demo meeting (30 min + 15 min buffer)
- [ ] Invite stakeholders (AR team, Finance leadership, IT, Sales managers)
- [ ] Set up demo environment (separate from production)
- [ ] Run `seed_demo_data.py` script
- [ ] Verify all features working in demo environment
- [ ] Create demo user accounts (Sarah, Michael, Jessica)
- [ ] Test on presentation screen/projector
- [ ] Prepare backup plan (screen recording if live demo fails)

### 1 Day Before Demo

- [ ] Test login credentials for all demo personas
- [ ] Verify sample data looks realistic and current
- [ ] Clear browser cache/cookies
- [ ] Bookmark key pages for quick navigation
- [ ] Test all workflows end-to-end
- [ ] Charge laptop fully
- [ ] Prepare handouts (one-page feature summary)
- [ ] Send reminder email to attendees

### 1 Hour Before Demo

- [ ] Arrive early to set up
- [ ] Connect laptop to projector/screen
- [ ] Test audio (if presenting remotely)
- [ ] Open browser with bookmarked pages
- [ ] Log in to all demo accounts
- [ ] Close unnecessary applications
- [ ] Silence phone and notifications
- [ ] Have water available
- [ ] Cue up backup screen recording (just in case)

### During Demo

- [ ] Start with business problem statement
- [ ] Speak slowly and clearly
- [ ] Pause for questions after each section
- [ ] Point cursor to what you're discussing
- [ ] Highlight numbers and metrics
- [ ] Show blinking alerts (visual impact)
- [ ] Demonstrate quick actions (add note, create task)
- [ ] Use realistic scenarios
- [ ] Keep to 30-minute time limit
- [ ] End with clear next steps

### After Demo

- [ ] Send thank-you email with next steps
- [ ] Share demo recording link
- [ ] Distribute one-page feature summary
- [ ] Schedule UAT kickoff meeting
- [ ] Gather feedback and questions
- [ ] Update demo based on feedback
- [ ] Begin planning training sessions

---

## Anticipated Questions & Answers

### Q: "How does data get into the system?"

**A:** "Great question. We have a nightly automated sync from Epicor Eagle. At 5 AM each morning, the system:
1. Exports customer, invoice, and payment data from Epicor to CSV files
2. Validates the data for quality and completeness
3. Loads it into the AR Control Hub database
4. Generates alerts based on the new data

The process takes about 15 minutes and runs completely automatically. The AR team sees fresh data when they log in at 8 AM."

### Q: "What if we need to make changes to customer data?"

**A:** "All changes still happen in Epicor - that remains the system of record. The AR Control Hub is read-only for customer master data. However, you CAN add notes, create tasks, send emails, and track promises - those are AR Control Hub specific and don't sync back to Epicor."

### Q: "Can we customize the alert rules?"

**A:** "Absolutely. The alert rules are configurable. Right now we have:
- Inactive account: 120+ days no activity
- Overdue invoice: 90+ days past due
- Over credit limit: Balance > limit
- Broken promise: 3+ days past promise date

We can adjust these thresholds based on your business policies."

### Q: "How accurate is the cash flow forecast?"

**A:** "The forecast starts at about 70% accuracy and improves as the system learns your customers' payment patterns. After 3-6 months of history, we typically see 85-90% accuracy. You can also see the forecast accuracy tracking in the Analytics dashboard."

### Q: "What happens if the nightly sync fails?"

**A:** "The system has built-in monitoring and retry logic. If a sync fails:
1. It retries automatically (up to 3 times with exponential backoff)
2. Sends email alert to the IT team
3. The previous day's data remains in the system so work can continue
4. You can manually trigger a sync from the admin panel

We also have a health check dashboard showing the status of all recent imports."

### Q: "Can we access this from mobile devices?"

**A:** "The current version is responsive web design - it works on tablets and large phones, though it's optimized for desktop. Phase 4 (weeks 19-24) includes a dedicated mobile app for iOS and Android if there's demand for it."

### Q: "How long does training take?"

**A:** "For AR specialists, about 2 hours of hands-on training. For managers using analytics, about 1 hour. For salespeople using the portal, about 30 minutes. We'll provide training sessions, user guides, and video tutorials."

### Q: "What about security and data privacy?"

**A:** "Security is built-in:
- JWT token authentication with 30-minute expiration
- Role-based access control (AR Manager, AR Specialist, Salesperson, Viewer)
- All passwords hashed with bcrypt
- HTTPS encryption in production
- Salesperson portal only shows their assigned customers
- Complete audit trail of all user actions
- Regular security updates and patches"

### Q: "Can we export reports to Excel?"

**A:** "Phase 1-3 includes CSV export for most reports. Phase 4 will add full Excel exports with formatting and PDF generation. For now, you can export the data and format it in Excel as needed."

### Q: "What's the ROI on this system?"

**A:** "Based on industry benchmarks:
- **Time Savings:** 2 hours/day per AR specialist × $30/hour × 250 days = $15,000/year
- **DSO Reduction:** 10% improvement on $1M AR = $100k freed up in cash
- **Collection Rate:** 15% improvement on $380k overdue = $57k additional collections
- **Estimated Annual Value:** $172,000

Implementation cost is minimal since we built it in-house. ROI achieved in < 3 months."

### Q: "When can we go live?"

**A:** "We're production-ready now. Proposed timeline:
- Week 1-2: User Acceptance Testing with AR team
- Week 3: Training sessions for all users
- Week 4: Production deployment (1 day)
- Week 5+: Ongoing support and monitoring

If UAT goes smoothly, we could be live in 4 weeks."

---

## Success Metrics to Highlight

### Immediate Benefits (Day 1)
- ✅ All AR data in one centralized location
- ✅ Automated priority scoring saves 2+ hours/day
- ✅ Proactive alerts prevent issues from escalating
- ✅ Complete customer history accessible in seconds

### Short-Term Wins (30 days)
- 📊 10% reduction in time spent on routine collections
- 📊 95% promise tracking accuracy (vs. 60% manual tracking)
- 📊 Zero broken promises missed
- 📊 50% reduction in "urgent" escalations

### Long-Term Impact (90 days)
- 📈 Reduce DSO from 38 to 35 days (target)
- 📈 Improve collection rate by 15%
- 📈 Free up $100k in working capital
- 📈 90%+ forecast accuracy for cash planning

### Operational Improvements
- 🎯 100% of critical accounts contacted weekly
- 🎯 Average response time to customer inquiries: < 2 hours
- 🎯 Sales team satisfaction with AR visibility: 8+/10
- 🎯 AR team workload stress reduction: Measurable via survey

---

## Demo Materials to Prepare

### Digital Materials

1. **One-Page Feature Summary (PDF)**
   - Key capabilities
   - Benefits by role
   - Implementation timeline
   - Contact information

2. **Demo Recording (Video)**
   - Full 30-minute walkthrough
   - Hosted on internal network
   - Available for those who couldn't attend
   - Can be used for future onboarding

3. **Screenshots (PNG)**
   - Dashboard view
   - Customer 360 view
   - Analytics dashboards
   - Salesperson portal
   - For presentations and documentation

4. **User Stories (Document)**
   - "A day in the life" scenarios
   - Before vs. after comparisons
   - Specific pain points solved

### Physical Materials

1. **Handouts (Printed)**
   - One-page feature summary
   - Quick reference card
   - FAQ sheet
   - Training schedule

2. **Feedback Forms**
   - Demo evaluation
   - Feature requests
   - Questions/concerns
   - UAT volunteer signup

---

## Post-Demo Action Items

### Immediate (Within 24 hours)
- [ ] Send thank-you email with demo recording link
- [ ] Distribute one-page feature summary
- [ ] Schedule UAT kickoff meeting
- [ ] Create Slack/Teams channel for Q&A

### Short-Term (Within 1 week)
- [ ] Incorporate feedback into system
- [ ] Schedule individual training sessions
- [ ] Prepare UAT test scenarios
- [ ] Create user guides and documentation
- [ ] Set up production environment

### Ongoing
- [ ] Weekly status updates to stakeholders
- [ ] UAT progress tracking
- [ ] Training session scheduling
- [ ] Go-live preparation checklist

---

**Demo Preparation Complete!**

Use this guide to deliver a compelling demonstration that showcases the AR Control Hub's capabilities and drives stakeholder buy-in for production deployment.
