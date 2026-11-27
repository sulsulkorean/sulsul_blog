export const SITE_NAME = "SULSUL Korean";

export const SITE_TAGLINE = "Speak Korean in Seoul — not just study it";

export const SITE_DESCRIPTION =
  "Survival Korean you can actually say out loud: real phrases for cafes, taxis, convenience stores and small talk, with romanization and when to use each one.";

/** Set NEXT_PUBLIC_SITE_URL in Vercel to the live blog domain. */
export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://blog.sulsul.app"
).replace(/\/$/, "");

export const APP_URL = "https://sulsul.app";

/** 대표님 1:1 과외 (Preply) — 2026-11-27 대표님 지시. 주소가 바뀌면 여기만. */
export const TUTOR_URL = "https://preply.in/st6ItHcH?ts=17957726";

/**
 * 랜딩 첫 화면의 «10초 말하기 체험» 칸 (LandingPage.tsx의 id="demo-section").
 * 마이크로 «물 주세요» 한 줄을 말해 보는 칸이고 가입이 필요 없다.
 * 앱 쪽에서 칸 id가 바뀌면 여기만 고친다.
 */
export const APP_DEMO_URL = "https://sulsul.app/#demo-section";

export const appLink = (campaign: string) =>
  `${APP_URL}/?utm_source=blog&utm_medium=${campaign}&utm_campaign=seo`;

export const DEFAULT_COVER_IMAGE = "/assets/blog/covers/start-speaking.png";

export const DEFAULT_AUTHOR = {
  name: "Yona",
  picture: "/assets/blog/authors/yona.png",
};

export const AUTHOR_BIO =
  "Yona is the founder of SULSUL, a Korean speaking app built around 100 survival patterns after years of watching learners memorise grammar tables and still order in English in Seoul.";
