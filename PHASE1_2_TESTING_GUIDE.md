# 🧪 Phase 1 & 2 Testing Guide

## Complete Testing Checklist for Microfinance MIS

---

## 📋 Pre-Testing Setup

### ✅ Step 1: Generate Test Data

**Run this command in PowerShell:**
```powershell
docker compose exec web python manage.py generate_test_data --clients 20 --loans 15
```

**Expected Output:**
- ✓ Created 20 clients (Ghana-based names, phone numbers, Ghana Cards)
- ✓ Created 15 loans across all 5 products
- ✓ Generated repayment schedules automatically
- ✓ Created realistic repayments (some on time, some late)
- ✓ Portfolio summary showing active loans and outstanding amounts

---

## 🎯 Phase 1 Testing: Financial Engine

### Test 1.1: Client Management ✅

**Location:** http://localhost:8000/admin/clients/client/

**What to Check:**
- [ ] All 20 clients appear in the list
- [ ] Client IDs are auto-generated (C00001, C00002, etc.)
- [ ] Ghana Card IDs are displayed
- [ ] Risk categories show (Low, Medium, High)
- [ ] KYC verification status is visible
- [ ] Phone numbers are in Ghana format (+233...)

**Test Actions:**
1. Click on a client to view details
2. Verify all fields are populated correctly
3. Check that client type (Individual, Group, SME) is set

**Expected Result:** ✓ All client data displays correctly with Ghana-specific information

---

### Test 1.2: Loan Products ✅

**Location:** http://localhost:8000/admin/loans/loanproduct/

**What to Check:**
- [ ] All 5 Ghana microfinance products are listed:
  1. Individual Micro Loan (IML-001)
  2. Group Solidarity Loan (GSL-002)
  3. SME Business Loan (SME-003)
  4. Agricultural Loan (AGL-004)
  5. Emergency Loan (EML-005)

**Test Actions:**
1. Click on each product
2. Verify interest rates are set
3. Check interest methods (Flat vs Declining Balance)
4. Verify term limits (min/max months)
5. Check fees (processing, insurance, late payment)

**Expected Result:** ✓ All 5 products configured with correct Ghana microfinance parameters

---

### Test 1.3: Loan Creation & Calculation ✅

**Location:** http://localhost:8000/admin/loans/loan/

**What to Check:**
- [ ] All 15 loans appear
- [ ] Loan IDs are auto-generated (L000001, L000002, etc.)
- [ ] Status shows correctly (Pending, Active, Closed)
- [ ] BoG Classification displayed (Current, Substandard, Doubtful, Loss)
- [ ] Days in arrears calculated

**Test Actions:**
1. Select an ACTIVE loan
2. Verify these calculated fields:
   - Total Interest
   - Total Repayable
   - Installment Amount
3. Check dates:
   - Application Date
   - Approved Date
   - Disbursed Date
   - Maturity Date

**Expected Result:** ✓ All loan calculations are correct based on interest method

---

### Test 1.4: Repayment Schedule ✅

**Location:** Click on a loan → View "Schedule Entries"

**What to Check:**
- [ ] Schedule is generated automatically after disbursement
- [ ] Installment numbers are sequential (1, 2, 3...)
- [ ] Due dates follow repayment frequency (daily/weekly/monthly)
- [ ] For DECLINING balance:
  - [ ] Principal increases each installment
  - [ ] Interest decreases each installment
- [ ] For FLAT rate:
  - [ ] Principal is equal each installment
  - [ ] Interest is equal each installment
- [ ] Outstanding balance decreases correctly

**Test Actions:**
1. Select 2 loans: one with Flat rate, one with Declining
2. Compare schedule patterns
3. Verify total matches loan's "Total Repayable"

**Expected Result:** ✓ Schedules are mathematically correct for both interest methods

---

### Test 1.5: Payment Allocation ✅

**Location:** http://localhost:8000/admin/repayments/repayment/

