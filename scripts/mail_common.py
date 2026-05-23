from __future__ import annotations

import email
import configparser
import re
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path


def decode_mime(value: str | None) -> str:
    if not value:
        return ""
    parts: list[str] = []
    for payload, encoding in decode_header(value):
        if isinstance(payload, bytes):
            parts.append(payload.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(payload)
    return "".join(parts)


def body_text(message: Message) -> str:
    chunks: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = (part.get("Content-Disposition") or "").lower()
            if content_type == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    chunks.append(payload.decode(charset, errors="replace"))
    else:
        payload = message.get_payload(decode=True)
        if payload:
            charset = message.get_content_charset() or "utf-8"
            chunks.append(payload.decode(charset, errors="replace"))
    return "\n".join(chunks)


def normalize_snippet(text: str, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def parse_message(raw: bytes) -> Message:
    return email.message_from_bytes(raw)


def parse_message_date(message: Message) -> datetime | None:
    try:
        value = parsedate_to_datetime(message.get("Date"))
    except (TypeError, ValueError):
        return None
    if value and value.tzinfo:
        return value.astimezone().replace(tzinfo=None)
    return value


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d")


def in_date_range(date_value: datetime | None, since: datetime | None, before: datetime | None) -> bool:
    if date_value is None:
        return True
    if since and date_value < since:
        return False
    if before and date_value >= before:
        return False
    return True


def message_matches(message: Message, keywords: list[str]) -> bool:
    haystack = "\n".join(
        [
            decode_mime(message.get("From")),
            decode_mime(message.get("To")),
            decode_mime(message.get("Cc")),
            decode_mime(message.get("Subject")),
            body_text(message),
        ]
    ).lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def parse_keywords(query: str) -> list[str]:
    return [term for term in re.split(r"\s+", query.strip()) if term]


def read_account_config(config_path: str | None) -> dict[str, str]:
    if not config_path:
        return {}
    parser = configparser.ConfigParser()
    loaded = parser.read(Path(config_path), encoding="utf-8")
    if not loaded:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if "account" not in parser:
        raise ValueError("Config file must include an [account] section.")
    return {key: value.strip() for key, value in parser["account"].items()}
