# AR Control Hub - Demo Troubleshooting Guide

**Keep this handy during demo preparation and execution.**

---

## Before the Demo

### Issue: Setup Script Fails

**Symptom:** `./scripts/setup_demo_environment.sh` exits with errors

**Diagnosis Steps:**
```bash
# Check if you're in the correct directory
pwd  # Should show /home/user/AR1 (or your project root)

# Check if script is executable
ls -la scripts/setup_demo_environment.sh

# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check if required ports are available
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port
```

**Solutions:**

1. **Permission Denied:**
   ```bash
   chmod +x scripts/setup_demo_environment.sh
   ./scripts/setup_demo_environment.sh
   ```

2. **PostgreSQL Not Running:**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start postgresql
   sudo systemctl status postgresql

   # macOS
   brew services start postgresql
   ```

3. **Port Already in Use:**
   ```bash
   # Kill existing processes
   pkill -f "uvicorn src.api.main:app"
   pkill -f "npm.*dev"

   # Or change ports in .env file
   API_PORT=8001
   NEXT_PUBLIC_API_URL=http://localhost:8001
   ```

4. **Database 'ar_demo' Doesn't Exist:**
   ```bash
   psql -U postgres -c "CREATE DATABASE ar_demo;"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ar_demo TO ar_user;"
   ```

5. **Faker Not Installed:**
   ```bash
   pip install faker
   ```

---

### Issue: Demo Data Not Generating

**Symptom:** `python scripts/seed_demo_data.py --scenario demo` fails

**Diagnosis:**
```bash
# Check if database is accessible
psql -d ar_demo -U ar_user -c "SELECT COUNT(*) FROM customers;"

# Check if migrations have run
alembic current

# Check if all Python dependencies installed
pip list | grep -E "faker|sqlalchemy|asyncpg"
```

**Solutions:**

1. **No Module Named 'faker':**
   ```bash
   pip install faker
   ```

2. **Database Connection Error:**
   ```bash
   # Check DATABASE_URL in .env or environment
   echo $DATABASE_URL

   # Should be:
   export DATABASE_URL="postgresql+asyncpg://ar_user:ar_dev_password@localhost:5432/ar_demo"
   ```

3. **Tables Don't Exist:**
   ```bash
   # Run migrations
   alembic upgrade head

   # Verify tables created
   psql -d ar_demo -c "\dt"
   ```

4. **Seed Script Hangs:**
   - Check for database locks: `SELECT * FROM pg_locks;`
   - Kill any blocking processes
   - Clear demo database and start fresh:
     ```bash
     psql -U postgres -c "DROP DATABASE ar_demo;"
     psql -U postgres -c "CREATE DATABASE ar_demo;"
     alembic upgrade head
     python scripts/seed_demo_data.py --scenario demo
     ```

---

### Issue: Can't Log In to Demo Accounts

**Symptom:** Login fails with "Invalid credentials"

**Diagnosis:**
```bash
# Check if users exist in database
psql -d ar_demo -c "SELECT email, role FROM users;"

# Should show at least:
# sarah.martinez@company.com | ar_specialist
# michael.chen@company.com    | ar_manager
# admin@company.com           | admin
```

**Solutions:**

1. **Users Not Created:**
   ```bash
   # Re-run seed script (it creates users)
   python scripts/seed_demo_data.py --scenario demo
   ```

2. **Password Hash Issue:**
   ```python
   # Create users manually via Python
   python -c "
   import asyncio
   from passlib.context import CryptContext
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from src.models import User

   async def create_user():
       engine = create_async_engine('postgresql+asyncpg://ar_user:ar_dev_password@localhost:5432/ar_demo')
       async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

       pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

       async with async_session() as session:
           user = User(
               email='sarah.martinez@company.com',
               username='sarah.martinez',
               hashed_password=pwd_context.hash('demo123'),
               role='ar_specialist',
               full_name='Sarah Martinez',
               is_active=True
           )
           session.add(user)
           await session.commit()
           print('User created successfully')

   asyncio.run(create_user())
   "
   ```

3. **Wrong Password:**
   - All demo accounts use password: `demo123`
   - Case-sensitive, no spaces
   - Try copy-paste to avoid typos

---

## During the Demo

### Issue: Backend API Not Responding

**Symptom:** Dashboard shows loading spinner indefinitely, or "Network Error"

**Diagnosis:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status": "healthy"}

# Check backend logs
tail -50 logs/demo_backend.log

# Check if process is running
ps aux | grep uvicorn
```

