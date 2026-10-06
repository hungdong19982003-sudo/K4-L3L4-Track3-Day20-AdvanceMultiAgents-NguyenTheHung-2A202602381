---
name: acme-log-conventions
description: Use when parsing server logs and performing error triage to follow Acme logging standards.
---
1. Standardize service names to lower-case with hyphens replaced by underscores (e.g. payment_service).
2. Sort the errors list ascending by service name, then by timestamp_utc.
3. Include top-level metadata: 'schema_version': 2 and 'generated_by': 'log-triage'.
