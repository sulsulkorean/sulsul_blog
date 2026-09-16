import { APP_URL } from "./constants";

/**
 * Drop one app link into the body after the first section.
 *
 * Every post only linked to the app in its final line, and analytics showed the
 * result: of ten blog→app visits in six weeks, one came from the in-post link and
 * the rest from the footer. Readers who finish the first section are the ones
 * still reading; that is where the link belongs. Tagged post_mid + the slug so
 * the weekly report can tell this link and this post apart from the rest.
 */
export function insertMidCta(html: string, slug: string): string {
  const second = html.indexOf("<h2", html.indexOf("<h2") + 1);
  if (second < 0) return html;
  const href = `${APP_URL}/?utm_source=blog&utm_medium=post_mid&utm_campaign=${slug}`;
  const cta = `<p class="mid-cta"><a href="${href}">Practice this out loud with SULSUL — the app says it, you repeat it →</a></p>\n`;
  return html.slice(0, second) + cta + html.slice(second);
}
