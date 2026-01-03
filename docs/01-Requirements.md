# Requirements (MVP First)
## MVP Modules
1. Users & Roles (RBAC)
2. Clients & KYC (basic)
3. Loans (origination, approvals, disbursement)
4. Repayments & schedules
5. Arrears ageing (PAR buckets)
6. NPL classification & provisioning support
7. Audit log (immutable)
8. Reports: disbursement vs target, PAR/NPL, top delinquent, collections vs target

## Non-functional
- Works offline on LAN
- Runs on Docker Desktop
- PostgreSQL as single source of truth
- Role-based access + segregation of duties
