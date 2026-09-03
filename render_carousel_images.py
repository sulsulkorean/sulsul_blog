#!/usr/bin/env python3
"""
Render Instagram carousels by stamping copy onto the designer's templates.

Templates (required):
  obsidian_data/4.Repurposed/templates/cover.png  — slide 1 (title only)
  obsidian_data/4.Repurposed/templates/body.png   — teaching slides (copy + page no.)
  obsidian_data/4.Repurposed/templates/end.png    — last slide (used as-is)

Usage:
  python3 render_carousel_images.py obsidian_data/4.Repurposed/ig-airport-check-in-korean.md
  python3 render_carousel_images.py --all
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPURPOSED_DIR = os.path.join(ROOT, "obsidian_data", "4.Repurposed")
TEMPLATE_DIR = os.path.join(REPURPOSED_DIR, "templates")

# Business text colors (CANVA_GUIDE) on the cream/white card
INK = (92, 75, 81)        # #5C4B51
MUTED = (120, 112, 120)   # #787078
PINK = (254, 100, 171)    # #FE64AB
CREAM = (254, 245, 230)   # matches cover background sample
WHITE = (255, 255, 255)

FONT_TTC = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
_FONT_CACHE: dict[tuple[int, int], ImageFont.FreeTypeFont] = {}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    preferred = (8, 7, 3, 1, 0) if bold else (0, 1, 2, 6)
    key = (size, int(bold))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    last_err = None
    for idx in preferred:
        try:
            face = ImageFont.truetype(FONT_TTC, size, index=idx)
            _FONT_CACHE[key] = face
            return face
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Cannot load Korean font: {last_err}")


def require_templates() -> dict[str, str]:
    paths = {
        "cover": os.path.join(TEMPLATE_DIR, "cover.png"),
        "body": os.path.join(TEMPLATE_DIR, "body.png"),
        "end": os.path.join(TEMPLATE_DIR, "end.png"),
    }
    missing = [k for k, p in paths.items() if not os.path.isfile(p)]
    if missing:
        raise FileNotFoundError(
            "Missing template(s): "
            + ", ".join(missing)
            + f"\nPut cover.png / body.png / end.png in {TEMPLATE_DIR}"
        )
    return paths


def wrap_text(draw, text, font_obj, max_width):
    if not text:
        return []
    if len(re.findall(r"[가-힣]", text)) >= max(1, len(text.replace(" ", "")) // 3):
        lines, cur = [], ""
        for ch in text:
            trial = cur + ch
            if draw.textlength(trial, font=font_obj) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
        return lines
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font_obj) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def parse_phrase_blocks(raw: str) -> list[dict]:
    blocks = []
    for m in re.finditer(
        r"(?:^|\n)\s*(?:([AB])\s*:\s*)?\*\*([^*]*[가-힣][^*]*)\*\*"
        r"\s*(?:—|-|–)\s*\*([^*]+)\*\s*(?:\n|\r\n)\s*[\"“]([^\"”]+)[\"”]",
        raw,
    ):
        blocks.append(
            {
                "choice": m.group(1) or "",
                "korean": m.group(2).strip(),
                "roman": m.group(3).strip(),
                "english": m.group(4).strip(),
            }
        )
    if blocks:
        return blocks
    km = re.search(
        r"\*\*([^*]*[가-힣][^*]*)\*\*\s*(?:—|-|–)\s*\*([^*]+)\*",
        raw,
    )
    em = re.search(r'[\"“]([^\"”]+)[\"”]', raw)
    if km:
        blocks.append(
            {
                "choice": "",
                "korean": km.group(1).strip(),
                "roman": km.group(2).strip(),
                "english": em.group(1).strip() if em else "",
            }
        )
    return blocks


def parse_carousel(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        raise ValueError(f"Missing frontmatter: {path}")
    fm, body = parts[1], parts[2]

    def fm_get(key: str, default: str = "") -> str:
        m = re.search(rf'(?m)^{key}:\s*["\']?(.*?)["\']?\s*$', fm)
        return m.group(1).strip() if m else default

    slides = []
    chunks = re.split(r"(?m)^##\s+Slide\s+(\d+)\s*[—\-–]?\s*(.*)$", body)
    i = 1
    while i + 2 <= len(chunks):
        slides.append(
            {
                "num": int(chunks[i]),
                "heading": chunks[i + 1].strip(),
                "raw": chunks[i + 2].strip(),
            }
        )
        i += 3
    if len(slides) != 6:
        raise ValueError(f"Expected 6 slides, found {len(slides)} in {path}")

    parsed = []
    for s in slides:
        raw = s["raw"]
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        when_m = re.search(r"(?im)^when:\s*(.+)$", raw)
        when = when_m.group(1).strip() if when_m else ""

        if s["num"] == 1:
            # "## Slide 1 — Title" makes heading=="Title" — never use that as copy.
            headline = ""
            for ln in lines:
                if ln.startswith("**") and re.search(r"[A-Za-z]", ln):
                    headline = re.sub(r"^\*\*|\*\*$", "", ln).strip()
                    break
            plain = [
                ln
                for ln in lines
                if not ln.startswith("**")
                and not ln.lower().startswith("when:")
                and not ln.startswith("http")
            ]
            if not headline and plain:
                headline = plain[0]
                plain = plain[1:]
            if not headline or headline.lower() in {"title", "hook", "cover"}:
                headline = fm_get("title") or s["heading"]
            support = plain[0] if plain else ""
            parsed.append(
                {"kind": "title", "num": 1, "headline": headline, "support": support}
            )
        elif s["num"] == 6:
            parsed.append({"kind": "end", "num": 6})
        else:
            parsed.append(
                {
                    "kind": "teach",
                    "num": s["num"],
                    "phrases": parse_phrase_blocks(raw),
                    "when": when,
                }
            )

    return {
        "title": fm_get("title"),
        "slug": fm_get("slug") or os.path.splitext(os.path.basename(path))[0],
        "slides": parsed,
        "source": path,
        "caption": fm_get("caption"),
    }


def render_cover(template_path: str, slide: dict) -> Image.Image:
    """First page: per-title max size. Title first; support only if room left."""
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    headline = (slide.get("headline") or "").strip()
    support = (slide.get("support") or "").strip()
    if headline.lower() in {"title", "hook", "cover"}:
        headline = support
        support = ""

    # Sulsuli sits on the right — text stays in left safe box only.
    x = 40
    y0 = 48
    max_w = 410
    max_bottom = 370
    navy = (59, 61, 138)

    # 1) Biggest title that fits the left box (ignore support for sizing).
    best_title = None
    for size in range(86, 39, -2):
        hf = font(size, bold=True)
        head_lines = wrap_text(draw, headline, hf, max_w)[:4]
        if not head_lines or len(head_lines) > 4:
            continue
        line_h = int(size * 1.1)
        title_h = len(head_lines) * line_h
        if y0 + title_h <= max_bottom:
            best_title = (size, hf, head_lines, line_h, title_h)
            break

    if best_title is None:
        size = 40
        hf = font(size, bold=True)
        head_lines = wrap_text(draw, headline, hf, max_w)[:4]
        line_h = int(size * 1.1)
        best_title = (size, hf, head_lines, line_h, len(head_lines) * line_h)

    size, hf, head_lines, line_h, title_h = best_title
    y = y0
    for ln in head_lines:
        draw.text((x, y), ln, font=hf, fill=navy)
        y += line_h

    # 2) Support only in leftover space — never shrink the title for it.
    if support:
        y += 10
        room = max_bottom - y
        if room >= 36:
            sf = font(min(32, max(22, size - 34)))
            sub_h = max(28, size - 36)
            max_subs = max(1, room // sub_h)
            for ln in wrap_text(draw, support, sf, max_w)[:max_subs]:
                if y + sub_h > max_bottom + 8:
                    break
                draw.text((x, y), ln, font=sf, fill=MUTED)
                y += sub_h
    return img


def render_body(template_path: str, slide: dict, page_no: int) -> Image.Image:
    """Blank body template: place copy to match body_sample.png; update page no."""
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Replace page number inside the pill (blank already has 01)
    draw.rectangle((378, 196, 442, 230), fill=WHITE)
    page = f"{page_no:02d}"
    pf = font(22)
    tw = draw.textlength(page, font=pf)
    draw.text((410 - tw / 2, 198), page, font=pf, fill=MUTED)

    phrases = slide.get("phrases") or []
    dual = len(phrases) >= 2
    x = 100
    y = 250
    max_w = 600

    # Bigger secondary lines — phone readability (roman / English / When)
    if dual:
        kf, rf, ef = font(42, bold=True), font(36), font(38)
        choice_f = font(26, bold=True)
        gap_k, gap_r, gap_e = 54, 46, 48
    else:
        kf, rf, ef = font(56, bold=True), font(40), font(42)
        choice_f = font(26, bold=True)
        gap_k, gap_r, gap_e = 68, 52, 54

    for idx, phrase in enumerate(phrases[:2]):
        if dual:
            label = phrase.get("choice") or ("A" if idx == 0 else "B")
            draw.text((x, y), label, font=choice_f, fill=PINK)
            y += 34

        for ln in wrap_text(draw, phrase.get("korean") or "", kf, max_w)[:2]:
            draw.text((x, y), ln, font=kf, fill=INK)
            y += gap_k

        roman = phrase.get("roman") or ""
        if roman:
            y += 4
            for ln in wrap_text(draw, roman, rf, max_w)[:2]:
                draw.text((x, y), ln, font=rf, fill=MUTED)
                y += gap_r

        english = phrase.get("english") or ""
        if english:
            cleaned = english.strip().strip("“”\"")
            quoted = f"“{cleaned}”"
            y += 4
            for ln in wrap_text(draw, quoted, ef, max_w)[:3]:
                draw.text((x, y), ln, font=ef, fill=MUTED)
                y += gap_e

        if dual and idx == 0:
            y += 10
            draw.text((x, y), "or", font=font(28, bold=True), fill=PINK)
            y += 40

    when = slide.get("when") or ""
    if when:
        wf = font(40)
        when_text = f"When: {when}"
        when_y = min(max(y + 36, 680), 740)
        for ln in wrap_text(draw, when_text, wf, 620)[:3]:
            draw.text((100, when_y), ln, font=wf, fill=MUTED)
            when_y += 48

    return img


def render_carousel(data: dict, out_dir: str) -> list[str]:
    templates = require_templates()
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    teach_i = 0

    for slide in data["slides"]:
        if slide["kind"] == "title":
            img = render_cover(templates["cover"], slide)
            out = os.path.join(out_dir, "01.png")
        elif slide["kind"] == "end":
            img = Image.open(templates["end"]).convert("RGB")
            out = os.path.join(out_dir, "06.png")
        else:
            teach_i += 1
            img = render_body(templates["body"], slide, teach_i)
            out = os.path.join(out_dir, f"{teach_i + 1:02d}.png")  # 02..05

        img.save(out, "PNG", optimize=True)
        paths.append(out)
        print(f"  wrote {out}")

    if data.get("caption"):
        cap_path = os.path.join(out_dir, "caption.txt")
        with open(cap_path, "w", encoding="utf-8") as f:
            f.write(data["caption"].strip() + "\n")
        print(f"  wrote {cap_path}")
    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Stamp carousel copy onto SULSUL design templates"
    )
    parser.add_argument("markdown", nargs="?", help="Path to one ig-*.md draft")
    parser.add_argument("--all", action="store_true", help="Render every ig-*.md")
    args = parser.parse_args()

    require_templates()

    if args.all:
        files = sorted(glob.glob(os.path.join(REPURPOSED_DIR, "ig-*.md")))
    elif args.markdown:
        files = [
            args.markdown
            if os.path.isabs(args.markdown)
            else os.path.join(ROOT, args.markdown)
        ]
    else:
        parser.error("Pass a markdown path or --all")

    for path in files:
        data = parse_carousel(path)
        folder = data["slug"] if data["slug"].startswith("ig-") else f"ig-{data['slug']}"
        out_dir = os.path.join(REPURPOSED_DIR, folder)
        print(f"Rendering {os.path.basename(path)} → {os.path.relpath(out_dir, ROOT)}/")
        render_carousel(data, out_dir)

    print("\nDone. Templates used from obsidian_data/4.Repurposed/templates/")


if __name__ == "__main__":
    main()
