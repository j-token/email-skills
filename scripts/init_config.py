#!/usr/bin/env python3
"""Create a user-owned mail config file from a provider template."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Codex" / "email-protocol"


PROVIDERS = {
    "generic": {
        "filename": "mail.ini",
        "content": """[account]
# Full email address used as the protocol username.
address = user@example.com

# Provider application password or protocol password.
password =

# POP3 over SSL/TLS.
pop_host = pop.example.com
pop_port = 995

# IMAP over SSL/TLS.
imap_host = imap.example.com
imap_port = 993
""",
    },
    "naver": {
        "filename": "naver-mail.ini",
        "content": """[account]
# Full email address used as the protocol username.
address = your-naver-address

# Paste the Naver application password here.
password =

# POP3 over SSL/TLS. Works with the POP settings currently enabled in Naver Mail.
pop_host = pop.naver.com
pop_port = 995

# IMAP over SSL/TLS. Fill/use this when IMAP is enabled in Naver Mail.
imap_host = imap.naver.com
imap_port = 993
""",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an Email Protocol config file.")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="generic")
    parser.add_argument("--output", help="Config file path to create.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing config file.")
    parser.add_argument("--open", action="store_true", help="Open the config file in Notepad on Windows.")
    return parser.parse_args()


def open_file(path: Path) -> None:
    if sys.platform.startswith("win"):
        subprocess.Popen(["notepad.exe", str(path)])
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
        return
    subprocess.Popen(["xdg-open", str(path)])


def main() -> int:
    args = parse_args()
    provider = PROVIDERS[args.provider]
    output = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / provider["filename"]
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.force:
        print(f"Config already exists: {output}")
    else:
        output.write_text(provider["content"], encoding="utf-8")
        print(f"Created config: {output}")

    if args.open:
        open_file(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
