import os
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    python_dir = str(Path(sys.executable).parent)
    paths = [python_dir]
    git_usr_bin = Path(r"C:\Program Files\Git\usr\bin")
    if git_usr_bin.exists():
        paths.append(str(git_usr_bin))
    paths.extend(["/usr/local/bin", "/usr/bin", "/bin"])

    env = {
        "PATH": os.pathsep.join(paths),
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return LocalShellBackend(
        root_dir=sandbox,
        virtual_mode=True,
        inherit_env=False,
        env=env,
        timeout=120,
    )


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"Invalid mode: {mode}. Must be 'single' or 'subagents'.")

    kwargs = {}
    prompt = BASE_PROMPT

    if mode == "subagents":
        kwargs["subagents"] = [
            {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE}
            for sub in get_subagents()
        ]
        prompt = prompt + SUBAGENTS_NOTE

    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt = prompt + SKILLS_NOTE

    actual_model = model or make_model()
    if model is None and hasattr(actual_model, "_generate"):
        orig_gen = actual_model._generate

        def _robust_generate(*args, **kw):
            import time
            time.sleep(4)
            for _attempt in range(10):
                try:
                    print(f"  [LLM CALL] attempt {_attempt}...", flush=True)
                    res = orig_gen(*args, **kw)
                    print("  [LLM CALL] completed successfully.", flush=True)
                    return res
                except Exception as exc:
                    err_str = str(exc)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate" in type(exc).__name__.lower():
                        print(f"  [LLM 429] Sleeping 22s (attempt {_attempt}): {err_str[:80]}", flush=True)
                        time.sleep(22)
                        continue
                    print(f"  [LLM ERROR]: {type(exc).__name__}: {err_str[:100]}", flush=True)
                    raise
            return orig_gen(*args, **kw)

        actual_model._generate = _robust_generate

    return create_deep_agent(
        model=actual_model,
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
