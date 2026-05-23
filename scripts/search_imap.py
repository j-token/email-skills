#!/usr/bin/env python3
"""Search an email account over IMAP SSL/TLS."""

from __future__ import annotations

import argparse
import imaplib
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mail_common import (  # noqa: E402
    body_text,
    decode_mime,
    message_matches,
    normalize_snippet,
    parse_keywords,
    parse_message,
    parse_message_date,
    read_account_config,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class SearchHit:
    folder: str
    msg_id: bytes
    date: datetime | None
    sender: str
    subject: str
    snippet: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search a mailbox through IMAP SSL/TLS.")
    parser.add_argument("--config", help="Path to an INI config file with an [account] section.")
    parser.add_argument("--host", default=os.getenv("MAIL_IMAP_HOST"), help="IMAP host, for example imap.naver.com.")
    parser.add_argument("--port", type=int, default=int(os.getenv("MAIL_IMAP_PORT", "0") or "0"))
    parser.add_argument("--address", default=os.getenv("MAIL_ADDRESS"))
    parser.add_argument("--password", default=os.getenv("MAIL_PASSWORD"))
    parser.add_argument("--query", required=True, help="Space-separated keywords. Any keyword may match.")
    parser.add_argument("--since", help="Inclusive start date, YYYY-MM-DD.")
    parser.add_argument("--before", help="Exclusive end date, YYYY-MM-DD.")
    parser.add_argument("--folder", action="append", help="Folder/mailbox to search. Repeatable.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true", help="Print resolved connection settings without connecting.")
    return parser.parse_args()


def imap_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%d-%b-%Y")


def list_folders(client: imaplib.IMAP4_SSL) -> list[str]:
    status, data = client.list()
    if status != "OK":
        return ["INBOX"]
    folders: list[str] = []
    for row in data:
        if not row:
            continue
        text = row.decode("utf-8", errors="replace")
        match = re.search(r' "([^"]+)"$', text)
        folders.append(match.group(1) if match else text.rsplit(" ", 1)[-1].strip('"'))
    return folders or ["INBOX"]


def build_search_terms(args: argparse.Namespace) -> list[str]:
    terms = ["ALL"]
    if args.since:
        terms += ["SINCE", imap_date(args.since)]
    if args.before:
        terms += ["BEFORE", imap_date(args.before)]
    return terms


def search_folder(client: imaplib.IMAP4_SSL, folder: str, args: argparse.Namespace, keywords: list[str]) -> list[SearchHit]:
    status, _ = client.select(f'"{folder}"', readonly=True)
    if status != "OK":
        return []
    status, data = client.search(None, *build_search_terms(args))
    if status != "OK" or not data or not data[0]:
        return []

    hits: list[SearchHit] = []
    for msg_id in reversed(data[0].split()):
        if len(hits) >= args.limit:
            break
        status, payload = client.fetch(msg_id, "(RFC822)")
        if status != "OK" or not payload or not isinstance(payload[0], tuple):
            continue
        message = parse_message(payload[0][1])
        if not message_matches(message, keywords):
            continue
        hits.append(
            SearchHit(
                folder=folder,
                msg_id=msg_id,
                date=parse_message_date(message),
                sender=decode_mime(message.get("From")),
                subject=decode_mime(message.get("Subject")),
                snippet=normalize_snippet(body_text(message)),
            )
        )
    return hits


def main() -> int:
    args = parse_args()
    config = read_account_config(args.config)
    args.host = args.host or config.get("imap_host")
    args.port = args.port or int(config.get("imap_port", "993"))
    args.address = args.address or config.get("address")
    args.password = args.password or config.get("password")
    if args.dry_run:
        if not args.host or not args.address:
            print("Dry run requires at least host and address from --config or flags.", file=sys.stderr)
            return 2
        print(f"IMAP host: {args.host}")
        print(f"IMAP port: {args.port}")
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

    client = imaplib.IMAP4_SSL(args.host, args.port)
    try:
        client.login(args.address, args.password)
        folders = args.folder or list_folders(client)
        all_hits: list[SearchHit] = []
        for folder in folders:
            all_hits.extend(search_folder(client, folder, args, keywords))
            if len(all_hits) >= args.limit:
                break
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass

    for hit in all_hits[: args.limit]:
        date_text = hit.date.isoformat(sep=" ") if hit.date else ""
        print(f"[{date_text}] {hit.folder} #{hit.msg_id.decode(errors='replace')}")
        print(f"From: {hit.sender}")
        print(f"Subject: {hit.subject}")
        if hit.snippet:
            print(f"Snippet: {hit.snippet}")
        print()
    print(f"Total hits: {len(all_hits[: args.limit])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
