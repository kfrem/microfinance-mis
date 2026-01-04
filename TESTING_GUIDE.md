# Testing Guide - Automatic Audit Logging

This guide will help you test the new automatic audit logging feature on your local machine.

## Prerequisites

- ✅ Docker Desktop installed and running on Windows 11
- ✅ Git installed
- ✅ Terminal (PowerShell, CMD, or Git Bash)

## Step-by-Step Testing Instructions

### 1. Pull the Latest Changes

```bash
# Navigate to your project directory
cd path/to/microfinance-mis

# Pull the latest changes from GitHub
git pull origin main

# Or if you want to test the PR branch directly:
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
```

### 2. Start the Application

```bash
# Make sure Docker Desktop is running, then:
docker compose up --build
```

Wait for the containers to start. You should see output like:
```
web_1  | Starting development server at http://0.0.0.0:8000/
web_1  | Quit the server with CONTROL-C.
```

### 3. Access the Admin Interface

Open your browser and go to:
- **URL**: http://localhost:8000/admin/

If you don't have a superuser yet, create one:
```bash
# In a new terminal window:
docker compose exec web python manage.py createsuperuser

# Follow the prompts to create username/password
```

### 4. Test Audit Logging

#### Test 1: Create a Client (CREATE action)
1. Go to http://localhost:8000/admin/clients/client/
2. Click "Add Client"
3. Fill in:
   - Full name: "John Doe"
   - Phone: "555-1234"
   - Email: "john@example.com"
4. Click "Save"

#### Test 2: Update a Client (UPDATE action)
1. Click on the client you just created
2. Change the phone to "555-5678"
3. Click "Save"

#### Test 3: Create a Loan (CREATE action)
1. Go to http://localhost:8000/admin/loans/loan/
2. Click "Add Loan"
3. Fill in:
   - Client: Select John Doe
   - Principal: 10000
   - Interest rate: 12.5
   - Term months: 12
   - Status: Active
4. Click "Save"

#### Test 4: Create a Repayment (CREATE action)
1. Go to http://localhost:8000/admin/repayments/repayment/
2. Click "Add Repayment"
3. Fill in:
   - Loan: Select the loan you created
   - Amount: 1000
   - Paid on: Today's date
   - Method: "Cash"
4. Click "Save"

#### Test 5: Delete a Repayment (DELETE action)
1. Select the repayment you created
2. Click "Delete"
3. Confirm deletion

### 5. Verify Audit Logs Were Created

#### Method 1: Via Admin Interface
1. Go to http://localhost:8000/admin/audit/auditlog/
2. You should see all the actions you performed:
   - Client CREATE
   - Client UPDATE (with field changes shown)
   - Loan CREATE
   - Repayment CREATE
   - Repayment DELETE

#### Method 2: Via Command Line
```bash
# Check total audit log count
docker compose exec web python manage.py shell -c "from audit.models import AuditLog; print(f'Total audit logs: {AuditLog.objects.count()}')"

# View recent audit logs
docker compose exec web python manage.py shell -c "
from audit.models import AuditLog
for log in AuditLog.objects.all()[:10]:
    print(f'{log.created_at} | {log.user} | {log.action} | {log.app_label}.{log.model_name} | {log.object_repr}')
"

# Check logs by action type
docker compose exec web python manage.py shell -c "
from audit.models import AuditLog
print(f'CREATE: {AuditLog.objects.filter(action=\"CREATE\").count()}')
print(f'UPDATE: {AuditLog.objects.filter(action=\"UPDATE\").count()}')
print(f'DELETE: {AuditLog.objects.filter(action=\"DELETE\").count()}')
"

# View detailed changes from an UPDATE action
docker compose exec web python manage.py shell -c "
from audit.models import AuditLog
update_log = AuditLog.objects.filter(action='UPDATE').first()
if update_log:
    print(f'Action: {update_log.action}')
    print(f'User: {update_log.user}')
    print(f'Object: {update_log.object_repr}')
    print(f'Changes: {update_log.changes}')
    print(f'IP: {update_log.ip_address}')
"
```

## Expected Results

✅ **Every CREATE operation** should create an audit log with:
- Action: CREATE
- User: Your username
- Object details
- IP address
- Timestamp

✅ **Every UPDATE operation** should create an audit log with:
- Action: UPDATE
- User: Your username
- Object details
- **Changes field showing old vs new values**
- IP address
- Timestamp

✅ **Every DELETE operation** should create an audit log with:
- Action: DELETE
- User: Your username
- Object ID and representation (before deletion)
- IP address
- Timestamp

## Audit Log Fields Explained

When viewing audit logs in the admin, you'll see:

| Field | Description |
|-------|-------------|
| **Created at** | When the action occurred |
| **User** | Who performed the action |
| **Action** | CREATE, UPDATE, or DELETE |
| **App label** | clients, loans, or repayments |
| **Model name** | Client, Loan, or Repayment |
| **Object ID** | Database ID of the object |
| **Object repr** | String representation of the object |
| **Changes** | JSON showing field changes (for UPDATE) |
| **Message** | Human-readable description |
| **IP address** | IP of the user who made the change |
| **User agent** | Browser/client information |

## Troubleshooting

### Issue: "No audit logs appearing"
**Solution**: Make sure you're logged in as a user when performing operations. System operations without a logged-in user won't create audit logs.

### Issue: "Changes field is empty"
**Solution**: The changes field only populates for UPDATE actions. CREATE and DELETE actions won't have field changes.

### Issue: "Can't access admin"
**Solution**: 
1. Make sure containers are running: `docker compose ps`
2. Create a superuser: `docker compose exec web python manage.py createsuperuser`

### Issue: "Connection refused"
**Solution**: 
1. Ensure Docker Desktop is running
2. Check containers: `docker compose ps`
3. Rebuild: `docker compose down && docker compose up --build`

## Test Bulk Delete

To test bulk delete functionality:

1. Go to http://localhost:8000/admin/clients/client/
2. Create 3 test clients
3. Select all 3 using checkboxes
4. Choose "Delete selected clients" from the action dropdown
5. Click "Go"
6. Confirm deletion
7. Check audit logs - you should see 3 separate DELETE audit logs

## Stopping the Application

When done testing:

```bash
# Stop containers (preserves data)
docker compose stop

# Or stop and remove containers (cleans up)
docker compose down
```

## Success Criteria

✅ All CRUD operations on Clients create audit logs
✅ All CRUD operations on Loans create audit logs
✅ All CRUD operations on Repayments create audit logs
✅ UPDATE operations show field-level changes in the changes field
✅ DELETE operations preserve object information before deletion
✅ Bulk delete creates individual audit logs for each object
✅ User, IP address, and user agent are captured
✅ Audit logs are immutable (can't be edited in admin)

## Next Steps After Testing

Once you've verified the audit logging works correctly:

1. ✅ Merge the pull request on GitHub
2. 📊 Start using the system for real data
3. 📈 Monitor audit logs for compliance and security
4. 🔄 Move on to Phase 2 features (dashboards, reporting, etc.)

---

**Need help?** Check the audit log admin interface for detailed information about each operation.
