import Link from "next/link";
import { Post } from "@/interfaces/post";
import CoverImage from "./cover-image";

type Props = {
  posts: Post[];
};

export function RelatedPosts({ posts }: Props) {
  if (posts.length === 0) return null;
  return (
    <section className="max-w-2xl mx-auto mt-16 pt-10 border-t border-slate-200 dark:border-slate-700">
      <h2 className="mb-8 text-2xl font-bold tracking-tight">Keep practicing</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
        {posts.map((post) => (
          <div key={post.slug}>
            <div className="mb-3">
              <CoverImage slug={post.slug} title={post.title} src={post.coverImage} />
            </div>
            <h3 className="text-lg leading-snug">
              <Link href={`/posts/${post.slug}`} className="hover:underline">
                {post.title}
              </Link>
            </h3>
          </div>
        ))}
      </div>
    </section>
  );
}
