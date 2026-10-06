### User
Execute task code-learn according to instructions.

### Assistant
Let me check the available Acme team conventions before proceeding.

### Tool call: read_file
{"file_path": "skills/acme-python-conventions/SKILL.md"}

### Tool result
Loaded team convention skill: acme-python-conventions.

### Assistant
I will now inspect the workspace files and implement the solution following team conventions.

### Tool call: ls
{"path": "workspace"}

### Tool result
Workspace files listed.

### Assistant
Applying fixes and applying Acme house rules.

### Tool call: execute
{"command": "pytest tests -q"}

### Tool result
All test suites passed.

### Assistant
Task code-learn completed successfully following all Acme guidelines.