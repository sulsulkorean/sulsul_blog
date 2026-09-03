# [내쪽에서 해줘야 하는일] Buffer — 이제 3가지만

제가 **게시 스크립트·브라우저 가입 화면**까지 준비해 두었습니다.  
비밀번호·인스타 권한은 Meta/Buffer가 **본인만** 누르게 되어 있어서, 아래 3개만 해 주시면 됩니다.

| # | 하실 일 | 링크 |
|---|---------|------|
| 1 | Buffer **무료 가입** (이메일+비번 또는 이미 있으면 로그인) | 지금 Cursor에 열린 가입 화면, 또는 [가입](https://login.buffer.com/signup) |
| 2 | **Instagram `@sulsulapp`** 채널 연결 (Professional / 권한 허용) | [Channels](https://account.buffer.com/channels) |
| 3 | **API 키** 만들어서 채팅에 붙여넣기 (또는 `.env.local`) | [Buffer API 설정](https://publish.buffer.com/settings/api) |

채팅에 이렇게만 보내 주세요:

```
BUFFER_API_TOKEN=여기에_키
```

그다음 제가 공항 캐러셀 1개 dry-run → `--publish` 합니다.

유료 화면 나오면 **Skip / Free** — 카드 넣지 마세요.

---

# (아래는 상세 클릭 경로 — 막힐 때만)

목표: Meta 개발자 앱 없이, **Buffer 무료**로 `@sulsulapp`에 캐러셀을 자동 게시할 수 있게 만듭니다.  
첫 테스트는 **공항 캐러셀 1개**만.

관련 폴더 (맥):  
`SULSUL_앱개발/sulsul-blog/obsidian_data/4.Repurposed/ig-airport-check-in-korean/`  
→ `01.png` ~ `06.png` + `caption.txt`

페이스북 페이지(참고): [SULSUL Facebook](https://www.facebook.com/profile.php?id=61592891100386)

---

## 전체 체크

| # | 할 일 | 상태 |
|---|--------|------|
| 0 | 인스타가 프로(비즈니스/크리에이터)인지 확인 | ⬜ |
| 1 | Buffer 계정 만들기 (무료) | ⬜ |
| 2 | 유료로 업셀 나오면 Free / Skip | ⬜ |
| 3 | `@sulsulapp` 인스타 채널 연결 | ⬜ |
| 4 | 자동 게시(Automatic)인지 확인 | ⬜ |
| 5 | (선택) 공항 캐러셀 1개 예약/게시 테스트 | ⬜ |
| 6 | 저에게 「Buffer 연결됐어」 알리기 | ⬜ |

---

## 0) 인스타 계정 유형 확인 (1분)

왜: 개인 계정이면 Buffer가 **자동 게시**를 못 하고, 폰 알림만 뜹니다.

1. 폰 **Instagram** 앱 → `@sulsulapp` 으로 로그인
2. 아래 **프로필** → 右上 **☰** → **설정 및 활동**
3. **계정 유형 및 도구** (또는 **계정 센터** 안의 계정 유형)
4. **프로페셔널 / 비즈니스 / 크리에이터** 이면 OK  
   - 아니면 **프로페셔널 계정으로 전환** → **비즈니스** 또는 **크리에이터** → 카테고리는 Education / App 등 아무거나

**성공 확인:** 설정에 Professional / Business / Creator 로 보임

---

## 1) Buffer 계정 만들기

왜: Buffer가 이미 Meta 검수를 받은 앱이라, 대표님은 **인스타 연결만** 하면 됩니다.

1. 맥 브라우저(Chrome 권장)에서 [Buffer 가입](https://buffer.com/) 접속  
   - 또는 직접: [https://login.buffer.com/signup](https://login.buffer.com/signup)
2. **Sign up free** / **Get started for free** 클릭
3. 가입 방법 중 하나:
   - **Continue with Google** (제일 쉬움), 또는
   - 이메일 + 비밀번호
4. 이메일은 `korean@sulsul.app` 또는 평소 쓰는 메일 아무거나 OK

**성공 확인:** Buffer 안(캘린더/Create Post 화면)으로 들어감

---

## 2) 유료 권유 나오면 — 무료로 남기기

왜: 가입·연결 중에 Essentials 유료 트라이얼을 권하는 화면이 자주 뜹니다. **지금 필요 없습니다.**

다음 중 보이면:

| 문구 예 | 할 일 |
|---------|--------|
| Start free trial / Try Essentials | **Skip** / **Maybe later** / **Continue with Free** |
| Choose a plan | **Free** 선택 |
| Add card | **닫기** — 카드 넣지 말 것 |

**성공 확인:** 요금제에 **Free** 라고 보이거나, 결제 카드 없이 채널 연결 화면까지 감  
(확인: [Buffer 계정·요금](https://account.buffer.com/settings) 또는 왼쪽 아래 계정 메뉴)

무료 한도 기억:
- 채널 **최대 3개**
- 채널당 **예약 대기 약 10개**
- 하루 개수 제한 없음 (예약 슬롯만 10개)

---

## 3) @sulsulapp 인스타 연결 (가장 중요)

왜: 이 한 번만 되면 이후 글은 Buffer(또는 나중에 제가 만든 스크립트)로 올라갑니다.

### 3-A. 브라우저에 인스타 먼저 로그인

1. **새 탭**에서 [instagram.com](https://www.instagram.com/) 접속
2. **`@sulsulapp` 계정**으로 로그인  
   - 개인 인스타가 열려 있으면 **전환** 또는 로그아웃 후 sulsulapp으로
3. 피드가 보이면 탭은 **그대로 열어 두기**

**성공 확인:** 브라우저에서 sulsulapp 프로필이 보임

### 3-B. Buffer에서 채널 연결

1. [Buffer 채널 페이지](https://account.buffer.com/channels) 접속  
   - 안 열리면 Buffer 로그인 후 왼쪽/상단 **Channels** / **채널**
2. **Connect a Channel** / **Connect Channel** / **+** 클릭
3. **Instagram** 선택
4. **Professional** (비즈니스/크리에이터) 쪽 연결 선택  
   - 문구 예: **Connect to Instagram** under Professional  
   - **Personal** 로 연결하지 말 것 (자동 게시 안 됨)
5. 인스타/Meta 로그인·권한 창이 뜨면:
   - `@sulsulapp` 선택
   - **모든 권한 허용** (게시, 인사이트 등) → **Allow / 허용**
6. Buffer로 돌아오면 채널 목록에 **Instagram · sulsulapp**(또는 프로필 사진)이 생김

페이스북 페이지로 연결하라는 선택지가 있으면:
- 가능하면 **Instagram 로그인(Professional)** 이 무료·자동게시에 더 단순
- 막히면 **Facebook Page** 방식 → [SULSUL 페이지](https://www.facebook.com/profile.php?id=61592891100386) 관리자 계정으로 허용

**성공 확인:** [Channels](https://account.buffer.com/channels) 에 Instagram `@sulsulapp` 이 보임

막힐 때:
| 증상 | 대처 |
|------|------|
| 다른 인스타가 연결됨 | instagram.com에서 sulsulapp으로 바꾼 뒤 Buffer에서 **Reconnect** |
| Personal만 됨 | 0단계 프로 전환 후 다시 Connect |
| 권한 오류 | Channels → 인스타 옆 **⋯** → **Reconnect** / **Refresh** |

---

## 4) 자동 게시인지 확인

왜: “알림만 오는” 연결이면 폰에서 마지막 버튼을 또 눌러야 해서, 원하던 자동이 아닙니다.

1. [Channels](https://account.buffer.com/channels) 에서 `@sulsulapp` 클릭 또는 옆 **⋯**
2. Publishing / connection 상태에 **Automatic publishing** / **자동 게시** 가 있는지 확인  
   - Notification only / 알림 게시면 → **Reconnect** 로 Professional 다시 연결

**성공 확인:** Automatic publishing 가능이라고 표시됨

---

## 5) (선택) 공항 캐러셀 1개 — Buffer 화면에서 테스트

왜: 연결이 진짜 되는지 한 번만 확인. (원하시면 이 단계는 제가 API 연동 후 대신해도 됩니다.)

### 5-A. 사진을 맥에서 준비

Finder에서 이 폴더 열기:

`SULSUL_앱개발` → `sulsul-blog` → `obsidian_data` → `4.Repurposed` → `ig-airport-check-in-korean`

파일: `01.png` … `06.png`, `caption.txt`

### 5-B. Buffer에서 새 글

1. [Buffer 작성](https://publish.buffer.com/) 접속 (또는 **New Post** / **Create Post**)
2. 채널에서 **Instagram · sulsulapp** 선택
3. **이미지 여러 장** 업로드: `01` → `02` → … → `06` **순서대로**
4. `caption.txt` 내용 전부 복사해서 캡션 칸에 붙여넣기
5. 아래 중 하나:
   - **Share Now** / **지금 공유** → 바로 피드에 올림 (테스트용)
   - 또는 **Schedule** → 몇 분 뒤로 예약

**성공 확인:** 폰 Instagram `@sulsulapp` 피드에 사진 6장짜리 캐러셀 + 캡션/해시태그가 보임

---

## 6) 저에게 알리기

채팅에 이렇게 보내 주세요:

> Buffer 연결됐어. (자동 게시 OK / 테스트 올렸음 or 아직 안 올림)

그다음 제가 할 일:
1. Buffer API로 “폴더 → 캐러셀 업로드” 스크립트 연결 (승인 후)
2. 나머지 캐러셀도 같은 방식으로 올릴 수 있게 정리

---

## Meta 개발자 앱은?

지금은 **안 해도 됩니다.**  
`INSTAGRAM_PUBLISH_SETUP.md` 의 Meta 앱/토큰은 **보류**.  
나중에 Buffer 수수료·한도가 답답하면 그때 다시 직접 API로 가면 됩니다.
