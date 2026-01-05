# 🚀 QUICK START GUIDE - Ghana Microfinance MIS

**Complete setup in 5 minutes!**

---

## ✅ Step 1: Pull Latest Code

```powershell
cd C:\Users\kfrem\Desktop\microfinance-mis
git pull origin genspark_ai_developer
```

---

## ✅ Step 2: Start Docker Containers

```powershell
docker compose up -d
```

**Wait 30 seconds for containers to start**

---

## ✅ Step 3: Check Containers Are Running

```powershell
docker compose ps
```

**Expected Output:**
```
NAME                        STATUS
microfinance-mis-db-1       Up
microfinance-mis-web-1      Up
```

Both should show "Up" ✅

---

## ✅ Step 4: Create Admin User

```powershell
docker compose exec web python manage.py createsuperuser
```

**Enter when prompted:**
- Username: `admin`
- Email: (press Enter to skip)
- Password: `admin123`
- Password (again): `admin123`

---

## ✅ Step 5: Generate Test Data

```powershell
docker compose exec web python manage.py generate_test_data
```

**This creates:**
- ✅ 50 test clients
- ✅ 75 test loans  
- ✅ 150+ repayment records
- ✅ Complete loan schedules

**Takes about 30 seconds**

---

## 🎉 Step 6: ACCESS YOUR APPLICATION!

### **Management Dashboard** (Main Dashboard)
```powershell
Start-Process "http://localhost:8000/management/"
```

**What you'll see:**
- ✅ KPI metric cards (Portfolio Value, Outstanding, Collection Rate, PAR 30)
- ✅ Management report cards (P&L, Officer Performance, Cash Flow)
- ✅ Board report cards (Executive Summary, Portfolio Quality, BoG Compliance)
- ✅ Quick export buttons (Excel & PDF)

---

### **Admin Panel** (Full Database Access)
```powershell
Start-Process "http://localhost:8000/admin/"
```

**Login with:**
- Username: `admin`
- Password: `admin123`

**You can manage:**
- Clients
- Loans
- Repayments
- Loan Schedules
- Scheduled Reports
- Report Snapshots

---

### **Operational Reports** (Phase 3 Reports)
```powershell
Start-Process "http://localhost:8000/reports/"
```

**Available Reports:**
- Client Portfolio Report
- Loan Aging Analysis
- BoG Regulatory Report
- Cash Flow Projection

---

### **Analytics Dashboard** (Phase 2 Dashboard)
```powershell
Start-Process "http://localhost:8000/dashboard/"
```

---

## 📊 QUICK TEST CHECKLIST

### Test Management Dashboard:
1. ✅ Open http://localhost:8000/management/
2. ✅ Verify KPI cards show real numbers
3. ✅ Click "📊 View Report" on any report card
4. ✅ Click "📥 Excel" or "📄 PDF" to download reports

### Test Specific Reports:
1. ✅ **P&L Statement**: http://localhost:8000/management/profit-loss/
2. ✅ **Board Report**: http://localhost:8000/management/board-report/
3. ✅ **Officer Performance**: http://localhost:8000/management/officer-performance/

### Test Downloads:
1. ✅ Download P&L Excel
2. ✅ Download P&L PDF
3. ✅ Download Board Excel
4. ✅ Download Board PDF
5. ✅ Download Officer Performance Excel

---

## 🔧 TROUBLESHOOTING

### If containers won't start:
```powershell
docker compose down -v
docker compose up --build -d
```

### If you see "Django not found" error:
```powershell
docker compose down -v
docker compose up --build -d
docker compose logs -f web
```

Wait for "Watching for file changes with StatReloader"

### If test data command fails:
```powershell
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py generate_test_data
```

### View container logs:
```powershell
docker compose logs web --tail 50
```

---

## 📋 ALL ACCESS POINTS

### Main Dashboards
- **Management Dashboard**: http://localhost:8000/management/
- **Operational Reports**: http://localhost:8000/reports/
- **Analytics Dashboard**: http://localhost:8000/dashboard/
- **Admin Panel**: http://localhost:8000/admin/

### Management Reports
- **Profit & Loss**: http://localhost:8000/management/profit-loss/
- **Board Summary**: http://localhost:8000/management/board-report/
- **Officer Performance**: http://localhost:8000/management/officer-performance/

### Report Downloads
- **P&L Excel**: http://localhost:8000/management/excel/profit-loss/
- **P&L PDF**: http://localhost:8000/management/pdf/profit-loss/
- **Board Excel**: http://localhost:8000/management/excel/board-report/
- **Board PDF**: http://localhost:8000/management/pdf/board-report/
- **Officer Excel**: http://localhost:8000/management/excel/officer-performance/

### Operational Reports
- **Client Portfolio Excel**: http://localhost:8000/reports/excel/portfolio/
- **Loan Aging Excel**: http://localhost:8000/reports/excel/aging/
- **BoG Report Excel**: http://localhost:8000/reports/excel/bog/
- **BoG Report PDF**: http://localhost:8000/reports/pdf/bog/
- **Portfolio Summary PDF**: http://localhost:8000/reports/pdf/portfolio/
- **Cash Flow**: http://localhost:8000/reports/cashflow/

---

## 🎯 WHAT TO DO NEXT

### 1. Explore the Management Dashboard
- Open http://localhost:8000/management/
- Review all KPI metrics
- Click through each report card
- Test Excel and PDF downloads

### 2. Check Admin Panel
- Login at http://localhost:8000/admin/
- Browse through all models
- View test data created
- Try editing a client or loan

### 3. Test All Reports
- Go through each report type
- Download samples in Excel and PDF
- Verify data accuracy
- Check formatting and styling

### 4. Review Documentation
- Read PHASE4_DEPLOYMENT.md for detailed info
- Check PHASE4_COMPLETE.md for feature list
- See TROUBLESHOOTING.md if you have issues

---

## 🎉 SUCCESS!

**If you can:**
1. ✅ See the Management Dashboard with KPI metrics
2. ✅ Click on report cards and see reports
3. ✅ Download Excel and PDF files
4. ✅ Access the Admin panel

**Then your Ghana Microfinance MIS is FULLY OPERATIONAL!** 🚀

---

## 📞 SUPPORT

**Stuck?** Check these files:
- `TROUBLESHOOTING.md` - Common issues and fixes
- `PHASE4_DEPLOYMENT.md` - Detailed deployment guide
- `PHASE4_COMPLETE.md` - Complete feature documentation

**Quick Commands Reference:**
```powershell
# Start system
docker compose up -d

# Stop system
docker compose down

# View logs
docker compose logs web

# Restart web container
docker compose restart web

# Access container shell
docker compose exec web bash

# Create admin user
docker compose exec web python manage.py createsuperuser

# Generate test data
docker compose exec web python manage.py generate_test_data
```

---

**Built for Ghana Microfinance Institutions** 🇬🇭  
**Empowering Financial Inclusion Through Technology** 💪
