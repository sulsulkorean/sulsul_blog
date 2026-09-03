# [내쪽에서 해줘야 하는일] 인스타 자동 게시 — 토큰 세팅

> **2026-08-05 경로 변경:** Meta 개발자 등록이 계정 보안으로 막혀 **Buffer 무료**로 우회합니다.  
> 지금 하실 일 → [`INSTAGRAM_BUFFER_SETUP.md`](./INSTAGRAM_BUFFER_SETUP.md)  
> 아래 Meta 직접 API 안내는 **나중에** (개발자 등록이 풀린 뒤) 용입니다.

목표: `@sulsulapp`에 **테스트 캐러셀 1개**만 올릴 수 있게 Meta 권한을 맥에 연결합니다.  
실제 게시는 토큰이 들어온 뒤, 제가 dry-run → `--publish` 순으로 실행합니다.

---

## 진행 체크

| # | 할 일 | 상태 |
|---|--------|------|
| 1 | 인스타를 프로(비즈니스/크리에이터)로 확인 | ⬜ |
| 2 | 페이스북 페이지와 연결 | ⬜ |
| 3 | Meta 앱 만들기 | ⬜ |
| 4 | Graph API로 토큰 + IG 계정 ID 받기 | ⬜ |
| 5 | `.env.local`에 두 줄 넣기 (또는 채팅에 전달) | ⬜ |
| 6 | 저에게 “토큰 넣었어” 라고 알리기 | ⬜ |

---

## 1) 인스타 계정 유형 확인

왜: Meta API는 **개인 계정**에 글을 못 올립니다. 프로 계정만 됩니다.

1. 폰에서 Instagram 앱 → `@sulsulapp` 로그인
2. 프로필 → 右上 **☰** → **설정 및 활동**
3. **계정 유형 및 도구** (또는 **계정**) 확인
4. **프로페셔널 계정**이면 OK  
   - 아니면 **프로페셔널 계정으로 전환** → **비즈니스** 또는 **크리에이터** 선택

**성공 확인:** 설정에 프로페셔널/비즈니스/크리에이터로 표시됨

---

## 2) 페이스북 페이지와 연결

왜: 가장 안정적인 게시 방식(Facebook Login + Graph API)은 **페이스북 페이지 ↔ 인스타** 연결이 필요합니다.