**What to Check:**
- [ ] Receipt numbers are auto-generated (RCP0000001, etc.)
- [ ] Payment allocation is automatic:
  - [ ] Penalties paid first
  - [ ] Interest paid second
  - [ ] Principal paid last
- [ ] Loan schedule updates after each payment

**Test Actions:**
1. Select a repayment record
2. Check allocation fields:
   - Principal Paid
   - Interest Paid
   - Penalty Paid
3. Go back to loan's schedule
4. Verify schedule entries show "Paid" amounts

**Expected Result:** ✓ Payments are allocated correctly using waterfall method

---

### Test 1.6: BoG Loan Classification ✅

**Location:** Dashboard or Admin → Loans

**What to Check:**
- [ ] Loans with 0-30 days arrears = "Current"
- [ ] Loans with 31-90 days arrears = "Substandard"
- [ ] Loans with 91-180 days arrears = "Doubtful"
- [ ] Loans with 180+ days arrears = "Loss"

**Test Actions:**
1. Filter loans by classification
2. Check days_in_arrears matches classification
3. Verify classification updates automatically after payments

**Expected Result:** ✓ BoG classification follows Bank of Ghana prudential guidelines

---

## 📊 Phase 2 Testing: Dashboard & Analytics

### Test 2.1: Executive Dashboard ✅

**Location:** http://localhost:8000/dashboard/

**What to Check:**
- [ ] **6 Key Metrics Display:**
  1. Portfolio Value (total principal disbursed)
  2. Outstanding Balance (current amount owed)
  3. Collection Rate (%)
  4. PAR 30 (Portfolio at Risk > 30 days)
  5. PAR 90 (Portfolio at Risk > 90 days)
  6. Total Provisions Required

**Test Actions:**
1. Verify all 6 cards show numbers (not zeros)
2. Check if percentages are realistic (0-100%)
3. Refresh page - numbers should be consistent

**Expected Result:** ✓ All metrics display real-time portfolio data

---

### Test 2.2: BoG Classification Table ✅

**Location:** Dashboard → BoG Loan Classification section

**What to Check:**
- [ ] Four rows display:
  - Current (0-30 days)
  - Substandard (31-90 days)
  - Doubtful (91-180 days)
  - Loss (180+ days)
- [ ] Each row shows:
  - Loan count
  - Total value (GHS)
  - Provision % required
  - Provision amount

**Test Actions:**
1. Add up loan counts - should equal total active loans
2. Verify provision % matches BoG guidelines:
   - Current: 1%
   - Substandard: 10%
   - Doubtful: 50%
   - Loss: 100%

**Expected Result:** ✓ Classification breakdown matches Bank of Ghana standards

---

### Test 2.3: Product Performance Table ✅

**Location:** Dashboard → Loan Product Performance section

**What to Check:**
- [ ] All 5 products listed
- [ ] Each product shows:
  - Active loan count
  - Outstanding amount
  - Loans in arrears count
  - Arrears amount

**Test Actions:**
1. Verify totals add up correctly
2. Check if products with more loans show higher numbers
3. Identify which products have highest arrears

**Expected Result:** ✓ Product performance shows realistic distribution

---

### Test 2.4: Arrears Aging Analysis ✅

**Location:** Dashboard → Arrears Aging section

**What to Check:**
- [ ] Four aging buckets:
  - 31-60 days
  - 61-90 days
  - 91-180 days
  - 180+ days
- [ ] Each bucket shows:
  - Loan count
  - Total amount in arrears

**Test Actions:**
1. Verify loans are correctly bucketed by days overdue
2. Check that older buckets have fewer loans (as expected)
3. Verify amounts are in Ghana Cedis (GHS)

**Expected Result:** ✓ Arrears aging helps identify collection priorities

---

### Test 2.5: Client Statistics ✅

**Location:** Dashboard → Client Statistics section

**What to Check:**
- [ ] Total Clients count
- [ ] Active Borrowers count (clients with active loans)
- [ ] Risk Level Breakdown:
  - Low Risk
  - Medium Risk
  - High Risk

