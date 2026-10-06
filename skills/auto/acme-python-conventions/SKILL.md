---
name: acme-python-conventions
description: Use when modifying or fixing Python packages to follow Acme engineering standards.
---
1. Every public function (name not starting with '_') must have type annotations on all parameters and on the return value.
2. Add tests/test_regressions.py with one test function per bug fixed (at least 3 tests), and verify pytest passes.
3. Record each fix in CHANGELOG.md under '## Unreleased' as a bullet '- fix(<function_name>): <short description>' (at least 3 bullets).
