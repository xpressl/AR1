# AR Control Hub - Pre-Demo Checklist

**Demo Date:** ________________
**Demo Time:** ________________
**Location:** ________________
**Expected Attendees:** ______

---

## 1 Week Before Demo

### Schedule & Invitations
- [ ] Send demo invitation email to all stakeholders
  - [ ] AR Team (Sarah Martinez, etc.)
  - [ ] Finance Leadership (CFO, VPs)
  - [ ] IT Management
  - [ ] Sales Managers (Jessica Williams, etc.)
- [ ] Reserve conference room (or create Zoom meeting)
- [ ] Add to calendars with reminder
- [ ] Request RSVP by [date]
- [ ] Book backup conference room (in case of conflicts)

### Environment Setup
- [ ] Set up demo database (separate from production)
- [ ] Run database migrations
- [ ] Generate demo data (`python scripts/seed_demo_data.py --scenario demo`)
- [ ] Verify all 3 demo user accounts work:
  - [ ] sarah.martinez@company.com / demo123
  - [ ] michael.chen@company.com / demo123
  - [ ] admin@company.com / demo123
- [ ] Test all major features work correctly
- [ ] Clear browser cache/cookies
- [ ] Bookmark key pages for quick navigation

### Materials Preparation
- [ ] Print feature summary handouts (1 per attendee + 5 extra)
- [ ] Print demo script for presenter reference
- [ ] Create feedback forms (physical or digital)
- [ ] Prepare UAT signup sheet
- [ ] Create backup screen recording (in case live demo fails)

### Technical Setup
- [ ] Test laptop connects to projector/screen
- [ ] Verify internet connection stable
- [ ] Test Zoom/video conferencing (if remote attendees)
- [ ] Charge laptop fully
- [ ] Bring power adapter
- [ ] Have backup laptop ready (if possible)

### Presentation Prep
- [ ] Review DEMO_GUIDE.md script thoroughly
- [ ] Practice 30-minute walkthrough at least twice
- [ ] Time each section to stay on schedule
- [ ] Rehearse Q&A responses (review 14 prepared questions)
- [ ] Identify 3 "wow moments" to emphasize
- [ ] Prepare backup talking points if demo runs short

---

## 1 Day Before Demo

### Final Environment Check
- [ ] Run `./scripts/setup_demo_environment.sh`
- [ ] Verify backend server running: http://localhost:8000/health
- [ ] Verify frontend running: http://localhost:3000
- [ ] Log in to each demo account and test
- [ ] Navigate through all demo sections successfully
- [ ] Verify sample data looks realistic and current
- [ ] Check blinking alerts are working (visual impact!)

### Technical Prep
- [ ] Test projector connection one more time
- [ ] Set screen resolution to match projector (usually 1920x1080)
- [ ] Close all unnecessary browser tabs
- [ ] Disable browser notifications
- [ ] Disable email/Slack/Teams notifications
- [ ] Silence phone
- [ ] Prepare "Do Not Disturb" sign for door

### Materials Check
- [ ] Count printed handouts (enough for everyone?)
- [ ] Organize handouts for easy distribution
- [ ] Bring extra pens/pencils
- [ ] Prepare name tags (if large group)
- [ ] Have water/coffee available

### Final Walkthrough
- [ ] Do complete 30-minute run-through
- [ ] Practice with timer to verify timing
- [ ] Review Q&A one more time
- [ ] Prepare opening statement (first 30 seconds memorized)
- [ ] Prepare closing statement with clear next steps

### Communication
- [ ] Send reminder email to all attendees
- [ ] Confirm conference room reservation
- [ ] Notify IT of demo (in case support needed)
- [ ] Alert security if external attendees

---

## 1 Hour Before Demo

### Room Setup
- [ ] Arrive early (at least 30 minutes before)
- [ ] Set up projector/screen
- [ ] Connect laptop and test display
- [ ] Test audio (if presenting remotely)
- [ ] Arrange chairs for good visibility
- [ ] Place handouts at each seat
- [ ] Set up feedback form station
- [ ] Have water available

### Technical Final Check
- [ ] Open browser with demo environment
- [ ] Log in to all 3 demo accounts (in separate tabs)
- [ ] Navigate to each major page once (warm up cache)
- [ ] Verify data still looks good
- [ ] Close unnecessary tabs
- [ ] Full screen mode ready

### Personal Prep
- [ ] Review opening and closing statements
- [ ] Quick mental walkthrough of demo flow
- [ ] Deep breath - you've got this! 😊
- [ ] Positive mindset: "This will help the team"

