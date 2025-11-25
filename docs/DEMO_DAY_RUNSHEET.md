# AR Control Hub - Demo Day Run Sheet

**Date:** ________________  **Time:** ________________  **Presenter:** ________________

**Print this sheet and check off items as you complete them.**

---

## T-Minus 60 Minutes (1 Hour Before)

**Physical Setup:**
- [ ] Arrive at conference room
- [ ] Connect laptop to projector/screen
- [ ] Test display (extend or duplicate mode)
- [ ] Set resolution to 1920x1080
- [ ] Test audio (if remote attendees)
- [ ] Arrange chairs for visibility
- [ ] Place handouts at each seat
- [ ] Set up feedback form station
- [ ] Water glass for presenter
- [ ] "Do Not Disturb" sign on door

**Technical Setup:**
- [ ] Phone on silent
- [ ] Close all unnecessary applications
- [ ] Disable email notifications
- [ ] Disable Slack/Teams notifications
- [ ] Disable browser notifications
- [ ] Close all browser tabs

---

## T-Minus 30 Minutes

**Environment Verification:**
```bash
# Run verification script
./scripts/verify_demo_environment.sh
```

- [ ] Verification script passed (all green)
- [ ] Backend health check: http://localhost:8000/health
- [ ] Frontend loads: http://localhost:3000
- [ ] Demo data shows $1.2M+ total AR

**Browser Setup:**
- [ ] Open Chrome/Firefox (preferred browser)
- [ ] Clear cache (Ctrl+Shift+Del)
- [ ] Zoom level: 100% (or 125% for projector)

**Demo Accounts (Pre-login in separate tabs):**

Tab 1: Sarah Martinez (Main Demo)
- [ ] Navigate to: http://localhost:3000
- [ ] Login: sarah.martinez@company.com / demo123
- [ ] Verify dashboard loads with data

Tab 2: Michael Chen (Analytics)
- [ ] Navigate to: http://localhost:3000
- [ ] Login: michael.chen@company.com / demo123
- [ ] Navigate to Cash Forecast page

Tab 3: Jessica Williams (Salesperson Portal)
- [ ] Navigate to: http://localhost:3000/salesperson
- [ ] Login: jessica.williams@company.com / demo123
- [ ] Verify only her 12 customers visible

Tab 4: Backup (Admin)
- [ ] Navigate to: http://localhost:3000
- [ ] Login: admin@company.com / demo123
- [ ] Keep this tab ready but hidden

**Warm Up Cache (Navigate Once to Each Page):**
- [ ] Dashboard: http://localhost:3000/dashboard
- [ ] Worklist: http://localhost:3000/worklist
- [ ] Customer 360: Click any customer from worklist
- [ ] Cash Forecast: http://localhost:3000/analytics/cash-forecast
- [ ] DSO Analysis: http://localhost:3000/analytics/dso

**Materials Check:**
- [ ] DEMO_QUICK_REFERENCE.md printed and next to laptop
- [ ] DEMO_TROUBLESHOOTING.md open in second window (just in case)
- [ ] Handouts counted (1 per attendee + 5 extra)
- [ ] Feedback forms ready
- [ ] UAT signup sheet ready
- [ ] Pens available

---

## T-Minus 10 Minutes

**Final Checks:**
- [ ] Full-screen mode ready (F11)
- [ ] Cursor visible and large enough
- [ ] Screen brightness adequate
- [ ] No embarrassing bookmarks visible
- [ ] No personal tabs open

**Personal Prep:**
- [ ] Review opening statement (30 seconds)
- [ ] Review closing statement
- [ ] Quick mental walkthrough of flow
- [ ] Deep breath - you've got this!

**Backup Plan Ready:**
- [ ] Screen recording queued (if demo fails)
- [ ] Screenshots folder bookmarked
- [ ] IT contact number in phone
- [ ] Backup presenter notified

---

## T-Minus 0 (Demo Time!)

### Opening (0-2 min) ✓ TARGET: 2 min

- [ ] Welcome everyone
- [ ] Thank attendees for coming
- [ ] State objectives clearly
- [ ] Set expectations (30 min demo + 15 min Q&A)
- [ ] Encourage questions

**Opening Line:**
> "Good morning! Today I'll show you the AR Control Hub - our new system that prioritizes collections automatically and forecasts cash flow 8 weeks ahead."

---

### Part 1: Dashboard (2-6 min) ✓ TARGET: 6 min

**Tab 1: Sarah Martinez - Dashboard**

- [ ] Point to Total AR: $1,247,850
- [ ] Show aging buckets breakdown
- [ ] Point to DSO: 37.5 days (trending down)
- [ ] Click "12 Active Alerts" → show blinking critical
- [ ] Return to dashboard

