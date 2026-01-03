# Controls & Audit Trail (Design)
- Every transaction has: maker, checker (where required), timestamp, reference, attachments list.
- PV workflow: Draft -> Submitted -> Approved -> Paid -> Posted -> Archived.
- No PV/No Pay rule (configurable).
- Bank withdrawal must link to PV or Disbursement Batch.
- Exceptions reports: missing PV, PV-cheque mismatch, unexplained withdrawals, disbursement not captured.
