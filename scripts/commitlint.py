#!/usr/bin/env python3
"""Conventional Commits validator — used as a pre-commit commit-msg hook."""

import re
import sys

TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "test",
    "chore",
    "ci",
    "perf",
    "build",
    "revert",
}

PATTERN = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: .{1,100}$")

HELP = """
Commit message must follow Conventional Commits:

  <type>(<scope>): <short description>

  Types : feat fix docs style refactor test chore ci perf build revert
  Scope : optional, e.g. mpv, ui, scanner
  Breaking: add ! after type/scope for breaking changes

Examples:
  feat(ui): add seek-bar keyboard shortcut
  fix(mpv): close socket fd in quit()
  chore: add pre-commit hooks
  docs: update INSTALL.md
"""


def main() -> int:
    if "--edit" in sys.argv:
        # pre-commit passes the commit-msg file path as the last argument
        msg_file = sys.argv[-1]
        if msg_file == "--edit":
            print("commitlint: no commit message file provided", file=sys.stderr)
            return 1
        try:
            msg = open(msg_file).readline().strip()
        except OSError as e:
            print(f"commitlint: cannot read {msg_file}: {e}", file=sys.stderr)
            return 1
    else:
        msg = sys.argv[1] if len(sys.argv) > 1 else ""

    # Strip comments and blank lines
    msg = "\n".join(line for line in msg.splitlines() if not line.startswith("#")).strip()
    subject = msg.splitlines()[0] if msg else ""

    m = PATTERN.match(subject)
    if not m:
        print(f"\ncommitlint: invalid commit message:\n  {subject!r}", file=sys.stderr)
        print(HELP, file=sys.stderr)
        return 1

    commit_type = m.group("type")
    if commit_type not in TYPES:
        print(
            f"\ncommitlint: unknown type {commit_type!r}. " f"Allowed: {', '.join(sorted(TYPES))}",
            file=sys.stderr,
        )
        print(HELP, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
