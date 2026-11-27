import { ReactNode } from "react";
import CoverImage from "./cover-image";
import DateFormatter from "./date-formatter";
import { PostTitle } from "@/app/_components/post-title";
import { type Author } from "@/interfaces/author";

type Props = {
  title: string;
  coverImage: string;
  date: string;
  author: Author;
  minutes: number;
  /** 답 상자 — 사진 «앞»에 온다. 열자마자 답이 보여야 한다. */
  children?: ReactNode;
};

/**
 * 2026-11-25 새 순서: 제목 → 한 줄 서명 → 답 상자 → 사진.
 * 전에는 제목 → 큰 사진 → 얼굴 → 날짜 순이라, 폰에서 두 번 넘겨야 글이 시작됐다.
 */
export function PostHeader({
  title,
  coverImage,
  date,
  author,
  minutes,
  children,
}: Props) {
  return (
    <>
      <PostTitle>{title}</PostTitle>
      <div className="max-w-2xl mx-auto mb-6 flex items-center gap-2 text-sm text-slate-500">
        <img src={author.picture} className="w-7 h-7 rounded-full" alt="" />
        <span className="font-semibold text-slate-700">{author.name}</span>
        <span aria-hidden="true">·</span>
        <DateFormatter dateString={date} />
        <span aria-hidden="true">·</span>
        <span>{minutes} min read</span>
      </div>
      <div className="max-w-2xl mx-auto">{children}</div>
      <div className="max-w-2xl mx-auto mb-8 rounded-2xl overflow-hidden">
        <CoverImage title={title} src={coverImage} />
      </div>
    </>
  );
}
