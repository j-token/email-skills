---
name: email-protocol
description: Search and inspect email accounts through provider-supported POP3 or IMAP. Use when the user asks to search a non-Gmail mailbox, connect provider email by protocol, or inspect payment and receipt emails from Naver or another provider.
---

# Email Protocol

## Scope

This plugin is read-only by default. It supports mailbox lookup and search through:

- POP3 over SSL/TLS
- IMAP over SSL/TLS

It does not provide SMTP sending.

## Choosing POP3 or IMAP

Prefer IMAP when available. IMAP can search folders and preserve server-side mailbox structure.

Use POP3 when the provider only exposes POP settings or when the user has already enabled POP. POP usually inspects the provider's POP-accessible inbox and is less suitable for folder-wide historical search.

## Configuration File

Prefer a user-owned configuration file. Do not store real passwords in the plugin directory unless the user explicitly chooses to.

For first-time setup, create a config file and open it for the user:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\init_config.py --provider naver --open
```

Use `config/example.ini` as the manual template. The search scripts accept:

- `--config C:\path\to\mail.ini`

The config file has one `[account]` section with shared credentials and protocol-specific host settings.

## Scripts

POP3 search:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_pop.py --config C:\Users\WinUser\mail.ini --query "receipt payment"
```

IMAP search:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_imap.py --config C:\Users\WinUser\mail.ini --query "receipt payment"
```

Both scripts accept:

- `--address`, `--password`, `--host`, and `--port` to override config file values.
- `--since YYYY-MM-DD`
- `--before YYYY-MM-DD`
- `--limit N`
- `--dry-run` to validate resolved settings without connecting.

POP also accepts `--scan-limit N` to cap how many newest messages are downloaded and inspected.

IMAP also accepts repeated `--folder`.

## Windows Console Encoding

Provider emails may contain Korean text, emoji, variation selectors, HTML fragments, and other characters that fail under the Windows default `cp949` console encoding.

All scripts that print email-derived text must configure stdout before printing:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

When adding or modifying scripts:

- Keep output UTF-8 with replacement for unsupported characters.
- Do not assume the terminal is already UTF-8.
- Avoid crashing on display-only encoding errors; unreadable characters may be replaced.
- Keep secrets out of logs and never print raw passwords.

## Provider Manuals

Use provider manuals when the user names a service:

- Naver: `manuals/naver.md`

If a provider blocks POP/IMAP or requires OAuth/app passwords, explain that the provider's security settings must be enabled first.

For Naver specifically, explain that POP3/IMAP access requires a Naver application password when using protocol clients. Point the user to `manuals/naver.md`, which includes the official Naver help link and the current creation path:

```txt
네이버ID > 보안설정 > 기본보안설정 > 2단계 인증 > 관리
```