**Solutions:**

1. **Backend Crashed:**
   ```bash
   # Restart backend
   pkill -f "uvicorn src.api.main:app"
   nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/demo_backend.log 2>&1 &

   # Wait 3 seconds
   sleep 3

   # Verify it's running
   curl http://localhost:8000/health
   ```

2. **Database Connection Lost:**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql

   # If down, restart
   sudo systemctl start postgresql

   # Then restart backend (see above)
   ```

3. **CORS Error in Browser Console:**
   - Check .env file has correct CORS_ORIGINS
   - Should include: `CORS_ORIGINS=http://localhost:3000,http://localhost:3001`
   - Restart backend after changing .env

**Quick Fallback:**
- If backend won't start during demo, use backup screen recording
- Apologize: "Let me show you a quick recording while we troubleshoot"
- Have IT contact on speed dial

---

### Issue: Frontend Page Won't Load

**Symptom:** White screen, or "This site can't be reached"

**Diagnosis:**
```bash
# Check if frontend is running
curl http://localhost:3000

# Check frontend logs
tail -50 logs/demo_frontend.log

# Check if process is running
ps aux | grep "npm.*dev"
```

**Solutions:**

1. **Frontend Not Running:**
   ```bash
   cd /home/user/AR1  # Or your project root
   pkill -f "npm.*dev"
   nohup npm run dev > logs/demo_frontend.log 2>&1 &

   # Wait 5 seconds
   sleep 5

   # Verify
   curl http://localhost:3000
   ```

2. **Node Modules Missing:**
   ```bash
   npm install
   npm run dev
   ```

3. **Port 3000 In Use:**
   ```bash
   # Kill existing process
   lsof -ti:3000 | xargs kill -9

   # Or use different port
   PORT=3001 npm run dev
   ```

4. **Build Errors:**
   ```bash
   # Check logs for errors
   cat logs/demo_frontend.log

   # Common fix: clear cache and rebuild
   rm -rf .next
   npm run dev
   ```

**Quick Fallback:**
- Use screenshots from docs/screenshots/ folder
- Walk through features using images
- Schedule follow-up demo once issue resolved

---

### Issue: Dashboard Shows No Data

**Symptom:** Dashboard loads but shows $0 AR, 0 customers, empty charts

**Diagnosis:**
```bash
# Check if data exists in database
psql -d ar_demo -c "SELECT COUNT(*) FROM customers;"
psql -d ar_demo -c "SELECT COUNT(*) FROM invoices;"
psql -d ar_demo -c "SELECT SUM(open_balance) FROM invoices WHERE status = 'Open';"

# Should show:
# Customers: 50
# Invoices: 200+
# Total AR: 1200000+ (around $1.2M)
```

**Solutions:**

1. **No Data in Database:**
   ```bash
   # Re-seed demo data
   python scripts/seed_demo_data.py --scenario demo

   # Refresh browser (Ctrl+R or Cmd+R)
   ```

2. **Wrong Database Connected:**
   ```bash
   # Check DATABASE_URL
   echo $DATABASE_URL

   # Should point to ar_demo, not ar_dev or ar_prod
   export DATABASE_URL="postgresql+asyncpg://ar_user:ar_dev_password@localhost:5432/ar_demo"

   # Restart backend
   pkill -f "uvicorn src.api.main:app"
   uvicorn src.api.main:app --reload
   ```

