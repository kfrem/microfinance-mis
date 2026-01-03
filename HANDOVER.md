\# HANDOVER — Microfinance MIS MVP



\## Purpose

Build a low-cost Microfinance MIS MVP that supports:

\- Client onboarding

\- Loan creation linked to clients

\- Repayment capture linked to loans

\- Admin dashboards later (Phase 2)

\- Audit trail of who did what (AuditLog)



\## What has been done (confirmed working)

\- Docker + Django running locally (Windows 11)

\- Admin login works: http://localhost:8000/admin/

\- Apps installed and visible in Admin:

&nbsp; - Clients

&nbsp; - Loans

&nbsp; - Repayments

&nbsp; - Audit logs

\- Database migrations created and applied for:

&nbsp; - clients, loans, repayments, audit



\## Current limitation

\- The AuditLog model exists but does NOT automatically record events yet.

\- Django’s internal admin history (LogEntry) works, but it is separate from AuditLog.



\## Immediate next development task

Implement automatic audit logging for:

\- Client create/update/delete

\- Loan create/update/delete

\- Repayment create/update/delete



Recommended approach (fast for MVP):

\- Override save\_model() and delete\_model() in each ModelAdmin to create AuditLog entries.



\## How to run

\- docker compose up -d

\- Admin: http://localhost:8000/admin/



\## Verification commands

\- Check containers:

&nbsp; - docker compose ps

\- Check AuditLog count:

&nbsp; - docker compose exec web python manage.py shell -c "from audit.models import AuditLog; print(AuditLog.objects.count())"

\- Check Django admin internal log count:

&nbsp; - docker compose exec web python manage.py shell -c "from django.contrib.admin.models import LogEntry; print(LogEntry.objects.count())"



\## Next phases (after MVP)

\- Add regulatory reporting outputs (BoG templates) and dashboards

\- Add role-based permissions per staff function

\- Add arrears/PAR reporting, provisioning rules, and portfolio KPIs



