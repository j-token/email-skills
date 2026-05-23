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

## Large Mailbox Search UX

사용자가 대량 메일함 검색을 요청하면 많은 메일 본문을 먼저 내려받지 않는다. `docs/mail-search-ux.md`의 UX 정책을 따른다.

기본 흐름:

1. 빠른 검색으로 시작한다.
2. 본문 검사 전에 날짜 범위, 발신자, 제목으로 후보를 줄인다.
3. IMAP에서는 가능한 한 서버 `SEARCH` 조건을 우선 사용한다.
4. POP3에서는 provider가 지원하면 `TOP` 기반 헤더 우선 스캔을 사용한다.
5. 전체 본문은 후보 메일에만 다운로드한다.
6. 검색이 몇 초 이상 걸리면 진행 상황을 보고한다.
7. 첫 검색 결과가 부족하거나 사용자가 전체 검색을 요청할 때만 범위를 확장한다.

검색 모드:

- 빠른 검색: 후보를 먼저 줄이고 후보 본문만 검사한다.
- 확장 검색: `--scan-limit`, 폴더 범위, 날짜 범위를 넓힌다.
- 정밀 검색: 더 많은 후보 본문을 검사하고 본문 키워드 매칭을 적용한다.

보안 정책:

- 로컬 메일함 캐시는 추가하지 않는다.
- 메일 제목, 발신자, snippet, 본문, 추출 금액을 DB나 파일에 영구 저장하지 않는다.
- 검색 중에는 현재 프로세스 메모리의 후보와 hit 객체만 임시로 유지한다.
- 비밀값은 로그에 남기지 않고 원본 비밀번호를 출력하지 않는다.

PDF 첨부 요청:

- 사용자가 PDF 첨부 목록이나 다운로드 가능 여부를 묻는 경우 `docs/mail-search-ux.md`의 `PDF 첨부 조회와 다운로드 매뉴얼`을 따른다.
- IMAP이 가능하면 `BODYSTRUCTURE`로 첨부 구조만 먼저 조회한다.
- IMAP이 비활성화되어 있으면 POP3 `TOP`으로 후보를 찾고 후보 메일에만 `RETR`를 사용한다.
- 사용자가 명시적으로 다운로드를 요청하기 전에는 PDF 파일을 저장하지 않는다.
- 다운로드가 요청되면 Git 저장소 밖의 사용자 소유 경로에 저장하고, 저장 전 `%PDF` 헤더를 검증한다.

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
