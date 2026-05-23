# 네이버 메일 설정 매뉴얼

이 문서는 AI agent가 네이버 메일을 POP3 또는 IMAP으로 읽기 전용 검색하기 위해 따라야 하는 설정 매뉴얼입니다.

## 권장 프로토콜

네이버에서 IMAP/SMTP가 활성화되어 있으면 IMAP을 우선 사용합니다.

POP3/SMTP만 활성화되어 있거나 사용자가 POP3 접근만 허용한 상태라면 POP3를 사용합니다.

POP3 설정:

```txt
POP host: pop.naver.com
POP port: 995
보안: SSL/TLS
사용자 이름: 전체 네이버 메일 주소
비밀번호: 네이버 애플리케이션 비밀번호
```

IMAP 설정:

```txt
IMAP host: imap.naver.com
IMAP port: 993
보안: SSL/TLS
사용자 이름: 전체 네이버 메일 주소
비밀번호: 네이버 애플리케이션 비밀번호
```

## 설정 파일 예시

`config/example.ini`를 사용자 소유 경로에 복사한 뒤 값을 채웁니다.

```ini
[account]
address = your-naver-address
password = naver-application-password
pop_host = pop.naver.com
pop_port = 995
imap_host = imap.naver.com
imap_port = 993
```

실제 설정 파일은 저장소 안에 두지 않습니다.

권장 경로:

```txt
C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini
```

## 애플리케이션 비밀번호

네이버는 일반 비밀번호 대신 애플리케이션 비밀번호를 요구할 수 있습니다. 특히 AI agent나 CLI 스크립트처럼 네이버 2단계 인증 화면을 직접 처리하지 않는 클라이언트는 애플리케이션 비밀번호를 사용해야 합니다.

공식 도움말:

<https://help.naver.com/service/5640/contents/8584?lang=ko&osType=COMMONOS>

생성 경로:

```txt
네이버ID > 보안설정 > 기본보안설정 > 2단계 인증 > 관리
```

절차:

1. 네이버 2단계 인증 관리 페이지를 엽니다.
2. 요청되면 네이버 로그인 비밀번호를 입력합니다.
3. `애플리케이션 비밀번호 관리` 항목을 찾습니다.
4. 애플리케이션 종류를 선택하거나 `Email Protocol` 같은 이름을 직접 입력합니다.
5. 생성 버튼을 누릅니다.
6. 생성된 비밀번호를 즉시 복사해 설정 파일의 `password` 값에 입력합니다.

주의:

- 생성된 애플리케이션 비밀번호는 한 번만 표시됩니다.
- 사용하지 않는 애플리케이션 비밀번호는 같은 관리 페이지에서 삭제합니다.
- 2단계 인증을 끄면 기존 애플리케이션 비밀번호도 삭제될 수 있습니다.
- 애플리케이션 비밀번호가 들어 있는 설정 파일을 커밋하거나 공유하지 않습니다.

## 연결 전 검증

POP3 dry-run:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_pop.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query test `
  --dry-run
```

IMAP dry-run:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_imap.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query test `
  --dry-run
```

비밀번호 출력은 반드시 `[set]` 또는 `[not set]` 형태여야 합니다.

## 검색 예시

POP3 검색:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_pop.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query "결제 영수증" `
  --since 2026-05-01 `
  --before 2026-06-01
```

IMAP 검색:

```powershell
python C:\Users\WinUser\plugins\email-protocol\scripts\search_imap.py `
  --config C:\Users\WinUser\Documents\Codex\email-protocol\naver-mail.ini `
  --query "결제 영수증" `
  --since 2026-05-01 `
  --before 2026-06-01
```

## 결제 메일 검색어

결제 내역을 찾을 때 유용한 검색어:

- `결제`
- `영수증`
- `주문`
- `승인`
- `결제정보`
- `합계`
- `네이버 시리즈`
- `쿠키`

지출 합계를 계산할 때는 실제 금액이 있는 결제 또는 영수증 메일만 집계합니다. 광고성 메일, 구매 확정 요청, 단순 알림은 사용자가 포함하라고 요청하지 않는 한 제외합니다.
