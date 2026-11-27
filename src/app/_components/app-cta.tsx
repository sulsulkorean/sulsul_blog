import { APP_DEMO_URL, APP_URL, TUTOR_URL } from "@/lib/constants";

/**
 * 2026-11-20: 대표님 «랜딩으로 안 간다고?? 당장 넣어».
 *
 * 10/15 → 11/20에 노출이 1,709 → 10,368회로 6배 늘었는데 앱 방문은 6주 동안 5회였다.
 * 원인을 세어 보니 «링크가 없다»가 아니었다 — 278편 전부에 앱 링크가 있다.
 * 다만 (1) 글 맨 끝의 굵은 글씨 한 줄과 (2) 첫 단락 뒤 분홍 줄 한 칸, 둘 다 «글자»라서
 * 스크롤하며 읽는 사람 눈에 칸으로 안 들어온다. 글 위에는 아무것도 없어서, 끝까지 안 읽고
 * 떠나는 독자(대부분)는 앱을 볼 기회가 0이었다.
 *
 * 그래서 눈에 띄는 칸을 글 위 1곳 + 글 끝 1곳에 넣는다. 278편을 고치지 않고 템플릿 한 곳에서
 * 일괄로 나가므로, 다음부터 문구를 바꾸려면 이 파일만 고치면 된다.
 * 출처 표식은 자리마다 다르게 붙여(article_top · article_end) 어느 칸이 실제로 눌리는지
 * GA4에서 가릴 수 있게 했다 — 둘 다 utm_source=blog이고 medium이 article로 시작한다.
 */
export const ctaHref = (slug: string, medium: string, demo = false) => {
  // 데모 주소에는 #demo-section 같은 꼬리가 붙는다 — 물음표는 «#» «앞»에 와야 한다.
  const [bare, hash] = (demo ? APP_DEMO_URL : APP_URL).split("#");
  // «sulsul.app?utm…»이 아니라 «sulsul.app/?utm…»이 되게 — 주소가 섞이면 GA4에서 둘로 센다.
  const path = /^https?:\/\/[^/?#]+$/.test(bare) ? `${bare}/` : bare;
  const sep = path.includes("?") ? "&" : "?";
  const q = `utm_source=blog&utm_medium=${medium}&utm_campaign=${slug}`;
  return `${path}${sep}${q}${hash ? `#${hash}` : ""}`;
};

/** 글 위 — 끝까지 안 읽고 떠나는 독자가 보는 유일한 칸. 짧게, 읽기를 막지 않게. */
export function AppCtaTop({ slug }: { slug: string }) {
  return (
    <div className="max-w-2xl mx-auto mb-10">
      <a
        href={ctaHref(slug, "article_top", true)}
        className="group flex items-center gap-4 rounded-2xl border border-pink-200 bg-pink-50 px-5 py-4 no-underline transition-colors hover:bg-pink-100 dark:border-pink-900/60 dark:bg-pink-950/30 dark:hover:bg-pink-950/50"
      >
        <span aria-hidden className="text-2xl leading-none">🎙️</span>
        <span className="flex-1">
          <span className="block font-bold text-slate-900 dark:text-slate-100">
            Say one Korean line out loud — 10 seconds
          </span>
          <span className="block text-sm text-slate-600 dark:text-slate-300">
            Reading Korean is not speaking it. Try the speaking demo, no sign-up.
          </span>
        </span>
        <span className="shrink-0 rounded-full bg-pink-500 px-4 py-2 text-sm font-bold text-white group-hover:bg-pink-600">
          Try it →
        </span>
      </a>
    </div>
  );
}

/** 글 끝 — 다 읽은 사람. 여기까지 온 독자가 가장 잘 누른다. */
export function AppCtaEnd({ slug }: { slug: string }) {
  return (
    // id: 떠 있는 띠(AppCtaSticky)가 «여기까지 왔으면 숨는다»를 판단하는 표식.
    <div id="app-cta-end" className="max-w-2xl mx-auto mt-14">
      <div className="rounded-2xl border-2 border-pink-500 bg-white px-6 py-8 text-center dark:bg-slate-900">
        <h2 className="mb-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Now say it out loud
        </h2>
        <p className="mx-auto mb-6 max-w-md text-slate-600 dark:text-slate-300">
          SULSUL says the phrase, you repeat it, and it tells you what came out
          wrong — 100 survival patterns for cafes, taxis and small talk in Seoul.
        </p>
        <a
          href={ctaHref(slug, "article_end")}
          className="inline-block rounded-full bg-pink-500 px-8 py-3 font-bold text-white no-underline transition-colors hover:bg-pink-600"
        >
          Start speaking Korean →
        </a>
        <p className="mt-4 text-sm">
          <a
            href={ctaHref(slug, "article_end_demo", true)}
            className="font-bold text-pink-600 dark:text-pink-400"
          >
            Or try one line first (10 seconds) →
          </a>
        </p>
      </div>
    </div>
  );
}

/** 글 끝 앱 칸 아래 한 줄 — 사람 선생님과 1:1로 배우고 싶은 독자용 (Preply). */
export function TutorLine() {
  return (
    <p className="max-w-2xl mx-auto mt-6 text-center text-slate-600 dark:text-slate-300">
      Want a one-on-one lesson with me?{" "}
      <a
        href={TUTOR_URL}
        target="_blank"
        rel="noopener sponsored"
        className="font-bold text-pink-600 underline dark:text-pink-400"
      >
        Click here :)
      </a>
    </p>
  );
}