3. **API Endpoint Returning Empty:**
   ```bash
   # Test API directly
   curl http://localhost:8000/api/v1/dashboard/summary

   # Should return JSON with non-zero values
   ```

4. **Frontend Caching Old Data:**
   - Clear browser cache (Ctrl+Shift+Del)
   - Hard reload (Ctrl+Shift+R or Cmd+Shift+R)
   - Try incognito/private window

---

### Issue: Blinking Alerts Not Blinking

**Symptom:** Critical alerts show as red text but don't blink/animate

**Diagnosis:**
```bash
# Open browser console (F12)
# Look for JavaScript errors
# Check if CSS animations are disabled
```

**Solutions:**

1. **Browser Animation Settings:**
   - Check if user has "prefers-reduced-motion" enabled
   - Test in different browser (Chrome, Firefox, Safari)

2. **CSS Not Loading:**
   - Hard reload page (Ctrl+Shift+R)
   - Check Network tab in DevTools for 404s

3. **Tailwind CSS Issue:**
   ```bash
   # Rebuild frontend
   cd frontend
   npm run build
   npm run dev
   ```

**Quick Fallback:**
- Point out red alerts verbally: "These critical alerts would normally be blinking"
- Emphasize severity with words: "CRITICAL - needs immediate attention"
- Move on, not a deal-breaker

---

### Issue: Customer 360 Page Crashes

**Symptom:** Clicking customer from worklist causes error or blank page

**Diagnosis:**
```bash
# Check backend logs for errors
tail -100 logs/demo_backend.log | grep ERROR

# Check browser console (F12) for JavaScript errors

# Test API endpoint directly
curl http://localhost:8000/api/v1/customers/[customer-id]
```

**Solutions:**

1. **Invalid Customer ID:**
   - Go back to worklist
   - Click different customer
   - Ensure URL has valid UUID or integer ID

2. **Missing Data:**
   ```bash
   # Check if customer exists
   psql -d ar_demo -c "SELECT * FROM customers WHERE id = 'customer-id';"

   # Check related data
   psql -d ar_demo -c "SELECT COUNT(*) FROM invoices WHERE customer_id = 'customer-id';"
   ```

3. **API Error:**
   - Check backend logs for stack trace
   - Common issue: missing relationship data
   - Restart backend as temporary fix

**Quick Fallback:**
- Use different customer (Acme Corp is usually safe bet)
- Verbally describe what would be shown
- "Let me show you another example..."

---

### Issue: Can't Add Notes or Tasks

**Symptom:** Clicking "Save" on new note/task does nothing or shows error

**Diagnosis:**
```bash
# Check browser console for errors
# Check Network tab - look for 400/500 status codes

# Test API endpoint
curl -X POST http://localhost:8000/api/v1/customers/[id]/notes \
  -H "Content-Type: application/json" \
  -d '{"content": "Test note", "note_type": "call"}'
```

**Solutions:**

1. **Authentication Issue:**
   - Log out and log back in
   - Check browser has auth token (check Local Storage in DevTools)

2. **Validation Error:**
   - Ensure all required fields filled
   - Check character limits
   - Note type must be one of: call, email, meeting, general

3. **Database Write Error:**
   - Check backend logs
   - Verify database not in read-only mode
   - Check disk space: `df -h`

**Quick Fallback:**
- Say: "In production this would save - let me show you the note appears in the list"
- Move on to showing existing notes
- Emphasize the feature verbally even if save fails

---

### Issue: Charts Not Rendering

**Symptom:** Cash forecast or DSO page shows empty space where charts should be

**Diagnosis:**
```bash
# Check browser console (F12) for JavaScript errors
# Check if Chart.js loaded (Network tab)
# Test with different browser
```

**Solutions:**

1. **JavaScript Library Not Loaded:**
   - Hard reload (Ctrl+Shift+R)
   - Clear cache and reload
   - Check frontend logs for build errors

2. **No Data for Charts:**
   ```bash
   # Check if forecast data exists
   curl http://localhost:8000/api/v1/analytics/cash-forecast

   # Should return array of weekly forecasts
   ```