### Contingency Prep
- [ ] Have backup screen recording queued up
- [ ] Know how to quickly restart servers if needed
- [ ] Have IT contact on speed dial
- [ ] Prepared to present without demo if technical issues
- [ ] Backup talking points ready

---

## During Demo

### Opening (0-2 minutes)
- [ ] Welcome everyone and thank them for attending
- [ ] Quick introductions if needed
- [ ] State demo objectives clearly
- [ ] Set expectations (30 min demo + 15 min Q&A)
- [ ] Encourage questions during demo

### Demo Execution (2-28 minutes)
- [ ] Follow DEMO_GUIDE.md script
- [ ] Speak slowly and clearly
- [ ] Point cursor to what you're discussing
- [ ] Highlight specific numbers and metrics
- [ ] Show blinking alerts (visual impact)
- [ ] Demonstrate quick actions (add note, create task)
- [ ] Use realistic scenarios from sample data
- [ ] Stay on time (glance at clock periodically)

### Engagement
- [ ] Make eye contact with attendees
- [ ] Read the room (are they engaged? confused?)
- [ ] Pause for questions after each section
- [ ] Call on specific people if appropriate
- [ ] Note questions to address later if short on time

### Closing (28-30 minutes)
- [ ] Summarize key benefits
- [ ] Restate business value ($172k annual)
- [ ] Clearly state next steps
- [ ] Open for Q&A
- [ ] Distribute feedback forms
- [ ] Pass around UAT signup sheet

---

## Immediately After Demo

### Wrap-Up
- [ ] Thank everyone for their time
- [ ] Collect feedback forms
- [ ] Collect UAT signup sheet
- [ ] Answer any remaining questions
- [ ] Exchange contact info with interested parties
- [ ] Take note of who seemed most engaged

### Follow-Up
- [ ] Send thank-you email within 24 hours
- [ ] Share demo recording link
- [ ] Send feature summary PDF to those who missed it
- [ ] Schedule UAT kickoff meeting with volunteers
- [ ] Create Slack/Teams channel for Q&A
- [ ] Document all questions asked
- [ ] Document all feedback received

### Debrief
- [ ] Personal reflection: What went well?
- [ ] What could be improved for next presentation?
- [ ] Were there any unexpected questions?
- [ ] Did timing work out as planned?
- [ ] Note any technical issues encountered
- [ ] Update demo script based on experience

---

## Within 1 Week After Demo

### Communication
- [ ] Send detailed meeting notes to all attendees
- [ ] Share action items with responsible parties
- [ ] Schedule UAT kickoff (Week 3)
- [ ] Schedule training sessions (Weeks 5-7)
- [ ] Set tentative go-live date (Week 8)

### Planning
- [ ] Incorporate feedback into system (if quick fixes)
- [ ] Prepare UAT test scenarios
- [ ] Create UAT environment
- [ ] Finalize training materials
- [ ] Update project timeline based on feedback

### Metrics
- [ ] Count number of attendees
- [ ] Calculate feedback score average
- [ ] Count UAT volunteers
- [ ] Document stakeholder buy-in level
- [ ] Report success metrics to leadership

---

## Demo Success Criteria

**Minimum Success:**
- [ ] Demo completed without major technical issues
- [ ] All attendees saw key features
- [ ] Questions answered satisfactorily
- [ ] At least 3 UAT volunteers signed up
- [ ] Positive feedback from majority

**Ideal Success:**
- [ ] Demo ran smoothly with no technical issues
- [ ] Attendees engaged and asked questions
- [ ] "Wow moments" landed well (blinking alerts, cash forecast, DSO)
- [ ] 5+ UAT volunteers signed up
- [ ] Enthusiastic positive feedback
- [ ] Executive sponsorship secured
- [ ] Go-live date approved

---

## Emergency Contacts

**Technical Support:**
- IT Help Desk: ext. [____]
- Database Admin: [Name] - [Phone]
- Network Support: [Name] - [Phone]

**Project Team:**
- Project Lead: [Your Name] - [Phone]
- AR Manager: Michael Chen - [Phone]
- Backup Presenter: [Name] - [Phone]

---

## Notes Section

**Things that went well:**
_____________________________________
_____________________________________
_____________________________________

**Things to improve:**
_____________________________________
_____________________________________
_____________________________________

**Unexpected questions:**
_____________________________________
_____________________________________
_____________________________________

**Follow-up items:**
_____________________________________
_____________________________________
_____________________________________

---

**Remember:** You've built an amazing system. The demo is just showing people what they'll love using every day!

**Confidence comes from preparation. You've got this! 🚀**
