import styles from "./post-lead.module.css";
import type { Prepared } from "@/lib/layout";

/** 읽는 시간 — 상위 블로그가 전부 쓰는 한 줄. 「길면 안 읽는다」를 미리 눌러 준다. */
export function ReadTime({ minutes }: { minutes: number }) {
  return <p className={styles.meta}>{minutes} min read</p>;
}

/** 결론 먼저 — 원고 맨 위에 이미 있던 요약을 상자로 보이게 한다. */
export function AnswerBox({ lead }: { lead: string }) {
  return (
    <aside className={styles.lead}>
      <p className={styles.label}>Short answer</p>
      <div dangerouslySetInnerHTML={{ __html: lead }} />
    </aside>
  );
}

/** 목차 — h2에서 자동. 폰에서는 접혀 있어 첫 화면을 먹지 않는다. */
export function Toc({ items }: { items: Prepared["toc"] }) {
  if (items.length < 3) return null;
  return (
    <details className={styles.toc}>
      <summary>In this post</summary>
      <ol>
        {items.map((item) => (
          <li key={item.id}>
            <a href={`#${item.id}`}>{item.text}</a>
          </li>
        ))}
      </ol>
    </details>
  );
}
