
from pathlib import Path
import os, subprocess, sys

def ensure_workspace(ws: str | None) -> Path:
    if not ws:
        ws = os.path.expanduser("~/.cast_autosec")
    p = Path(os.path.expanduser(ws))
    p.mkdir(parents=True, exist_ok=True)
    return p

def run_cmd(cmd: list[str]):
    print("$", " ".join(cmd))
    p = subprocess.run(cmd, check=False)
    if p.returncode != 0:
        print(f"Command failed with exit code {p.returncode}", file=sys.stderr)
    return p.returncode

def docker_available() -> bool:
    try:
        subprocess.run(["docker","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False
