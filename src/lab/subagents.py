"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when you need to inspect files, search patterns, read specifications, "
                "sample data, logs, or README without modifying any file."
            ),
            "system_prompt": (
                "You are an exploratory subagent. Your role is to carefully inspect directory structures, "
                "read specifications, docstrings, code, and sample data. Report accurate factual findings, "
                "summaries, and exact locations back to the main agent. Do not modify or delete any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when you need to write code, apply edits, fix errors, transform data, "
                "or run shell scripts and tests to verify changes."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to apply precise file edits, create "
                "required output files, write code or data transformations, and run tests or scripts "
                "using the shell to verify your implementation before reporting back."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when implementation is finished to independently verify test suites, check against "
                "constraints, formatting conventions, edge cases, and report any remaining issues."
            ),
            "system_prompt": (
                "You are an independent reviewer subagent. Your role is to verify the final workspace state "
                "against all task requirements, run tests or validation scripts, check for subtle edge cases, "
                "formatting errors, and report whether everything passes or what issues remain. Do not modify files."
            ),
        },
    ]
