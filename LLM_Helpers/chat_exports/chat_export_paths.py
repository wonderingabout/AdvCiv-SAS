# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Keep both transcript helpers on the same output path and let users configure it outside either script. (GPT-6.1-Sol) -->
# <!-- custom: re derives Claude Code's project folder name from the repository path. (Claude code Opus 5.5) -->
import os
from pathlib import Path
import re


configured_dir = os.environ.get("LLM_CHAT_EXPORT_DIR")
DEFAULT_EXPORT_DIR = Path(configured_dir).expanduser() if configured_dir else Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "llm_chat_exports"

# <!-- custom: Shared input locations too, so agents need not rediscover them: Claude Code keeps each session as <session-id>.jsonl under a per-project folder, which CLAUDE_CONFIG_DIR can relocate. (Claude code Opus 5.5) -->
# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
REPO_ROOT = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
claude_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
CLAUDE_PROJECTS_DIR = (Path(claude_config_dir).expanduser() if claude_config_dir else Path.home() / ".claude") / "projects"


def claude_project_dir(repo_root=REPO_ROOT):
    # <!-- custom: Claude Code names the folder after the repository path with every non-alphanumeric character replaced by "-"; checked against this repository's existing folder. (Claude code Opus 5.5) -->
    return CLAUDE_PROJECTS_DIR / re.sub(r"[^A-Za-z0-9]", "-", str(repo_root))


def latest_claude_session(repo_root=REPO_ROOT):
    project_dir = claude_project_dir(repo_root)
    sessions = sorted(project_dir.glob("*.jsonl"), key=lambda path: path.stat().st_mtime)
    if not sessions:
        raise SystemExit("No Claude Code session logs found in %s; pass the .jsonl or export ZIP explicitly." % project_dir)
    return sessions[-1]
