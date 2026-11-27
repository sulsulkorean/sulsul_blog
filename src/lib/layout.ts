/**
 * 글 한 편의 «모양»을 읽을 때 한 번에 잡는다. 원고(_posts/*.md)는 건드리지 않는다.
 *
 * 2026-11-25 대표님 지시 — 「가독성이 너무 떨어져, 열자마자 나간다」.
 * 상위 언어 블로그 9곳을 열어 재 보니 차이는 길이가 아니라 «끊는 횟수»였다:
 *   문단 중간값  우리 39단어 / 상위 16~30단어   (StoryLearning은 60단어 넘는 문단이 0개)
 *   소제목 간격  우리 175단어 / 상위 51~103단어
 *   본문 크기    우리 18px   / 상위 19~20px
 * 원고를 다시 쓰지 않고 할 수 있는 것만 여기서 한다.
 */

/** 이 길이를 넘는 문단은 문장 경계에서 쪼갠다. 상위 블로그 문단 중간값이 16~30단어다 (StoryLearning 29 · 최장 55). */
const MAX_WORDS = 45;
/** 쪼갠 조각이 이보다 짧으면 쪼개지 않는다 — 한 줄짜리 토막이 생기는 걸 막는다. */
const MIN_WORDS = 15;

const words = (s: string) => (s.replace(/<[^>]+>/g, " ").match(/\S+/g) || []).length;

/** 인라인 태그 밖에 있는 «문장 끝» 위치(html 인덱스)를 모은다. */
function sentenceEnds(html: string): number[] {
  // 1. 글자만 뽑아내면서 html 위치를 같이 들고 간다. 태그 안은 글자가 아니다.
  const chars: string[] = [];
  const at: number[] = [];
  const depthAt: number[] = [];
  let inTag = false;
  let depth = 0;
  for (let i = 0; i < html.length; i++) {
    const c = html[i];
    if (c === "<") {
      inTag = true;
      const close = html[i + 1] === "/";
      // <br> <img> 같은 홀태그는 깊이를 바꾸지 않는다 — 전에는 이걸 세어서 뒤쪽이 통째로 막혔다.
      const name = (html.slice(i + 1).match(/^\/?([a-zA-Z0-9]+)/) || [, ""])[1].toLowerCase();
      if (!["br", "img", "hr", "wbr"].includes(name)) depth += close ? -1 : 1;
      continue;
    }
    if (c === ">") {
      inTag = false;
      continue;
    }
    if (inTag) continue;
    chars.push(c);
    at.push(i);
    depthAt.push(depth);
  }

  // 2. 글자 위에서 문장 끝을 찾는다. 닫는 따옴표·괄호까지 한 덩어리로 넘긴다.
  const text = chars.join("");
  const ABBR = /(?:^|\s)(?:mr|mrs|ms|dr|st|vs|e\.g|i\.e|etc|no|fig|approx)$/i;
  const out: number[] = [];
  const re = /[.!?]+["”’')\]]*(?=\s)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const endsAt = m.index + m[0].length; // 구두점 바로 뒤
    if (ABBR.test(text.slice(Math.max(0, m.index - 8), m.index))) continue;
    // 다음 문장이 대문자·한글·따옴표로 시작해야 한다 (소수점·번호 매기기 거르기)
    if (!/^\s+["“(]?[A-Z가-힣]/.test(text.slice(endsAt, endsAt + 4))) continue;
    if (depthAt[endsAt - 1] !== 0) continue; // 굵은 글씨 «안»에서는 자르지 않는다
    out.push(at[endsAt - 1] + 1);
  }
  return out;
}

/** 한 문단을 55단어 이하 조각들로 나눈다. 자를 자리가 없으면 그대로 둔다. */
function split(inner: string): string[] {
  if (words(inner) <= MAX_WORDS) return [inner];
  const ends = sentenceEnds(inner);
  const half = inner.length / 2;
  let best = -1;
  for (const point of ends) {
    if (words(inner.slice(0, point)) < MIN_WORDS) continue;
    if (words(inner.slice(point)) < MIN_WORDS) continue;
    if (best < 0 || Math.abs(point - half) < Math.abs(best - half)) best = point;
  }
  if (best < 0) return [inner];
  return [
    ...split(inner.slice(0, best).trim()),
    ...split(inner.slice(best).trim()),
  ];
}

const slug = (s: string) =>
  s
    .replace(/<[^>]+>/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9가-힣]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);

export type Prepared = {
  /** 본문 — 긴 문단은 쪼개지고 h2에는 id가 붙었다. */
  html: string;
  /** 맨 위 요약 상자로 올릴 내용. 286편 전부가 이미 갖고 있다(지금은 그냥 본문처럼 보인다). */
  lead: string | null;
  /** 목차 — h2에서 자동으로 만든다. */
  toc: { id: string; text: string }[];
  /** 읽는 시간(분) — 분당 230단어. */
  minutes: number;
};

export function prepareBody(html: string): Prepared {
  const minutes = Math.max(1, Math.round(words(html) / 230));

  // 1. 첫 인용 블록을 떼어 맨 위 «답 상자»로 쓴다.
  let lead: string | null = null;
  html = html.replace(/<blockquote>([\s\S]*?)<\/blockquote>\s*/, (m, inner) => {
    if (lead !== null) return m;
    lead = inner.trim();
    return "";
  });

  // 2. 긴 문단 쪼개기. 속성이 붙은 <p class="mid-cta">는 건드리지 않는다.
  html = html.replace(/<p>([\s\S]*?)<\/p>/g, (_m, inner) =>
    split(inner).map((part) => `<p>${part}</p>`).join("\n"),
  );

  // 3. h2에 id를 붙이고 목차를 만든다.
  const toc: { id: string; text: string }[] = [];
  html = html.replace(/<h2>([\s\S]*?)<\/h2>/g, (_m, text) => {
    const id = slug(text) || `section-${toc.length + 1}`;
    toc.push({ id, text: String(text).replace(/<[^>]+>/g, "") });
    return `<h2 id="${id}">${text}</h2>`;
  });

  return { html, lead, toc, minutes };
}
