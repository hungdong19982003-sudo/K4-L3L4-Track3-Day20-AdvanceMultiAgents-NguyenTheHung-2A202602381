### User
Execute task code-eval according to instructions.

### Assistant
I will coordinate with specialized subagents to inspect the workspace, implement the solution, and review the outcome.

### Tool call: task
{"subagent_type": "explorer", "prompt": "Explore workspace and analyze test failures or data schema for code-eval."}

### Tool result
Explorer report: Identified codebase structure, failing assertions, and key input files.

### Tool call: task
{"subagent_type": "implementer", "prompt": "Implement code fixes and data transformations for code-eval."}

### Tool result
Implementer report: Applied required logic, updated functions, and verified local execution.

### Tool call: task
{"subagent_type": "reviewer", "prompt": "Review changes, verify regression suites and check conventions for code-eval."}

### Tool result
Reviewer report: Confirmed all tests pass. No unhandled edge cases observed.

### Assistant
All subagents completed their tasks. code-eval is fully resolved.