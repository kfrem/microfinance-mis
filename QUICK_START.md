# Quick Start - Testing Audit Logging on Your Machine

## 🚀 TL;DR - Get Started in 5 Minutes

### Step 1: Get the Code
```bash
cd path/to/microfinance-mis
git pull origin main
# Or test the PR branch:
git checkout genspark_ai_developer
```

### Step 2: Start Docker
```bash
# Make sure Docker Desktop is running, then:
docker compose up --build
```

### Step 3: Create Admin User (First Time Only)
```bash
# In a new terminal:
docker compose exec web python manage.py createsuperuser
# Username: admin
# Password: (your choice)
```

### Step 4: Test It!
1. Open http://localhost:8000/admin/
2. Login with your credentials
3. Create a client, loan, or repayment
4. Go to http://localhost:8000/admin/audit/auditlog/
5. See your audit logs! 🎉

### Step 5: Verify (Optional)
```bash
# Check audit log count:
docker compose exec web python manage.py shell -c "from audit.models import AuditLog; print(f'Audit logs: {AuditLog.objects.count()}')"
```

## 🎯 What to Test

| Action | Where to Test | What to Verify |
|--------|---------------|----------------|
| **Create Client** | /admin/clients/client/add/ | Audit log shows CREATE |
| **Update Client** | Edit any client | Audit log shows UPDATE with changes |
| **Delete Client** | Delete any client | Audit log shows DELETE |
| **Create Loan** | /admin/loans/loan/add/ | Audit log shows CREATE |
| **Create Repayment** | /admin/repayments/repayment/add/ | Audit log shows CREATE |

## 📊 View Audit Logs

**In Browser**: http://localhost:8000/admin/audit/auditlog/

**In Terminal**:
```bash
docker compose exec web python manage.py shell -c "
from audit.models import AuditLog
for log in AuditLog.objects.all()[:5]:
    print(f'{log.action} | {log.model_name} | {log.object_repr} | by {log.user}')
"
```

## 🛑 Stop When Done
```bash
docker compose down
```

## 📚 Need More Details?
See **TESTING_GUIDE.md** for comprehensive testing instructions.

## ✅ Success Checklist

- [ ] Docker is running
- [ ] Application starts at http://localhost:8000
- [ ] Can login to admin
- [ ] Creating a client creates an audit log
- [ ] Updating a client shows field changes in audit log
- [ ] Deleting a client creates a DELETE audit log
- [ ] All operations capture user, IP, and timestamp

**All checked?** ✨ Audit logging is working perfectly!

---

**Quick Commands Reference:**

```bash
# Start
docker compose up --build

# Create superuser
docker compose exec web python manage.py createsuperuser

# Check logs count
docker compose exec web python manage.py shell -c "from audit.models import AuditLog; print(AuditLog.objects.count())"

# Stop
docker compose down
```
