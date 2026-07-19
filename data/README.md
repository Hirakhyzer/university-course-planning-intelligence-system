# Data policy

This repository runs with synthetic fictional university data by default.

Do not commit real student records, transcripts, advising notes, disability accommodations, financial-aid data, professor HR records, registrar extracts, or private institutional schedules.

For authorized institutional pilots, place local data under `data/raw/` and keep it out of Git. A real deployment should include:

- FERPA/privacy review
- institutional research approval where applicable
- registrar and advisor validation
- access control and audit logging
- appeal and correction workflows
- bias and accessibility review
- secure retention/deletion policy
