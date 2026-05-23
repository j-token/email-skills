#!/usr/bin/env python3
"""Search an email account over POP3 SSL/TLS."""

from __future__ import annotations

import argparse
import os
import poplib
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mail_common import (  # noqa: E402
    body_text,
    decode_mime,
    in_date_range,
    message_matches,
    normalize_snippet,
    parse_date,
    parse_keywords,
    parse_message,
    parse_message_date,
    read_account_config,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class SearchHit:
    msg_no: int
    date: datetime | None
    sender: str
    subject: str
    snippet: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search a mailbox through POP3 SSL/TLS.")
    parser.add_argument("--config", help="Path to an INI config file with an [account] section.")
    parser.add_argument("--host", default=os.getenv("MAIL_POP_HOST"), help="POP host, for example pop.naver.com.")
    parser.add_argument("--port", type=int, default=int(os.getenv("MAIL_POP_PORT", "0") or "0"))
    parser.add_argument("--address", default=os.getenv("MAIL_ADDRESS"))
    parser.add_argument("--password", default=os.getenv("MAIL_PASSWORD"))
    parser.add_argument("--query", required=True, help="Space-separated keywords. Any keyword may match.")
    parser.add_argument("--since", help="Inclusive start date, YYYY-MM-DD.")
    parser.add_argument("--before", help="Exclusive end date, YYYY-MM-DD.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--scan-limit", type=int, default=500, help="Newest messages to inspect.")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved connection settings without connecting.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_account_config(args.config)
    args.host = args.host or config.get("pop_host")
    args.port = args.port or int(config.get("pop_port", "995"))
    args.address = args.address or config.get("address")
    args.password = args.password or config.get("password")
    if args.dry_run:
        if not args.host or not args.address:
            print("Dry run requires at least host and address from --config or flags.", file=sys.stderr)
            return 2
        print(f"POP host: {args.host}")
        print(f"POP port: {args.port}")
        print(f"Address: {args.address}")
        print(f"Password: {'[set]' if args.password else '[not set]'}")
        return 0
    if not args.host or not args.address or not args.password:
        print("Provide --config, or pass --host, --address, and --password.", file=sys.stderr)
        return 2

    keywords = parse_keywords(args.query)
    if not keywords:
        print("--query must include at least one keyword.", file=sys.stderr)
        return 2

    since = parse_date(args.since)
    before = parse_date(args.before)
    hits: list[SearchHit] = []

    client = poplib.POP3_SSL(args.host, args.port, timeout=30)
    try:
        client.user(args.address)
        client.pass_(args.password)
        message_count = len(client.list()[1])
        start = max(1, message_count - args.scan_limit + 1)
        for msg_no in range(message_count, start - 1, -1):
            if len(hits) >= args.limit:
                break
            response, lines, _ = client.retr(msg_no)
            if not response.startswith(b"+OK"):
                continue
            message = parse_message(b"\n".join(lines))
            date_value = parse_message_date(message)
            if not in_date_range(date_value, since, before):
                continue
            if not message_matches(message, keywords):
                continue
            hits.append(
                SearchHit(
                    msg_no=msg_no,
                    date=date_value,
                    sender=decode_mime(message.get("From")),
                    subject=decode_mime(message.get("Subject")),
                    snippet=normalize_snippet(body_text(message)),
                )
            )
    finally:
        client.quit()

    for hit in hits:
        date_text = hit.date.isoformat(sep=" ") if hit.date else ""
        print(f"[{date_text}] POP #{hit.msg_no}")
        print(f"From: {hit.sender}")
        print(f"Subject: {hit.subject}")
        if hit.snippet:
            print(f"Snippet: {hit.snippet}")
        print()
    print(f"Total hits: {len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