3. **Responsive Design Issue:**
   - Zoom out (Ctrl+Minus)
   - Make window wider
   - F11 for full-screen mode

**Quick Fallback:**
- Use screenshot from docs folder
- Draw chart on whiteboard
- Verbally describe trend: "This chart would show increasing collections over next 8 weeks"

---

### Issue: Salesperson Portal Shows All Customers

**Symptom:** Jessica Williams sees customers not assigned to her

**Diagnosis:**
```bash
# Check salesperson assignments
psql -d ar_demo -c "SELECT name, salesperson_id FROM customers WHERE salesperson_id = 'jessica.williams';"

# Check API endpoint
curl http://localhost:8000/api/v1/salesperson/customers \
  -H "X-Salesperson-ID: jessica.williams"
```

**Solutions:**

1. **Authorization Bug:**
   - This is a code issue
   - Not fixable during demo
   - Verbally explain: "Portal filters to only Jessica's customers"

2. **Missing Header:**
   - Check if frontend sending X-Salesperson-ID header
   - Log out and log back in

3. **Database Assignment Issue:**
   ```bash
   # Verify Jessica has customers assigned
   psql -d ar_demo -c "SELECT COUNT(*) FROM customers WHERE salesperson_id = 'jessica.williams';"

   # If 0, assign some:
   psql -d ar_demo -c "UPDATE customers SET salesperson_id = 'jessica.williams' WHERE id IN (SELECT id FROM customers LIMIT 12);"
   ```

---

### Issue: Projector Display Issues

**Symptom:** Screen looks fine on laptop but wrong on projector

**Solutions:**

1. **Resolution Mismatch:**
   - Set laptop display to 1920x1080 (most common projector resolution)
   - Windows: Settings → Display → Resolution
   - Mac: System Preferences → Displays → Scaled

2. **Duplicate vs Extend Display:**
   - Use **Duplicate** mode (same content on both screens)
   - Windows: Win+P → Duplicate
   - Mac: System Preferences → Displays → Arrangement → Mirror Displays

3. **Colors Look Washed Out:**
   - Adjust projector brightness/contrast
   - Increase font size in browser (Ctrl+Plus)
   - Use high contrast mode if available

4. **Text Too Small:**
   - Zoom browser to 125% or 150% (Ctrl+Plus)
   - Increase system font size
   - Sit closer to screen yourself so you can read

---

### Issue: Demo Running Long

**Symptom:** Already at 20 minutes but only finished Customer 360 section

**Solutions:**

1. **Speed Up:**
   - Skip deep-dives, hit highlights only
   - Say: "I'll show you the quick version of this..."
   - Combine sections (show Cash Forecast and DSO together)

2. **Cut Sections:**
   - Skip Salesperson Portal (least critical)
   - Mention it exists but don't demonstrate
   - Focus on highest-value features (Dashboard, Worklist, Customer 360)

3. **Extend Q&A Time:**
   - "Let me show you one more feature quickly, then we'll open for questions"
   - Take questions during demo instead of at end

---

### Issue: Demo Running Short

**Symptom:** Already at 20 minutes and finished all sections

**Solutions:**