**Key Talking Point:** "Everything in one view - no more digging through Epicor reports"

---

### Part 2: Worklist (6-12 min) ✓ TARGET: 12 min

**Tab 1: Sarah Martinez - Worklist**

- [ ] Show auto-sorted by risk score
- [ ] Point to top customer (Acme Corp - $45k overdue)
- [ ] Explain risk factors
- [ ] Click Acme Corp → Customer 360

**Key Talking Point:** "Save 2+ hours/day on manual prioritization"

---

### Part 3: Customer 360 (12-17 min) ✓ TARGET: 17 min

**Tab 1: Sarah Martinez - Customer 360 (Acme Corp)**

- [ ] Summary card (credit limit, balance, DSO)
- [ ] Invoices tab (5 open invoices)
- [ ] Payment history (last payment 47 days ago)
- [ ] Alerts (2 active: aging, broken promise)
- [ ] Notes tab
- [ ] Tasks tab
- [ ] **LIVE ACTION:** Add note: "Called customer, promised payment by Friday"
- [ ] **LIVE ACTION:** Create task: "Follow up on Friday afternoon"
- [ ] Click Save

**WOW MOMENT:** "In 30 seconds I documented a call and set a reminder - used to take 5 minutes"

---

### Part 4: Cash Forecast (17-22 min) ✓ TARGET: 22 min

**Tab 2: Michael Chen - Cash Forecast**

- [ ] Show 8-week rolling forecast
- [ ] Point to Week 1: $87,450 expected
- [ ] Hover over bars (show tooltips)
- [ ] Scroll to table breakdown
- [ ] Point to accuracy indicator

**Key Talking Point:** "Answers: How much cash are we collecting this month?"

**Business Value:** "Helps CFO plan cash needs 8 weeks ahead"

---

### Part 5: DSO Analysis (22-25 min) ✓ TARGET: 25 min

**Tab 2: Michael Chen - DSO Analysis**

- [ ] Current DSO: 37.5 days (trending down from 39)
- [ ] Target DSO: 35 days
- [ ] Show trend line
- [ ] Scroll to problem accounts
- [ ] Click worst offender (95-day DSO) → Customer 360

**Business Impact:** "Every 1-day DSO reduction = $28k working capital freed"

---

### Part 6: Salesperson Portal (25-28 min) ✓ TARGET: 28 min

**Tab 3: Jessica Williams - Salesperson Portal**

- [ ] Show Jessica's 12 customers only
- [ ] Total AR for her: $187,250
- [ ] 3 customers with alerts
- [ ] Click one customer → show limited view
- [ ] Log back out

**Key Talking Point:** "Empowers sales to help with collections proactively"

---

### Closing & Business Value (28-30 min) ✓ TARGET: 30 min

- [ ] Summarize key benefits (5 bullet points)
- [ ] Restate business impact: **$172,000 annual value**
- [ ] DSO target: 37.5 → 35 days = $56k working capital
- [ ] Time savings: 2+ hrs/day = 500 hrs/year
- [ ] Next steps:
  - [ ] Today: Gather feedback
  - [ ] Week 3: UAT (2 weeks)
  - [ ] Week 5-7: Training
  - [ ] Week 8: Go-Live

---

### Q&A (30-45 min) ✓ TARGET: 45 min

- [ ] Open for questions
- [ ] Refer to prepared Q&A in DEMO_QUICK_REFERENCE.md
- [ ] Take notes of questions for documentation
- [ ] Answer with confidence
- [ ] If unsure: "Great question - let me follow up with details"

---

## Immediately After Demo

**Wrap-Up:**
- [ ] Thank everyone for their time
- [ ] Collect feedback forms
- [ ] Collect UAT signup sheet
- [ ] Answer remaining questions
- [ ] Exchange contact info
- [ ] Note who seemed most engaged

**Technical Cleanup:**
- [ ] Stop screen recording
- [ ] Save recording with clear filename
- [ ] Don't shut down servers yet (people may want to try)

---

## Post-Demo (Within 24 Hours)

**Follow-Up:**
- [ ] Send thank-you email to all attendees
- [ ] Share demo recording link
- [ ] Send feature summary PDF to those who missed handout
- [ ] Schedule UAT kickoff with volunteers
- [ ] Create Slack/Teams channel for Q&A
- [ ] Document all questions asked
- [ ] Document all feedback received

**Debrief:**
- [ ] Personal reflection: What went well?
- [ ] What could be improved?
- [ ] Were there unexpected questions?
- [ ] Did timing work out?
- [ ] Any technical issues?
- [ ] Update demo script based on experience

---

## Emergency Procedures

