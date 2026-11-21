import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parent.parent

DECKS_STUB = """#!/bin/bash
printf '%s\\n' "$@" > "$STUB_ARGS"
printf '%b' "$STUB_OUTPUT"
exit "${STUB_STATUS:-0}"
"""

RECORDER_STUB = """#!/bin/bash
printf '%s\\n' "$@" > "$0.args"
cat > "$0.stdin"
"""


def executable(path, text):
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


@pytest.fixture
def stubs(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable(bin_dir / "decks", DECKS_STUB)
    for name in ("open", "pbcopy", "osascript"):
        executable(bin_dir / name, RECORDER_STUB)
    return bin_dir


@pytest.fixture
def decks_dir(tmp_path):
    directory = tmp_path / "decks"
    (directory / "toanki").mkdir(parents=True)
    return directory


@pytest.fixture
def run(stubs, decks_dir, tmp_path):
    def run_action(action, card="", output="", status=0, decks_bin=None, directory=None):
        args_file = tmp_path / "decks.args"
        env = {
            "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(tmp_path),
            "action": action,
            "card": card,
            "decks_dir": directory or str(decks_dir),
            "decks_bin": decks_bin or str(stubs / "decks"),
            "STUB_ARGS": str(args_file),
            "STUB_OUTPUT": output,
            "STUB_STATUS": str(status),
        }
        done = subprocess.run(
            [str(WORKFLOW / "run.sh")], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL
        )
        result = json.loads(done.stdout)["alfredworkflow"]
        called = args_file.read_text().splitlines() if args_file.exists() else None
        return result["variables"]["show"], result["arg"], called

    return run_action


@pytest.fixture
def filter_items():
    def items_for(query):
        done = subprocess.run([str(WORKFLOW / "filter.sh"), query], capture_output=True, text=True)
        return json.loads(done.stdout)["items"]

    return items_for
