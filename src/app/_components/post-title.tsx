import { ReactNode } from "react";

type Props = {
  children?: ReactNode;
};

/**
 * 2026-11-25: 폰에서 text-5xl(48px) + mb-12였다. 제목 하나가 첫 화면의 절반을 먹고,
 * 가운데 정렬이라 눈이 줄마다 왼쪽을 다시 찾아야 했다.
 * 상위 블로그 9곳은 폰에서 28~34px · 왼쪽 정렬이다.
 */
export function PostTitle({ children }: Props) {
  return (
    <h1 className="max-w-2xl mx-auto text-3xl md:text-5xl font-bold tracking-tight leading-tight mb-4">
      {children}
    </h1>
  );
}