### If Backend Crashes During Demo:
1. **Don't panic** - smile at audience
2. Say: "Let me check something real quick"
3. Attempt quick restart:
   ```bash
   pkill -f "uvicorn src.api.main:app"
   uvicorn src.api.main:app --reload
   ```
4. If not fixed in 2 minutes:
   - Switch to backup screen recording
   - Say: "Let me show you a recording while we troubleshoot"
5. Continue with confidence

### If Projector Fails:
1. Ask: "Can everyone see on my laptop screen?"
2. If yes: Move laptop to center, people gather around
3. If no: Use backup screen recording on someone else's laptop
4. Last resort: Whiteboard walkthrough (you know this cold!)

### If Data Looks Wrong:
1. Don't apologize profusely
2. Say: "This is demo data - in production you'll see your real AR"
3. Verbally describe what SHOULD be shown
4. Continue with other working sections

### If Running Long (Past 30 Minutes):
1. Check clock at 20-min mark
2. If behind: Skip Salesperson Portal
3. Fast-forward through DSO (just show the number)
4. Keep Customer 360 and Cash Forecast (highest value)
5. Extend Q&A time instead

### If Running Short (Finished at 20 Minutes):
1. Ask: "Would you like to see more details on any feature?"
2. Demonstrate filtering/sorting
3. Show API documentation (http://localhost:8000/docs)
4. Open for Q&A early
5. Show advanced features (user management, settings)

---

## Success Metrics

**Audience Engagement Indicators:**
- ✅ Leaning forward, taking notes
- ✅ Asking clarifying questions
- ✅ Nodding, smiling
- ✅ "Wow" or "That's cool" comments
- ✅ Discussion about their own use cases

**Red Flags:**
- ⚠️ Blank stares, no questions
- ⚠️ Checking phones/laptops
- ⚠️ Side conversations unrelated to demo
- ⚠️ People leaving early
- **Action:** Pause and ask "Does this make sense?" or "What questions do you have?"

**Minimum Success Criteria:**
- [ ] Demo completed without major crashes
- [ ] All key features shown (Dashboard, Worklist, Customer 360, Cash Forecast)
- [ ] At least 3 questions asked (shows engagement)
- [ ] At least 3 UAT volunteers signed up
- [ ] Majority positive feedback

**Ideal Success Criteria:**
- [ ] Demo ran smoothly, no technical issues
- [ ] "Wow moments" landed well (blinking alerts, 30-sec note/task creation)
- [ ] 5+ UAT volunteers signed up
- [ ] Enthusiastic positive feedback
- [ ] Executive sponsorship secured
- [ ] Go-live date approved

---

## Presenter Mindset

**Before Demo:**
- ✅ "I've prepared thoroughly"
- ✅ "I know this system inside and out"
- ✅ "This will help the team succeed"
- ✅ "Even if something goes wrong, I have backups"

**During Demo:**
- ✅ Speak slowly and clearly
- ✅ Make eye contact with audience
- ✅ Point cursor to what you're discussing
- ✅ Pause after key points
- ✅ Use specific numbers
- ✅ Tell stories, not just features
- ✅ Stay positive and enthusiastic

**If Something Goes Wrong:**
- ✅ Stay calm - take a breath
- ✅ Smile at audience
- ✅ Use backup plan quickly
- ✅ Don't apologize excessively
- ✅ Turn it positive: "This is why we do UAT!"

**Confidence Mantra:**
*"I built an amazing system. The demo is just showing people what they'll love using every day."*

---

## Demo URLs (Bookmark These)

```
Main Demo (Sarah):    http://localhost:3000/dashboard
Worklist:             http://localhost:3000/worklist
Customer Detail:      [Click from worklist]
Analytics (Michael):  http://localhost:3000/analytics/cash-forecast
DSO:                  http://localhost:3000/analytics/dso
Sales Portal:         http://localhost:3000/salesperson

Backend Health:       http://localhost:8000/health
API Docs:             http://localhost:8000/docs
```

---

## Key Numbers to Memorize

- **Total AR:** $1,247,850
- **Current DSO:** 37.5 days
- **Target DSO:** 35 days
- **Active Alerts:** 12
- **Customers:** 50
- **Invoices:** 200+
- **Week 1 Forecast:** $87,450
- **Annual Value:** $172,000
- **Time Savings:** 2+ hrs/day = 500 hrs/year
- **Working Capital:** $56k freed (from DSO improvement)

---

**You've got this! Go show them what you built! 🚀**

**Remember:** Confidence comes from preparation. You've prepared. Now execute.

---

**Post-Demo Reflection:**

What went well:
_________________________________
_________________________________
_________________________________

What to improve:
_________________________________
_________________________________
_________________________________

Unexpected questions:
_________________________________
_________________________________
_________________________________
