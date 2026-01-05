# 🔧 TROUBLESHOOTING GUIDE - Django Container Issues

## ❌ Issue: Django Module Not Found

**Symptoms:**
- `ModuleNotFoundError: No module named 'django'`
- `docker compose logs web --tail 20` returns no output
- Container crashes immediately after starting

---

## 🎯 SOLUTION: Complete Container Rebuild

### Step 1: Clean Everything
```powershell
# Stop and remove all containers, networks, volumes
docker compose down -v

# Remove the web image completely
docker rmi microfinance-mis-web
```

### Step 2: Verify Files Are Correct
```powershell
# Check requirements.txt exists and has content
type app\requirements.txt
```

**Expected Output:**
```
django
psycopg[binary]
dj-database-url
python-dateutil
openpyxl
reportlab
```

### Step 3: Check Docker Compose Configuration
```powershell
type docker-compose.yml
```

**Verify the `command:` line includes:**
```yaml
command: bash -lc "pip install --no-cache-dir -r requirements.txt && if [ ! -f manage.py ]; then django-admin startproject core .; fi && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

### Step 4: Rebuild from Scratch
```powershell
# Build without cache
docker compose build --no-cache

# Start containers
docker compose up -d
```

### Step 5: Watch Real-Time Logs
```powershell
# Follow logs to see what's happening
docker compose logs -f web
```

**Wait for these messages:**
```
✓ Collecting django
✓ Downloading django-X.X.X...
✓ Installing collected packages: django, psycopg, openpyxl, reportlab...
✓ Successfully installed django-X.X.X psycopg-X.X.X...
✓ Operations to perform:
✓ Applying contenttypes.0001_initial... OK
✓ Applying auth.0001_initial... OK
✓ Starting development server at http://0.0.0.0:8000/
✓ Watching for file changes with StatReloader
```

**Press Ctrl+C when you see "Watching for file changes"**

---

## 🔍 ALTERNATIVE SOLUTION: Use Dockerfile

If the above doesn't work, we can create a proper Dockerfile instead of using command-based installation.

### Create Dockerfile:
```powershell
# Create a new file in project root
New-Item -Path "Dockerfile" -ItemType File
```

Add this content to `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first (for better caching)
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

### Update docker-compose.yml:
Change the `web` service to:
```yaml
web:
  build: .
  working_dir: /app
  volumes:
    - ./app:/app
  ports:
    - "8000:8000"
  environment:
    DATABASE_URL: postgresql://microfinance:microfinance_password_change_me@db:5432/microfinance
  depends_on:
    - db
```

Then rebuild:
```powershell
docker compose down -v
docker compose up --build -d
docker compose logs -f web
```

---

## 🐛 DEBUGGING STEPS

### Check Container Status
```powershell
docker compose ps
```

**Expected:**
```
NAME                          STATUS
microfinance-mis-db-1         Up
microfinance-mis-web-1        Up
```

### Check if Container Is Running
```powershell
docker compose ps web
```

If STATUS shows "Exited" or "Restarting", the container is crashing.

### View Full Logs
```powershell
docker compose logs web
```

### Enter Running Container (if it stays up)
```powershell
docker compose exec web bash
```

Then inside container:
```bash
# Check Python version
python --version

# Check pip packages
pip list

# Try importing django
python -c "import django; print(django.VERSION)"

# Check requirements file
cat requirements.txt

# Manual install if needed
pip install -r requirements.txt
```

### Check Volume Mounts
```powershell
docker compose exec web ls -la /app
```

**Should show:**
- manage.py
- core/ directory
- requirements.txt
- Other app directories

---

## ⚡ QUICK FIX COMMANDS

**Full Clean Rebuild:**
```powershell
docker compose down -v
docker system prune -f
docker compose up --build -d --force-recreate
docker compose logs -f web
```

**Force Requirements Install:**
```powershell
docker compose exec web pip install -r requirements.txt
docker compose restart web
docker compose logs -f web
```

**Check for Port Conflicts:**
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# If something is using it, kill it or change docker-compose.yml ports to 8001:8000
```

---

## 📋 COMMON ISSUES & FIXES

### Issue 1: "No such file or directory: requirements.txt"
**Fix:**
```powershell
# Ensure requirements.txt is in app/ directory
dir app\requirements.txt

# If missing, recreate it
echo django > app\requirements.txt
echo psycopg[binary] >> app\requirements.txt
echo dj-database-url >> app\requirements.txt
echo python-dateutil >> app\requirements.txt
echo openpyxl >> app\requirements.txt
echo reportlab >> app\requirements.txt
```

### Issue 2: Database Connection Refused
**Fix:**
```powershell
# Wait for PostgreSQL to be ready
docker compose logs db

# Should see: "database system is ready to accept connections"

# If not, restart db first
docker compose restart db
Start-Sleep -Seconds 10
docker compose restart web
```

### Issue 3: Permission Denied
**Fix:**
```powershell
# On Windows, ensure Docker Desktop is running with proper permissions
# Run PowerShell as Administrator if needed

# Check Docker is accessible
docker ps
```

### Issue 4: Container Keeps Restarting
**Fix:**
```powershell
# Remove restart policy temporarily
docker compose down
# Edit docker-compose.yml, add under web service:
#   restart: "no"

docker compose up -d
docker compose logs web

# This will show the actual error before it restarts
```

---

## ✅ VERIFICATION CHECKLIST

After fixing, verify these work:

```powershell
# 1. Check both containers are up
docker compose ps

# 2. Check web logs show success
docker compose logs web --tail 30

# 3. Test Django is installed
docker compose exec web python -c "import django; print('Django OK')"

# 4. Test database connection
docker compose exec web python manage.py check

# 5. Access the site
Start-Process "http://localhost:8000/management/"
```

---

## 🆘 LAST RESORT: Complete Reset

If nothing works, start completely fresh:

```powershell
# 1. Stop everything
docker compose down -v

# 2. Remove all related images
docker rmi microfinance-mis-web
docker rmi postgres:16
docker rmi python:3.12-slim

# 3. Clean Docker system
docker system prune -a -f

# 4. Remove volumes
docker volume rm microfinance-mis_pgdata

# 5. Pull latest code
git pull origin genspark_ai_developer

# 6. Rebuild everything
docker compose up --build -d

# 7. Watch logs
docker compose logs -f web
```

---

## 📞 STILL HAVING ISSUES?

Run this diagnostic script and share output:

```powershell
Write-Host "=== Docker Version ===" -ForegroundColor Cyan
docker --version
docker compose version

Write-Host "`n=== Container Status ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Web Container Logs ===" -ForegroundColor Cyan
docker compose logs web

Write-Host "`n=== Requirements File ===" -ForegroundColor Cyan
type app\requirements.txt

Write-Host "`n=== Docker Compose Config ===" -ForegroundColor Cyan
docker compose config

Write-Host "`n=== Volume Contents ===" -ForegroundColor Cyan
docker compose exec web ls -la /app 2>&1
```

---

**Generated**: January 4, 2026  
**For**: Ghana Microfinance MIS Deployment
