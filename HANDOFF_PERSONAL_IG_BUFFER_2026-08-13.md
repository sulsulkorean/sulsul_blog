# Handoff — 개인 인스타 Buffer 자동화

날짜: 2026-08-13  
출발 채팅: SULSUL blog / SNS 캐러셀·Buffer (`sulsul-blog`)  
새 채팅 탭 이름 예: `🟣 jarvis · 개인 IG Buffer 업로드 (Claude)` 또는 `🩷 HQ · 개인 인스타 Buffer (Claude)`

---

## 목표
대표님 **개인 Instagram** 계정을 Buffer에 추가 연결하고, 맥에 있는 **개인 사진**을 골라 업로드/예약할 수 있게 한다.  
(SULSUL `@sulsulapp` 비즈니스 캐러셀 파이프라인과 **분리**해서 진행)

---

## 완료된 것 (SULSUL 쪽 — 이 채팅에서)
- Buffer Free + `@sulsulapp` (Instagram Professional) 연결됨
- `BUFFER_API_TOKEN` / `BUFFER_CHANNEL_ID` → `sulsul-blog/.env.local` (gitignore)
- `publish_buffer_carousel.py` — SULSUL 캐러셀 게시용
- 공항 캐러셀 1개 테스트 게시 완료 (캡션 UTM 이슈 → 규칙 수정, 라이브 글은 인스타 앱에서 수동 수정 필요했음)
- Buffer Free: 채널 **1/3** 사용 → 개인 계정 **+1** 여유 있음

## 이 새 채팅에서 할 일
1. 개인 IG 계정 `@???` 확인 (대표님이 아이디 제공)
2. Buffer Channels에 개인 계정 연결  
   - **프로(크리에이터)** → 자동 게시 가능  
   - **개인** → Buffer 알림 후 폰에서 최종 게시만 되는 경우가 많음
3. 올릴 사진 폴더 경로 확인 (맥)
4. 개인용 업로드 스크립트 또는 기존 Buffer API 재사용  
   - SULSUL 캐러셀 엔진과 **채널/캡션/폴더 분리**
   - `.env.local`에 `BUFFER_PERSONAL_CHANNEL_ID` 등 별도 키 권장 (sulsul 채널과 혼동 금지)
5. 테스트 1장만 올린 뒤 승인 → 확장

## 제약 / 주의
- Buffer Free: 채널 최대 3, 채널당 예약 ~10
- 개인 사진·개인 계정 — 대표님 승인 없이 임의 업로드 금지
- SULSUL `publish_buffer_carousel.py` 기본 채널을 개인으로 바꾸지 말 것
- API 토큰은 채팅에 재붙여넣지 말고 `.env.local`만 사용 (이미 있음)

## 참고 파일
- `SULSUL_앱개발/sulsul-blog/INSTAGRAM_BUFFER_SETUP.md`
- `SULSUL_앱개발/sulsul-blog/publish_buffer_carousel.py`
- Buffer Channels: https://account.buffer.com/channels
- Buffer API settings: https://publish.buffer.com/settings/api

## 새 채팅 첫 메시지 (복사용)

```
@INSTAGRAM_BUFFER_SETUP.md @publish_buffer_carousel.py
핸드오프: docs 대신 이 파일 기준 — 개인 인스타 Buffer 자동화
목표: 개인 IG를 Buffer에 연결하고, 맥 사진 폴더에서 골라 업로드
SULSUL sulsulapp 채널과 분리. Free 1/3 사용 중. BUFFER_API_TOKEN은 .env.local에 있음.
개인 @아이디 / 사진 폴더 경로 / 프로 전환 여부(A 자동 vs B 알림) 확인 후 진행.
```

(또는 HQ에서: `@docs/HQ_CHAT_RULES.md` + 위 요약)
