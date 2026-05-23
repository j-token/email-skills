# Email Protocol

Email Protocol은 AI가 사용자의 메일함을 POP3 또는 IMAP으로 읽기 전용 검색할 수 있게 해주는 도구입니다.

이 저장소는 두 가지 설치 방식을 지원합니다.

- Codex 플러그인 방식: 저장소 전체를 Codex 플러그인으로 설치합니다.
- Skill 단독 방식: `email-protocol` skill만 설치하고, 스크립트와 매뉴얼은 이 저장소를 기준 경로로 사용합니다.

## AI 전용 설치 매뉴얼

이 문서는 사람이 직접 따라 하는 일반 사용자 설명서가 아니라, AI agent가 사용자의 로컬 환경에 설치하거나 운영할 때 따라야 하는 매뉴얼입니다.

필수 규칙:

- 원본 비밀번호, 앱 비밀번호, 쿠키, 전체 credential 파일 내용을 출력하지 않습니다.
- 실제 계정 설정 파일은 이 저장소 안에 두지 않습니다.
- 권장 설정 경로는 `C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini`처럼 사용자 소유 경로입니다.
- 최초 네트워크 연결 전에는 반드시 `--dry-run`으로 설정 해석을 확인합니다.
- IMAP이 가능하면 IMAP을 우선 사용합니다. 제공자가 POP3만 제공하거나 사용자가 POP3만 활성화한 경우 POP3를 사용합니다.
- Git 저장소는 하나만 둡니다. `skills`, `scripts`, `manuals` 아래에 별도 `.git`을 만들지 않습니다.

## 저장소 구조

```txt
.agents/plugins/marketplace.json  GitHub marketplace manifest
.codex-plugin/plugin.json       Codex 플러그인 manifest
docs/mail-search-ux.md          대량 메일 조회 UX 개선 설계
skills/email-protocol/SKILL.md  Codex skill 지시문
scripts/init_config.py          사용자 소유 설정 파일 생성 도구
scripts/search_imap.py          IMAP SSL/TLS 메일함 검색
scripts/search_pop.py           POP3 SSL/TLS 메일함 검색
scripts/mail_common.py          메일 파싱 공통 함수
config/example.ini              안전한 설정 템플릿
manuals/naver.md                네이버 POP3/IMAP 설정 매뉴얼
```

## 설치 방법 1: Codex 플러그인

Codex가 플러그인, skill, 매뉴얼, 스크립트를 함께 발견해야 할 때 이 방식을 사용합니다.

GitHub marketplace로 추가할 때는 repo 루트의 `.agents/plugins/marketplace.json`을 사용합니다. 이 repo는 루트가 곧 `email-protocol` plugin 루트이므로 marketplace entry의 `source.path`는 `./`입니다.

권장 설치 경로:

```txt
C:\Users\WinUser\plugins\email-protocol
```

`C:\Users\WinUser\.agents\plugins\marketplace.json`에 다음 entry가 있어야 합니다.

```json
{
  "name": "email-protocol",
  "source": {
    "source": "local",
    "path": "./plugins/email-protocol"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

플러그인 구조를 검증합니다.

```powershell
python C:\Users\WinUser\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\WinUser\plugins\email-protocol
```

설치 후 Codex는 다음 skill을 사용할 수 있어야 합니다.

```txt
C:\Users\WinUser\plugins\email-protocol\skills\email-protocol\SKILL.md
```

## 설치 방법 2: Skill 단독

AI 환경이 로컬 플러그인을 지원하지 않고 skill만 지원할 때 이 방식을 사용합니다.

저장소는 안정적인 경로에 둡니다.

```txt
C:\Users\WinUser\plugins\email-protocol
```

skill 디렉터리를 Codex skill 경로로 복사합니다.

```powershell
Copy-Item -Recurse -Force `
  C:\Users\WinUser\plugins\email-protocol\skills\email-protocol `
  C:\Users\WinUser\.codex\skills\email-protocol
```

Skill 단독 설치에서도 스크립트는 이 저장소의 파일을 호출해야 합니다.

```txt
C:\Users\WinUser\plugins\email-protocol\scripts
```

Windows가 아닌 환경에서는 저장소를 clone한 실제 경로에 맞춰 `SKILL.md` 안의 스크립트 경로를 수정합니다.

## 계정 설정

설정 파일은 사용자 소유 경로에 만듭니다.

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\init_config.py --provider naver --open
```

설정 파일은 하나의 `[account]` 섹션을 사용합니다.

```ini
[account]
address = user@example.com
password = provider-application-password
pop_host = pop.example.com
pop_port = 995
imap_host = imap.example.com
imap_port = 993
```

네이버는 프로토콜 접근을 활성화하고 애플리케이션 비밀번호를 만들어야 합니다.

```txt
manuals/naver.md
```

## 검증

POP3 설정을 연결 없이 검증합니다.

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_pop.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query test `
  --dry-run
```

IMAP 설정을 연결 없이 검증합니다.

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_imap.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query test `
  --dry-run
```

비밀번호 출력은 다음 형태여야 합니다.

```txt
Password: [set]
```

`--dry-run`에서 실제 비밀번호가 출력되면 설치를 중단하고 스크립트를 수정해야 합니다.

## 검색 예시

IMAP 검색:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_imap.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query "결제 영수증" `
  --since 2026-05-01 `
  --before 2026-06-01
```

POP3 검색:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_pop.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query "네이버 시리즈 쿠키 결제" `
  --since 2026-05-01 `
  --before 2026-06-01 `
  --scan-limit 1000
```

## Git 정책

이 디렉터리가 Email Protocol의 유일한 Git 저장소입니다.

다음 위치에는 `.git`을 만들지 않습니다.

- `skills/email-protocol`
- `scripts`
- `manuals`
- 사용자 설정 파일 디렉터리

실제 계정 설정 파일은 커밋하지 않습니다. 템플릿, 스크립트, skill, 매뉴얼만 커밋합니다.
