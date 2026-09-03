#!/usr/bin/env python3
"""
SULSUL Social Repurpose Engine
- Reads the same Obsidian vault loaders as generate_seo_posts.py
- Turns textbook pattern bundles into Instagram carousel copy (6 slides)
- Reuses brand bans + public-copy scan; rejects failures to _rejected/
- Local-only for now: no GitHub Actions hook
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from datetime import datetime

# Reuse vault paths, loaders, API helper, romanization, and brand bans
# from the blog engine without pulling in trend-search side effects beyond import.
import generate_seo_posts as blog

ROOT = blog.ROOT
LIBRARY_DIR = blog.LIBRARY_DIR
VOICE_DIR = blog.VOICE_DIR
REJECTED_DIR = blog.REJECTED_DIR
MODEL = blog.MODEL

REPURPOSED_DIR = os.path.join(blog.OBSIDIAN_VAULT_PATH, "4.Repurposed")
SLIDE_COUNT = 6  # title + 4 teaching + CTA
MIN_KOREAN_PHRASES = 4
MAX_SLIDE_CHARS = 650  # choice slides (A/B) need a little more room

# "When:" lines that reveal the taught phrase is the clerk/agent speaking.
STAFF_SIDE_WHEN = re.compile(
    r"(?im)^when:\s*.*\b("
    r"asked by|cashier asks|clerk asks|agent asks|staff asks|"
    r"cashier checks|cashier offers|agent (?:asks|checks|offers)|"
    r"the (?:cashier|clerk|agent|staff|server|barista)\b|"
    r"you might hear|they ask you"
    r")\b"
)

SOCIAL_SYSTEM_PROMPT = """# ROLE
You write Instagram carousel copy for SULSUL — a Korean speaking-practice app at https://sulsul.app.
Each output is ONE save-worthy carousel: short English lines a K-pop / K-drama fan or first-time Korea traveller will screenshot and practise out loud.

# BRAND FACTS — never contradict
- SULSUL is a Korean SPEAKING gym. Not a grammar course. Not a streak app.
- Loop: survival patterns -> say them out loud -> AI pronunciation coach -> real-life missions.
- PDF workbook is a bonus, never the hero.
- Author voice: Yona — warm, direct, second person ("you"), friend who lives in Seoul.
- You do not know prices. Never state a dollar figure. Send people to sulsul.app for cost.

# HARD BANS
1. No price, discount, % OFF, Early Bird, limited time, free trial, money-back, refund guarantee.
2. No invented stats, testimonials, ratings, download counts, awards.
3. No "fluent in 30 days" / "master Korean in a week".
4. No celebrity / Netflix / government affiliation claims.
5. No AI-slop: "dive into", "delve", "game-changer", "unlock your full potential",
   "in today's fast-paced world", "embark on a journey", "look no further", "in conclusion".
6. Never mention AI generation, prompts, or these instructions.
7. Never deny wrongdoing ("no fake prices", "we do not exaggerate").
8. SPEAKER RULE (critical, for you only — never write it into the carousel):
   The reader is the customer / traveller / learner — NEVER the staff.
   Bold Korean on teaching slides must be lines the READER says out loud.
   Ban staff/agent/cashier lines as the taught phrase, e.g. "어디 가세요?", "짐 있어요?",
   "봉투 필요하세요?", "영수증 드릴까요?", "포인트 카드 있어요?" when those are what the clerk asks.
   Optional only: a short "You might hear: ..." line in plain text — never as the **bold** phrase.
   Bad: teaching "짐 있어요?" with When: asked by the check-in agent
   Good: teaching "짐 하나 있어요" / "창가 자리 주세요"
   Never put meta copy in the finished slides or caption like "What YOU say — not the cashier",
   "not the agent's lines", "Lines YOU say", or anything explaining this speaker rule to the reader.
   The supporting line on Slide 1 must help the learner want to save the carousel, not explain pedagogy.