1. 인스타 → 설정 → **계정 유형 및 도구** → **페이지** (또는 Meta Business Suite)
2. `@sulsulapp`을 SULSUL용 페이스북 페이지에 연결  
   - 페이지가 없으면 [Facebook Pages](https://www.facebook.com/pages/create)에서 SULSUL 페이지 생성 후 연결

**성공 확인:** 인스타 설정에 연결된 페이스북 페이지 이름이 보임

---

## 3) Meta 개발자 앱 만들기 (클릭 경로 상세)

왜: 인스타에 “프로그램이 대신 올려도 된다”고 Meta에 등록하려면 **앱 1개**가 필요합니다.  
개발 모드면 **본인 계정/페이지**만 가능 — 테스트 1개에는 충분합니다.

연결된 SULSUL 페이스북 페이지:  
[SULSUL Facebook Page](https://www.facebook.com/profile.php?id=61592891100386)

### 3-0. 개발자 계정 (처음 한 번만)

1. 맥 브라우저에서 [Meta for Developers](https://developers.facebook.com/) 접속
2. 오른쪽 위 **로그인** — SULSUL 페이스북에 쓰는 **같은 계정**으로 로그인
3. 처음이면 **시작하기 / Get Started** → 전화번호·직업 등 물어보면 대충 채우고 완료  
   - “개발자가 아닙니다” 같은 안내가 나오면 **등록**을 눌러 개발자로 전환

**성공 확인:** 상단에 **내 앱 / My Apps** 메뉴가 보임

### 3-1. 앱 만들기

1. [앱 목록](https://developers.facebook.com/apps/) 접속  
   또는 상단 **내 앱** 클릭
2. 오른쪽 위 초록/파란 버튼 **앱 만들기 (Create App)** 클릭  
   - 직접 주소: [앱 만들기](https://developers.facebook.com/apps/creation/)
3. **사용 사례(Use case)** 화면이 나오면:
   - 목록을 아래로 스크롤
   - **기타 (Other)** 선택  
   - **다음 (Next)**
4. **앱 유형** 화면:
   - **비즈니스 (Business)** 선택  
     (Consumer/소비자 고르면 토큰·게시가 막힐 수 있음)
   - **다음 (Next)**
5. **앱 세부정보**:
   - **앱 이름:** `SULSUL Instagram Publisher`
   - **앱 연락처 이메일:** 본인 이메일 (자동으로 들어가 있으면 그대로)
   - **비즈니스 포트폴리오:** 있으면 SULSUL 관련 것 선택 / 없으면 **나중에 연결** 또는 **연결하지 않음** 가능 (테스트는 나중에 해도 됨)
6. **앱 만들기 (Create app)** 클릭  
   - 비밀번호·2단계 인증 물어보면 입력

**성공 확인:** 화면이 **앱 대시보드**로 바뀌고, 왼쪽 위에 `SULSUL Instagram Publisher` 이름이 보임

막히면 자주 나오는 경우:
| 화면/문구 | 대처 |
|-----------|------|
| 사용 사례만 잔뜩 있고 Other가 안 보임 | 맨 아래까지 스크롤 → **Other / 기타** |
| Business Verification 강요 | **나중에** / Skip 비슷한 버튼으로 통과 (테스트 단계는 보통 가능) |
| “앱을 만들 수 없음” | 같은 페이스북 계정인지, 다른 브라우저(크롬)로 재시도 |

### 3-2. 제품 추가 (Instagram + Facebook Login)

앱 대시보드 왼쪽 메뉴에서:

1. **제품 추가 (Add product)** 또는 **제품 (Products)** 클릭  
   (왼쪽 맨 아래·중간에 있음)
2. 카드 목록에서 **Instagram** 찾기 → **설정 / Set up** 클릭  
   - 하위 옵션이 나오면: **API setup with Facebook login**  
     (페이스북 페이지에 인스타가 연결된 우리 방식)
3. 다시 **제품 추가** → **Facebook Login** 또는 **Facebook Login for Business** → **설정 / Set up**  
   - 웹 설정 화면이 나와도, 지금은 URL을 꼭 채울 필요 없음 (토큰은 Graph Explorer로 받음) → 대시보드로 돌아가면 됨

**성공 확인:** 왼쪽 메뉴에 **Instagram**, **Facebook Login** 이 각각 보임

여기까지 되면 **3단계 완료**. 이어서 문서 **4) 토큰 + 인스타 계정 ID 받기**로 가면 됩니다.

---

## 4) 토큰 + 인스타 계정 ID 받기

왜: 스크립트가 “어느 계정에 / 어떤 권한으로” 올릴지 이 두 값이 있어야 합니다.

### 4-A. Graph API Explorer로 토큰 발급

1. [Graph API Explorer](https://developers.facebook.com/tools/explorer/) 접속
2. 右上 **Meta 앱** = 방금 만든 `SULSUL Instagram Publisher` 선택
3. **권한 추가(Add a Permission)** 에서 아래를 추가 후 **Generate Access Token**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
4. 페이스북이 권한 창을 띄우면 **SULSUL 페이지** + **인스타** 접근을 허용

**성공 확인:** Explorer 입력칸에 긴 Access Token 문자열이 생김

### 4-B. 인스타 비즈니스 계정 ID 확인

Explorer에 아래를 넣고 **Submit**:

```
me/accounts?fields=name,access_token,instagram_business_account
```

응답에서:

- 페이지의 `access_token` → 이게 **페이지 토큰** (게시용으로 더 안정적)
- `instagram_business_account.id` → 이게 **IG_USER_ID**

페이지 토큰이 보이면 그걸 쓰고, 안 보이면 4-A에서 받은 유저 토큰으로도 시도할 수 있습니다.

### 4-C. (권장) 장기 토큰으로 바꾸기

짧은 토큰은 몇 시간 만에 만료됩니다.

1. [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) 접속
2. 토큰 붙여넣기 → **Debug**
3. **Extend Access Token** 이 있으면 눌러 장기 토큰(약 60일)으로 연장
4. 연장된 값을 복사

**성공 확인:** Debugger에 만료일이 수십 일 뒤로 표시됨

---

## 5) 맥 `.env.local`에 넣기

파일 위치 (블로그 프로젝트 루트):

`SULSUL_앱개발/sulsul-blog/.env.local`

아래 **두 줄**을 추가합니다. (`OPENAI_API_KEY` 줄은 그대로 두세요.)

```bash
IG_USER_ID=여기에_instagram_business_account_id
IG_ACCESS_TOKEN=여기에_장기_토큰_또는_페이지_토큰
```

선택(기본값 그대로 둬도 됨):

```bash
IG_GRAPH_VERSION=v22.0
IG_GRAPH_HOST=graph.facebook.com
```

**성공 확인:** 파일에 `IG_USER_ID`, `IG_ACCESS_TOKEN` 두 키가 보임 (값을 채팅에 붙여 넣으셔도 됩니다. 제가 `.env.local`에 넣어 드립니다.)

---

## 6) 저에게 알리기

채팅에 이렇게만 보내 주세요:

> 토큰 넣었어. 공항 캐러셀로 dry-run 해줘.

그러면 제가:

1. dry-run으로 캡션·이미지 6장 확인  
2. 문제 없으면 **공항(`ig-airport-check-in-korean`) 1개만** `--publish`  
3. 인스타 앱에서 피드에 올라왔는지 확인 방법 안내  

**5개 연속 게시는 이번 승인 범위 밖입니다.** 테스트 1개 성공 후 따로 요청해 주세요.

---

## 자주 막히는 지점

| 증상 | 해결 |
|------|------|
| 개인 계정이라 API 거절 | 1단계 프로 전환 |
| `instagram_business_account` 가 null | 2단계 페이지 연결 다시 |
| `(#10) Application does not have permission` | Explorer에서 권한 다시 추가·토큰 재발급 |
| 이미지 URL 오류 | 제가 스크립트에서 임시 공개 URL로 올립니다. 대표님 추가 작업 없음 |
