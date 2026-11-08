import { Post } from "@/interfaces/post";
import fs from "fs";
import matter from "gray-matter";
import { join } from "path";
import { DEFAULT_AUTHOR, DEFAULT_COVER_IMAGE } from "./constants";

const postsDirectory = join(process.cwd(), "_posts");

export function getPostSlugs() {
  if (!fs.existsSync(postsDirectory)) return [];
  return fs.readdirSync(postsDirectory).filter((file) => file.endsWith(".md"));
}

let slugSet: Set<string> | null = null;

/**
 * 2026-11-09: 본문 안 글→글 링크가 `](/slug)` 로 적혀 있는데 글의 실제 경로는 `/posts/slug` 다.
 * 223편에 걸친 570개 링크가 전부 404였고(라이브 확인), 그래서 구글이 글 사이를 못 걸어다녔다.
 * 발행기가 계속 이 식으로 쓰므로 고치는 자리는 «쓸 때»가 아니라 «읽을 때»다 — 지난 글과
 * 앞으로 나올 글을 한꺼번에 덮는다. 글이 아닌 /assets/... 는 슬러그 집합에 없어 손대지 않는다.
 */
function fixPostLinks(content: string): string {
  slugSet ??= new Set(getPostSlugs().map((f) => f.replace(/\.md$/, "")));
  return content.replace(/\]\(\/([A-Za-z0-9-]+)(?=[)?#])/g, (whole, s) =>
    slugSet!.has(s) ? `](/posts/${s}` : whole,
  );
}

export function getPostBySlug(slug: string): Post | null {
  const realSlug = slug.replace(/\.md$/, "");
  const fullPath = join(postsDirectory, `${realSlug}.md`);
  if (!fs.existsSync(fullPath)) {
    return null;
  }
  const fileContents = fs.readFileSync(fullPath, "utf8");
  const { data, content } = matter(fileContents);

  const coverImage = data.coverImage || DEFAULT_COVER_IMAGE;

  return {
    ...data,
    slug: realSlug,
    content: fixPostLinks(content),
    coverImage,
    author: data.author?.name ? data.author : DEFAULT_AUTHOR,
    ogImage: { url: data.ogImage?.url || coverImage },
  } as Post;
}

export function getAllPosts(): Post[] {
  return getPostSlugs()
    .map((slug) => getPostBySlug(slug))
    .filter((post): post is Post => post !== null)
    .sort((post1, post2) => (post1.date > post2.date ? -1 : 1));
}

const STOP = new Set(["korean", "phrases", "phrase", "korea", "in", "at", "the", "a", "for", "of", "to", "and", "when", "with", "on", "your", "you"]);

function topicWords(post: Post): Set<string> {
  const text = [post.title, post.primaryKeyword, ...(post.keywords || [])].join(" ");
  return new Set(text.toLowerCase().match(/[a-z가-힣]{3,}/g)?.filter((w) => !STOP.has(w)));
}

/**
 * Posts worth linking from `post`. Every post used to stand alone — no post linked
 * to any other — so Google had no path to discover or rank the newer ones (Sept 2026:
 * 85 of 140 unindexed). Same category counts most; shared topic words break ties;
 * newest wins among equals so fresh posts get inbound links quickly.
 */
export function getRelatedPosts(post: Post, all: Post[], limit = 3): Post[] {
  const mine = topicWords(post);
  return all
    .filter((p) => p.slug !== post.slug)
    .map((p) => {
      let score = p.category === post.category ? 2 : 0;
      topicWords(p).forEach((w) => mine.has(w) && score++);
      return { p, score };
    })
    .sort((a, b) => b.score - a.score || (a.p.date > b.p.date ? -1 : 1))
    .slice(0, limit)
    .map(({ p }) => p);
}

export function wordCount(content: string) {
  return content.trim().split(/\s+/).filter(Boolean).length;
}