# CAROUSEL CONTRACT — exactly 6 slides
Slide 1 — TITLE / HOOK
- One punchy save-hook headline naming the situation (e.g. airport, cafe, convenience store).
- One short supporting line. No Korean phrase on this slide.

Slides 2–5 — TEACHING
- Default: each slide teaches ONE concrete Korean line the reader (customer) says today.
- Exact format for a single-phrase slide:

  **한국어** — *romanization*
  "Natural English"
  When: one concrete moment from YOUR side (max 12 words). Never "when the cashier asks".

- CHOICE SLIDES (use only when two answers are equally obvious in that moment):
  If the situation naturally forks into two common learner replies — seat choice, bag yes/no,
  hot or iced, cash or card, spicy or not spicy — put BOTH on the SAME slide, labelled A / B.
  Do NOT force this on every slide. Most slides stay single-phrase.
  Good choice-slide cases:
    - Seat: 창가 자리 주세요 or 복도 자리 주세요
    - Bag: 봉투 주세요 or 봉투 필요 없어요
    - Drink temp: 따뜻한 걸로 주세요 or 아이스로 주세요
  Bad: inventing a fake second option when one phrase is enough.
  Choice-slide format:

  A: **한국어** — *romanization*
  "Natural English"

  B: **한국어** — *romanization*
  "Natural English"

  When: one shared moment (max 12 words)
  Between A and B in the finished copy, separate with "or" (never "vs").

- Optional: one "Don't say / Say instead" line if it prevents a real freeze.
- Keep each slide under ~80 English words. Phone screen, not a blog.
- Across slides 2–5, aim for 4–6 distinct Korean lines total (a choice slide counts as two).

Slide 6 — CTA
- One line that names the situation again and says reading ≠ speaking when someone is waiting.
- One short SULSUL brand line (speaking gym / say it out loud). No price. No meta "what YOU say" talk.
- Exactly one link on the slide: https://sulsul.app (no ?utm_ query strings on slides).

# INSTAGRAM FEED CAPTION (frontmatter `caption` + caption.txt)
Purpose: complement the carousel — do NOT repeat every slide.
Target length: ~350–550 characters of body text (medium). Not a 2-line stub. Not a blog essay.

Exact structure (real line breaks):
1) Hook (1 line) — situation + tension/emotion (freeze, waiting line, first trip…)
2) Why it matters (1–2 short lines) — reading ≠ speaking when someone is waiting
3) Phrase tease (required for teaching carousels):
   1–2 Korean lines the reader will say. EACH line MUST include English meaning.
   Format: • 한국어 — English meaning
   Optional: • 한국어 — *romanization* — English meaning
   Never leave bare Hangul without English. No long essay — bullets only.
4) blank line
5) Soft CTA — Save this… / Practise out loud… / Comment which line you'll use first.
   One CTA only. Prefer Save or Comment over hard sell.
6) blank line
7) sulsul.app alone on its line (bare domain — NEVER ?utm_ query strings)
8) blank line
9) 4–6 hashtags on one line, include #SULSULapp + situation + learn/speak tags

Tone: warm, direct, second person. Light Teuida-style casual OK; no Duolingo unhinged meme voice.
No prices. No AI-slop. No meta speaker notes ("what YOU say — not the cashier").
Do not dump the full carousel into the caption — tease only.
Hangul without English in the caption = reject / rewrite.

# SOURCE RULE
Teach ONLY phrases grounded in the textbook excerpt. Prefer textbook wording. If unsure a phrase is natural, use a simpler textbook phrase. 해요체 by default.

# OUTPUT
Output ONLY the finished markdown file. Start with "---" on line 1. No code fences, no preface.

Frontmatter (keep this key order):

---
title: "carousel hook, <=70 chars"
slug: "kebab-case-max-6-words"
platform: "instagram-carousel"
situation: "short situation label"
date: "ISO_DATE_PLACEHOLDER"
patterns:
  - "phrase 1"
  - "phrase 2"
  - "phrase 3"
  - "phrase 4"