**Test Actions:**
1. Verify Active Borrowers ≤ Total Clients
2. Check risk distribution makes sense
3. Verify numbers match admin client counts

**Expected Result:** ✓ Client stats accurately reflect database

---

### Test 2.6: Portfolio Quality Report ✅

**Location:** http://localhost:8000/dashboard/portfolio/

**What to Check:**
- [ ] All metrics from executive dashboard
- [ ] Detailed breakdown tables
- [ ] More detailed analytics

**Test Actions:**
1. Compare with executive dashboard
2. Verify consistency of numbers
3. Check for additional insights

**Expected Result:** ✓ Portfolio report provides comprehensive analysis

---

### Test 2.7: BoG Prudential Report ✅

**Location:** http://localhost:8000/dashboard/bog/

**What to Check:**
- [ ] Regulatory-compliant report format
- [ ] Classification breakdown
- [ ] Provision calculations
- [ ] NPL (Non-Performing Loan) ratio

**Test Actions:**
1. Verify all BoG requirements are covered
2. Check provision calculations are correct
3. Verify report is ready for submission

**Expected Result:** ✓ BoG report meets Bank of Ghana reporting standards

---

## 🌐 Deployment Testing

### Test 3.1: Local Access ✅

**Location:** http://localhost:8000/dashboard/

**What to Check:**
- [ ] Dashboard loads without errors
- [ ] All sections display correctly
- [ ] No authentication required (for demo)

---

### Test 3.2: Online Access (Cloudflare Tunnel) ✅

**Location:** https://tabs-sheer-casual-arts.trycloudflare.com/dashboard/

**What to Check:**
- [ ] Same dashboard loads from internet
- [ ] HTTPS connection is secure
- [ ] All data displays correctly
- [ ] No "DisallowedHost" errors

**Test Actions:**
1. Open in incognito/private window
2. Test from another device (phone/tablet)
3. Share link with colleague to verify access

**Expected Result:** ✓ System is accessible online via Cloudflare Tunnel

---

## 📸 Documentation & Screenshots

### Capture These Screenshots:

1. **Executive Dashboard** - Full view with all 6 metrics
2. **BoG Classification Table** - Showing all 4 categories
3. **Product Performance** - All 5 products listed
4. **Arrears Aging** - All aging buckets
5. **Admin - Client List** - Showing 20 clients
6. **Admin - Loan List** - Showing 15 loans
7. **Admin - Loan Schedule** - One loan's full schedule
8. **Admin - Repayment List** - Multiple repayments

---

## ✅ Final Checklist

Before moving to Phase 3, ensure:

- [ ] Test data is generated successfully
- [ ] All 20 clients are in the system
- [ ] All 15 loans are created with schedules
- [ ] Dashboard displays non-zero metrics
- [ ] BoG classification is working correctly
- [ ] Payment allocation follows waterfall method
- [ ] System is accessible online via Cloudflare
- [ ] No errors in browser console (F12)
- [ ] All admin sections are accessible
- [ ] Screenshots are captured for documentation

---

## 🐛 Common Issues & Fixes

### Issue: Dashboard shows all zeros
**Fix:** Run `generate_test_data` command

### Issue: Can't login to admin
**Fix:** Run `docker compose exec web python manage.py createsuperuser`

### Issue: Tunnel not accessible online
**Fix:** Check `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in settings.py

### Issue: Loans have no schedules
**Fix:** Click on loan in admin → Save (this triggers schedule generation)

---

## 🚀 Ready for Phase 3?

Once all tests pass, we'll move to Phase 3:
- Advanced Report Generation (Excel, PDF)
- Email Delivery System
- Cash Flow Projections
- Data Export Features

---

**Testing Date:** _____________

**Tested By:** _____________

**Status:** ✅ PASS / ❌ FAIL

**Notes:**
_______________________________________
_______________________________________
_______________________________________
