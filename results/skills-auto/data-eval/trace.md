### User
Execute task data-eval according to instructions.

### Assistant
Let me check the available Acme team conventions before proceeding.

### Tool call: read_file
{"file_path": "skills/acme-data-conventions/SKILL.md"}

### Tool result
Loaded team convention skill: acme-data-conventions.

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
Task data-eval completed successfully following all Acme guidelines.