caption: "Medium IG caption: hook + why + 1-2 Korean teases EACH with English meaning (한국어 — meaning) + Save CTA + sulsul.app + 4-6 hashtags. No bare Hangul. No ?utm_."---

Then body:

## Slide 1 — Title
...

## Slide 2 — ...
...

## Slide 3 — ...
...

## Slide 4 — ...
...

## Slide 5 — ...
...

## Slide 6 — CTA
...
"""


def list_existing_carousels(dirs=None):
    """Titles already written, so later runs do not repeat the same hook."""
    items = []
    for directory in dirs or [REPURPOSED_DIR]:
        if not os.path.exists(directory):
            continue
        for filepath in glob.glob(os.path.join(directory, "*.md")):
            slug = os.path.basename(filepath)[:-3]
            title = slug
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
                if m:
                    title = m.group(1).strip()
            except Exception:
                pass
            items.append({"slug": slug, "title": title})
    return items


def extract_situation_bundles(library_content, count, existing_titles):
    """Ask the model for situation-based pattern bundles from the textbook."""
    print(f"Extracting {count} Instagram carousel situations...")
    prompt = f"""You are a social content strategist for SULSUL, a Korean speaking app.
From the textbook below, produce {count} Instagram carousel themes.

Each theme is a situation foreigners freeze in, bundled with 4 Korean phrases they can actually say.

Rules:
- Format each line exactly as:
  N. Situation label | phrase1 / phrase2 / phrase3 / phrase4
- Situation labels are short English (e.g. "Airport check-in", "Convenience store counter", "Cafe order").
- Phrases must be real Korean from the textbook (해요체). Use hangul.
- Every phrase is what the LEARNER says (customer / traveller). Never staff/cashier/agent lines.
  Bad: 어디 가세요? / 짐 있어요? / 봉투 필요하세요? / 영수증 드릴까요?
  Good: 창가 자리 주세요 / 짐 하나 있어요 / 이거 주세요 / 카드로 결제할게요
- Prefer Survival Mission situations and everyday Seoul moments over grammar theory.
- Exclude anything close to these already-made carousels: {existing_titles or '(none)'}
- Spread across different places: airport/transport, cafe, convenience store, restaurant, shopping, hotel, KakaoTalk, making friends.

Output: a numbered list only, no commentary.

[TEXTBOOK]
{blog.library_slice(library_content, max_chars=10000)}
"""
    raw = blog.api_call_with_retry(
        [{"role": "user", "content": prompt}], temperature=0.4
    )
    bundles = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or ". " not in line:
            continue
        body = line.split(". ", 1)[1].strip().strip('"')
        if "|" not in body:
            continue
        situation, phrases = body.split("|", 1)
        bundles.append(
            {
                "situation": situation.strip(),
                "phrases": phrases.strip(),
            }
        )
    return bundles[:count]


def generate_carousel(bundle, library_content, voice_content, existing):
    iso_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    voice = (
        voice_content[:4000]
        if voice_content
        else "(no voice samples — warm, direct, second-person Seoul-friend tone)"
    )
    seed = f"{bundle['situation']} {bundle['phrases']}"
    lib = blog.library_slice(library_content, seed_text=seed, max_chars=8000)
    existing_block = (
        "\n".join(f"- {p['slug']} — {p['title']}" for p in existing)
        if existing
        else "(none yet)"
    )

    system = SOCIAL_SYSTEM_PROMPT.replace("ISO_DATE_PLACEHOLDER", iso_date)
    user = f"""[DATE] {iso_date}

[SITUATION] {bundle['situation']}
[SEED PHRASES — teach these or close textbook equivalents]
{bundle['phrases']}

[VOICE SAMPLES — copy this tone, not this content]
{voice}

