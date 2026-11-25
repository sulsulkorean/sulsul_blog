"use client";

import { useEffect, useState } from "react";
import { ctaHref } from "./app-cta";

/**
 * 2026-11-26: 대표님 결정 A — 「글 길이는 그대로 두고, 앱 칸을 따라다니게」.
 *
 * 그날 실측(폰 375×812, 한 화면 = 스크롤 한 번): 보통 글이 10번, 가장 긴 글이 17번이다.
 * 같은 검색어 상위는 더 길다 — 90DayKorean 39 · KoreanClass101 35 · Preply 21 · Busuu 18.
 * 그래서 길이를 깎지 않기로 했다(깎으면 노출 10,368회가 깎인다).
 *
 * 앱 칸은 글 위(1화면째) · 중간(42%) · 끝(97%) 셋이 있지만, 그 사이 예닐곱 화면 동안은
 * 앱이 화면에서 사라진다. 이 띠가 그 구간을 메운다.
 *
 * 뜨는 조건: 글 위 칸을 지나친 뒤(한 화면 넘게 내렸을 때).
 * 사라지는 조건: 글 끝 칸이 보일 때(같은 칸 두 개가 겹치지 않게) · 닫기를 눌렀을 때.
 * 출처 표식 article_sticky — GA4에서 위·중간·끝과 따로 센다.
 */
export function AppCtaSticky({ slug }: { slug: string }) {
  const [show, setShow] = useState(false);
  const [closed, setClosed] = useState(false);

  useEffect(() => {
    let endVisible = false;
    const update = () => {
      setShow(window.scrollY > window.innerHeight && !endVisible);
    };

    const end = document.getElementById("app-cta-end");
    const io = new IntersectionObserver(
      ([entry]) => {
        endVisible = entry.isIntersecting;
        update();
      },
      { rootMargin: "0px 0px -15% 0px" },
    );
    if (end) io.observe(end);

    window.addEventListener("scroll", update, { passive: true });
    update();
    return () => {
      window.removeEventListener("scroll", update);
      io.disconnect();
    };
  }, []);

  const open = show && !closed;

  return (
    <div
      aria-hidden={!open}
      className={`fixed inset-x-0 bottom-0 z-40 border-t border-pink-200 bg-white/95 backdrop-blur transition-transform duration-200 dark:border-pink-900/60 dark:bg-slate-900/95 ${
        open ? "translate-y-0" : "translate-y-full"
      }`}
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="mx-auto flex max-w-2xl items-center gap-3 px-4 py-2.5">
        <span aria-hidden className="text-xl leading-none">
          🎙️
        </span>
        <span className="flex-1 text-sm font-bold leading-tight text-slate-900 dark:text-slate-100">
          Say one Korean line out loud
          <span className="block text-xs font-normal text-slate-500 dark:text-slate-400">
            10 seconds, no sign-up
          </span>
        </span>
        <a
          href={ctaHref(slug, "article_sticky", true)}
          tabIndex={open ? undefined : -1}
          className="shrink-0 rounded-full bg-pink-500 px-5 py-2 text-sm font-bold text-white no-underline hover:bg-pink-600"
        >
          Try it →
        </a>
        <button
          type="button"
          onClick={() => setClosed(true)}
          tabIndex={open ? undefined : -1}
          aria-label="Close"
          className="shrink-0 px-1 text-xl leading-none text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        >
          ×
        </button>
      </div>
    </div>
  );
}