1. **Add Depth:**
   - Show more customers in Customer 360
   - Demonstrate filtering and sorting features
   - Add more notes and tasks live
   - Show API documentation (http://localhost:8000/docs)

2. **Open Q&A Early:**
   - "We have extra time - what questions do you have?"
   - Refer to prepared Q&A in DEMO_QUICK_REFERENCE.md

3. **Show Advanced Features:**
   - User management (creating new users)
   - Settings and configuration
   - Reports and exports (if implemented)

---

## After Demo Issues

### Issue: Can't Stop Servers

**Symptom:** `pkill` commands not working, servers still running

**Solutions:**

```bash
# Find process IDs
ps aux | grep uvicorn
ps aux | grep "npm.*dev"

# Kill by PID
kill -9 [PID]

# Nuclear option (kills all matching processes)
killall -9 uvicorn
killall -9 node

# Verify stopped
lsof -i :8000  # Should return nothing
lsof -i :3000  # Should return nothing
```

---

### Issue: Demo Recording Didn't Save

**Symptom:** Screen recording failed or corrupted

**Solutions:**

1. **OBS/QuickTime/Other Recorder:**
   - Check default save location
   - Search for .mp4 or .mov files created today

2. **Backup Plan:**
   - Do a quick 5-minute re-record of key highlights
   - Use screen recording from pre-demo practice session
   - Send written summary instead with screenshots

3. **Next Time:**
   - Test recording BEFORE demo
   - Record to external drive (faster write speed)
   - Use cloud recording (Zoom, Teams) as backup

---

### Issue: Attendees Want Access Now

**Symptom:** "Can I log in and try it today?"

**Response:**

**Positive But Controlled:**
> "I love your enthusiasm! The system is currently set up with demo data, not your real AR data.
>
> Here's the plan:
> 1. Week 3: We'll set up UAT environment with real data
> 2. You'll get login credentials for testing
> 3. We'll incorporate your feedback before go-live
>
> I'll send you the demo recording and feature summary today so you can review. Sound good?"

**If Insistent:**
- Give them demo account: sarah.martinez@company.com / demo123
- Warn that data is fake and will be wiped
- Set expectation: "This is a sandbox - your real system comes in Week 8"

---

## Emergency Contacts

**During Demo - Quick Reference:**

| Issue | Contact | Number | Notes |
|-------|---------|--------|-------|
| Projector not working | AV Support | ext. ____ | Usually in building services |
| Internet down | IT Helpdesk | ext. ____ | Have mobile hotspot as backup |
| Database crash | Database Admin | [Phone] | Escalate immediately |
| Can't find conference room | Reception | ext. ____ | Have backup room reserved |

**Escalation Path:**
1. Try to fix yourself (use this guide)
2. Call IT Helpdesk (for infrastructure issues)
3. Call Database Admin (for data issues)
4. Call backup presenter (if you need to step away)

---

## Prevention Checklist

**Do These 1 Day Before:**

- [ ] Run `./scripts/setup_demo_environment.sh` completely
- [ ] Test login to all 3 demo accounts
- [ ] Navigate to every major page successfully
- [ ] Add a test note and task (verify save works)
- [ ] Test on actual projector/screen you'll use
- [ ] Record backup screen capture
- [ ] Print this troubleshooting guide
- [ ] Have IT contact numbers saved in phone

**Do These 1 Hour Before:**

- [ ] Restart laptop (fresh start)
- [ ] Run setup script again (ensure clean state)
- [ ] Test backend: `curl http://localhost:8000/health`
- [ ] Test frontend: Open http://localhost:3000 in browser
- [ ] Close all unnecessary applications
- [ ] Disable notifications (email, Slack, etc.)
- [ ] Connect to projector and test display
- [ ] Have this guide open in second window

---

## Recovery Mantras

**When Something Goes Wrong:**

1. **Stay Calm**
   - Take a breath
   - Smile at audience
   - Say: "Let me check something real quick"

2. **Use Fallbacks**
   - Screenshots
   - Backup recording
   - Whiteboard explanation
   - Verbal walkthrough

3. **Be Honest**
   - "Looks like we have a technical hiccup"
   - "This is exactly why we do UAT!"
   - "In production this would work, let me show you a recording"

4. **Keep Momentum**
   - Don't spend >2 minutes troubleshooting
   - Move to backup plan quickly
   - Offer to show working version later

5. **Turn It Positive**
   - "Great question - this shows how we'll handle errors in production"
   - "Good thing we caught this now, not during go-live!"
   - "This is why your feedback during UAT is so valuable"

---

**Remember:** Even professional demos have hiccups. Your preparation and recovery matter more than perfection!

**The show must go on!** 🎭🚀