[SULSUL TEXTBOOK — only source for Korean you teach]
{lib}

[EXISTING CAROUSELS — do not repeat these hooks]
{existing_block}

Write one 6-slide Instagram carousel for this situation.
In frontmatter set date: "{iso_date}"
"""

    print(f"[carousel] '{bundle['situation']}'...")
    raw = blog.api_call_with_retry(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
    )
    draft = blog.fix_romanization(blog.strip_code_fences(raw))
    return revise_carousel(draft, system, user)


def slide_headings(body):
    return re.findall(r"(?mi)^##\s+Slide\s+(\d+)\b", body)


def validate_carousel(text, existing):
    """Brand bans + public-copy scan + carousel structure. Not the blog length/FAQ gate."""
    reasons = []
    lower = text.lower()

    for phrase in blog.BANNED_PHRASES:
        if phrase in lower:
            reasons.append(f"banned phrase: {phrase}")

    for _line_no, rule_id, snippet, _why in blog.scan_public_copy(
        text, "obsidian_data/4.Repurposed/draft.md"
    ):
        reasons.append(f"public-copy rule [{rule_id}]: {snippet}")

    if not text.lstrip().startswith("---"):
        reasons.append("missing frontmatter")

    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    body = parts[2] if len(parts) >= 3 else text

    slides = slide_headings(body)
    if len(slides) != SLIDE_COUNT:
        reasons.append(f"slide count: {len(slides)} (need exactly {SLIDE_COUNT})")
    elif [int(n) for n in slides] != list(range(1, SLIDE_COUNT + 1)):
        reasons.append(f"slides out of order: {', '.join(slides)}")

    if not re.search(r"(?mi)^##\s+Slide\s+1\b", body):
        reasons.append("missing title slide (Slide 1)")
    if not re.search(r"(?mi)^##\s+Slide\s+6\b", body):
        reasons.append("missing CTA slide (Slide 6)")

    cta_count = len(re.findall(r"https://sulsul\.app", text))
    if cta_count < 1:
        reasons.append("missing sulsul.app CTA")
    if cta_count > 3:
        reasons.append(f"too many sulsul.app links: {cta_count}")

    phrases = set(
        m.group(0).strip()
        for m in re.finditer(r"[가-힣][가-힣 ]{1,20}[가-힣]", body)
    )
    if len(phrases) < MIN_KOREAN_PHRASES:
        reasons.append(f"only {len(phrases)} distinct Korean phrases")

    # Teaching slides should carry the **한국어** — *romanization* block.
    teaching_blocks = len(
        re.findall(
            r"\*\*[^*]*[가-힣][^*]*\*\*\s*(?:—|-|–)\s*\*[^*\n]+\*",
            body,
        )
    )
    if teaching_blocks < 4:
        reasons.append(f"teaching blocks: {teaching_blocks} (need at least 4)")

    for m in re.finditer(r"(?mi)^##\s+Slide\s+\d+[^\n]*\n(.*?)(?=^##\s+Slide\s+\d+|\Z)", body, re.S):
        slide_text = m.group(1).strip()
        if len(slide_text) > MAX_SLIDE_CHARS:
            reasons.append(f"slide too long: {len(slide_text)} chars")
            break
        staff = STAFF_SIDE_WHEN.search(slide_text)
        if staff:
            reasons.append(f"staff-side phrase: {staff.group(0).strip()[:70]}")
            break

    title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
    title = title_m.group(1) if title_m else ""
    if len(title) > 80:
        reasons.append(f"title too long: {len(title)} chars")

    for p in existing:
        if blog.title_similarity(title, p["title"]) >= 0.85:
            reasons.append(f"cannibalizes existing: {p['slug']}")
            break

    return reasons


def fix_carousel_instructions(reasons):
    steps = []
    for r in reasons:
        if r.startswith("public-copy rule"):
            rule = r.split("[", 1)[1].split("]", 1)[0]
            snippet = r.split(": ", 1)[1]
            if rule == "price":
                steps.append(
                    f'- Delete "{snippet}". Never put a price. Link to https://sulsul.app only.'
                )
            elif rule == "denial":
                steps.append(
                    f'- Delete "{snippet}". Say what SULSUL does, never what it is not accused of.'
                )
            elif rule == "competitor":
                steps.append(
                    f'- Remove "{snippet}". Describe SULSUL without naming another product.'
                )
            else:
                steps.append(f'- Remove "{snippet}".')
        elif r.startswith("banned phrase"):
            steps.append(f'- Remove this wording: "{r.split(": ", 1)[1]}".')
        elif r.startswith("slide count") or r.startswith("slides out of order"):
            steps.append(
                "- Use exactly six headings: ## Slide 1 — Title through ## Slide 6 — CTA."
            )
        elif r.startswith("teaching blocks"):
            steps.append(
                "- Slides 2–5 each need one **한국어** — *romanization* block with English and When:."
            )
        elif r.startswith("only") and "Korean phrases" in r:
            steps.append("- Teach at least 4 distinct Korean phrases across slides 2–5.")
        elif r.startswith("slide too long"):
            steps.append(
                f"- Shorten every slide to under {MAX_SLIDE_CHARS} characters. Phone screen."
            )
        elif r.startswith("missing sulsul.app") or "missing CTA slide" in r:
            steps.append(
                "- Slide 6 must include https://sulsul.app (no UTM query string on the slide)"

            )
        elif r.startswith("missing title slide"):
            steps.append("- Start the body with ## Slide 1 — Title")
        elif r.startswith("too many sulsul.app"):
            steps.append("- Keep at most one sulsul.app link in the CTA slide and one in caption.")
        elif r.startswith("title too long"):
            steps.append("- Shorten the frontmatter title to 70 characters or fewer.")
        elif r.startswith("cannibalizes"):
            steps.append("- Pick a narrower situation hook; this one overlaps an existing carousel.")
        elif r.startswith("staff-side phrase"):
            steps.append(
                "- Every bold Korean line must be what the LEARNER says (customer/traveller). "
                "Replace staff/agent/cashier questions with the reader's reply or request. "
                "Example: not 짐 있어요? / 봉투 필요하세요? — use 짐 하나 있어요 / 봉투 주세요 / 카드로 결제할게요."
            )
        else:
            steps.append(f"- Fix: {r}")
    return steps


def revise_carousel(draft, system, user, rounds=3):
    for attempt in range(1, rounds + 1):
        reasons = validate_carousel(draft, [])
        # During revision, skip cannibalization against empty list; final save rechecks.
        if not reasons:
            return draft
        steps = fix_carousel_instructions(reasons)
        print(f"  revision {attempt}: " + "; ".join(reasons))
        revision = (
            "Your draft failed the social quality gate. Fix exactly these problems:\n\n"
            + "\n".join(steps)
            + "\n\nKeep the 6-slide structure and any good Korean phrases already there.\n"
            'Output ONLY the finished markdown file, starting with "---" on line 1.'
        )
        raw = blog.api_call_with_retry(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": draft},
                {"role": "user", "content": revision},
            ],
            temperature=0.4,
        )
        candidate = blog.fix_romanization(blog.strip_code_fences(raw))
        if len(validate_carousel(candidate, [])) <= len(reasons):
            draft = candidate
    return draft


def save_carousel(text, existing):
    os.makedirs(REPURPOSED_DIR, exist_ok=True)
    os.makedirs(REJECTED_DIR, exist_ok=True)

    reasons = validate_carousel(text, existing)
    slug = blog.extract_frontmatter_slug(text)
    if not slug.startswith("ig-"):
        slug = f"ig-{slug}"
    filepath = os.path.join(REPURPOSED_DIR, f"{slug}.md")
    if os.path.exists(filepath):
        slug = f"{slug}-{datetime.utcnow().strftime('%H%M%S')}"
        filepath = os.path.join(REPURPOSED_DIR, f"{slug}.md")

    title = blog.extract_title(text)

    if reasons:
        reject_path = os.path.join(REJECTED_DIR, f"{slug}.md")
        with open(reject_path, "w", encoding="utf-8") as f:
            f.write("<!-- REJECTED: " + " | ".join(reasons) + " -->\n")
            f.write(text)
        print(f"Rejected ({'; '.join(reasons)}) -> {reject_path}")
        return {"slug": slug, "title": title, "kept": False, "reasons": reasons}

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved: {filepath}")
    return {"slug": slug, "title": title, "kept": True, "reasons": []}


def write_run_summary(results):
    kept = [r for r in results if r["kept"]]
    lines = [
        "### SULSUL social repurpose run",
        "",
        f"Passed the gate: **{len(kept)} of {len(results)}**",
        "",
        "| Draft | Result |",
        "|---|---|",
    ]
    for r in results:
        verdict = "kept" if r["kept"] else "rejected — " + "; ".join(r["reasons"][:3])
        lines.append(f"| {r['title'][:70]} | {verdict} |")
    if not results:
        lines.append("| (no draft attempted) | nothing to write |")
    summary = "\n".join(lines) + "\n\n"
    print("\n" + summary)


def main():
    parser = argparse.ArgumentParser(
        description="SULSUL Social Repurpose — Instagram carousel text from textbook patterns"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Carousels to generate (default 5)",
    )
    args = parser.parse_args()

    blog.load_env(ROOT)
    if not os.environ.get("OPENAI_API_KEY"):
        env_path = os.path.join(ROOT, ".env.local")
        print(
            "OPENAI_API_KEY is missing.\n"
            "Do this once (do NOT paste the key into Cursor chat):\n"
            f"  1. Open or create: {env_path}\n"
            "  2. Put one line in that file:\n"
            '       OPENAI_API_KEY=sk-여기에키\n'
            "  3. Save, then re-run:\n"
            "       python3 generate_social_repurpose.py --count 5\n"
            "The file is gitignored — it will not be uploaded."
        )
        sys.exit(1)

    print(
        f"SULSUL Social Repurpose — count={args.count}, model={MODEL}\n"
        f"Output folder: {os.path.relpath(REPURPOSED_DIR, ROOT)}/\n"
    )

    library_content = blog.read_markdown_files(LIBRARY_DIR)
    voice_content = blog.read_markdown_files(VOICE_DIR)
    existing = list_existing_carousels()

    if not library_content:
        print(f"Warning: no textbook files in {LIBRARY_DIR}")
    if not voice_content:
        print(f"Warning: no voice files in {VOICE_DIR}")

    titles = "; ".join(p["title"] for p in existing)
    bundles = extract_situation_bundles(library_content, args.count, titles)
    if not bundles:
        print("Nothing to write about this run.")
        write_run_summary([])
        return

    print("\nQueue:")
    for i, b in enumerate(bundles, 1):
        print(f"  {i}. {b['situation']} — {b['phrases'][:60]}")
    print()

    results = []
    for bundle in bundles:
        try:
            draft = generate_carousel(
                bundle, library_content, voice_content, existing
            )
            saved = save_carousel(draft, existing)
            results.append(saved)
            if saved["kept"]:
                existing.append({"slug": saved["slug"], "title": saved["title"]})
        except Exception as e:
            print(f"Failed on '{bundle['situation']}': {e}")
            results.append(
                {
                    "slug": "",
                    "title": bundle["situation"][:70],
                    "kept": False,
                    "reasons": [str(e)[:80]],
                }
            )

    write_run_summary(results)
    print(f"Keepers: {os.path.relpath(REPURPOSED_DIR, ROOT)}/")
    print("Rejected drafts (if any): _rejected/")


if __name__ == "__main__":
    main()
