#!/usr/bin/env python3
"""
Publish one local Instagram carousel folder to @sulsulapp via Meta Graph API.

Safety:
  - Default is dry-run (no network publish).
  - Real post only with --publish.
  - This run is scoped to ONE folder (test-first).

Env (.env.local):
  IG_USER_ID          Instagram professional account id
  IG_ACCESS_TOKEN     Page or long-lived user token with content_publish
  IG_GRAPH_HOST       default graph.facebook.com
  IG_GRAPH_VERSION    default v22.0

Images must be reachable by Instagram's servers. By default each slide is
uploaded briefly to litterbox (1h). Override with --image-base-url if already
hosted publicly.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from tools.load_env import load_env

ROOT = Path(__file__).resolve().parent
DEFAULT_TEST = ROOT / "obsidian_data/4.Repurposed/ig-airport-check-in-korean"
LITTERBOX_API = "https://litterbox.catbox.moe/resources/internals/api.php"


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def graph_base() -> str:
    host = os.environ.get("IG_GRAPH_HOST", "graph.facebook.com").strip()
    ver = os.environ.get("IG_GRAPH_VERSION", "v22.0").strip()
    return f"https://{host}/{ver}"


def require_creds() -> tuple[str, str]:
    uid = os.environ.get("IG_USER_ID", "").strip()
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not uid or not token:
        die(
            "Missing IG_USER_ID or IG_ACCESS_TOKEN in .env.local.\n"
            "See INSTAGRAM_PUBLISH_SETUP.md"
        )
    return uid, token


def list_slides(folder: Path) -> list[Path]:
    slides = sorted(folder.glob("[0-9][0-9].png"))
    if not slides:
        slides = sorted(folder.glob("[0-9][0-9].jpg"))
    if len(slides) < 2:
        die(f"Need at least 2 slides in {folder}")
    if len(slides) > 10:
        die(f"Instagram allows max 10 slides; found {len(slides)}")
    return slides


def read_caption(folder: Path) -> str:
    cap = folder / "caption.txt"
    if not cap.is_file():
        die(f"Missing caption.txt in {folder}")
    text = cap.read_text(encoding="utf-8").strip()
    if not text:
        die("caption.txt is empty")
    return text


def to_jpeg(src: Path, dest: Path, quality: int = 92) -> Path:
    from PIL import Image

    im = Image.open(src).convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=quality, optimize=True)
    return dest


def http_json(method: str, url: str, data: dict | None = None, timeout: int = 120) -> dict:
    body = None
    headers = {"User-Agent": "sulsul-blog-ig-publisher/1.0"}
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = {"raw": err_body}
        raise RuntimeError(f"HTTP {e.code} {url}\n{json.dumps(parsed, ensure_ascii=False, indent=2)}") from e


def upload_litterbox(jpeg_path: Path, hours: str = "1h") -> str:
    """Temporary public URL so Instagram can fetch the image."""
    boundary = "----SulsulBoundary7MA4YWxkTrZu0gW"
    file_bytes = jpeg_path.read_bytes()
    parts = []
    for name, value in (("reqtype", "fileupload"), ("time", hours)):
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="fileToUpload"; filename="{jpeg_path.name}"\r\n'.encode()
    )
    parts.append(b"Content-Type: image/jpeg\r\n\r\n")
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        LITTERBOX_API,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "sulsul-blog-ig-publisher/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        url = resp.read().decode("utf-8").strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Litterbox upload failed: {url}")
    return url


def resolve_image_urls(slides: list[Path], image_base_url: str | None, dry_run: bool) -> list[str]:
    if image_base_url:
        base = image_base_url.rstrip("/")
        urls = []
        for p in slides:
            # Prefer matching .jpg name if caller staged jpegs; else keep stem + .jpg
            urls.append(f"{base}/{p.stem}.jpg")
        return urls

    if dry_run:
        return [f"(would-upload) {p.name}" for p in slides]

    urls = []
    with tempfile.TemporaryDirectory(prefix="ig-carousel-") as tmp:
        tmp_path = Path(tmp)
        for p in slides:
            jpeg = to_jpeg(p, tmp_path / f"{p.stem}.jpg")
            print(f"  uploading {p.name} → temp public URL…")
            urls.append(upload_litterbox(jpeg))
            print(f"    {urls[-1]}")
    return urls


def wait_container(container_id: str, token: str, timeout_s: int = 180) -> None:
    base = graph_base()
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = f"{base}/{container_id}?fields=status_code,status&access_token={urllib.parse.quote(token)}"
        info = http_json("GET", url)
        code = (info.get("status_code") or "").upper()
        if code in {"FINISHED", "PUBLISHED"}:
            return
        if code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container {container_id} failed: {info}")
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for container {container_id}")


def create_child(ig_user_id: str, token: str, image_url: str) -> str:
    base = graph_base()
    url = f"{base}/{ig_user_id}/media"
    data = {
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": token,
    }
    resp = http_json("POST", url, data)
    cid = resp.get("id")
    if not cid:
        raise RuntimeError(f"No child container id: {resp}")
    wait_container(cid, token)
    return cid


def create_carousel(ig_user_id: str, token: str, child_ids: list[str], caption: str) -> str:
    base = graph_base()
    url = f"{base}/{ig_user_id}/media"
    data = {
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": caption,
        "access_token": token,
    }
    resp = http_json("POST", url, data)
    cid = resp.get("id")
    if not cid:
        raise RuntimeError(f"No carousel container id: {resp}")
    wait_container(cid, token)
    return cid


def publish_container(ig_user_id: str, token: str, creation_id: str) -> str:
    base = graph_base()
    url = f"{base}/{ig_user_id}/media_publish"
    data = {"creation_id": creation_id, "access_token": token}
    resp = http_json("POST", url, data)
    mid = resp.get("id")
    if not mid:
        raise RuntimeError(f"Publish failed: {resp}")
    return mid


def main() -> None:
    load_env(str(ROOT))
    parser = argparse.ArgumentParser(description="Publish one SULSUL Instagram carousel")
    parser.add_argument(
        "folder",
        nargs="?",
        default=str(DEFAULT_TEST),
        help="Carousel folder with 01.png… and caption.txt (default: airport test)",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Actually post to Instagram. Without this flag, dry-run only.",
    )
    parser.add_argument(
        "--image-base-url",
        default="",
        help="If set, use {base}/01.jpg … instead of temp upload",
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        die(f"Folder not found: {folder}")

    slides = list_slides(folder)
    caption = read_caption(folder)
    dry_run = not args.publish

    print("=== Instagram carousel publish ===")
    print(f"folder:  {folder}")
    print(f"slides:  {len(slides)} → {', '.join(p.name for p in slides)}")
    print(f"mode:    {'DRY-RUN (no post)' if dry_run else 'PUBLISH'}")
    print(f"caption ({len(caption)} chars):")
    print("---")
    print(caption)
    print("---")

    if dry_run:
        has_uid = bool(os.environ.get("IG_USER_ID", "").strip())
        has_tok = bool(os.environ.get("IG_ACCESS_TOKEN", "").strip())
        print(f"creds:   IG_USER_ID={'OK' if has_uid else 'MISSING'}  IG_ACCESS_TOKEN={'OK' if has_tok else 'MISSING'}")
        urls = resolve_image_urls(slides, args.image_base_url or None, dry_run=True)
        for u in urls:
            print(f"  image: {u}")
        print("\nDry-run complete. To post this ONE carousel:")
        print(f"  python3 publish_instagram_carousel.py \"{folder}\" --publish")
        return

    ig_user_id, token = require_creds()
    print(f"ig_user: {ig_user_id}")
    print(f"graph:   {graph_base()}")

    image_urls = resolve_image_urls(slides, args.image_base_url or None, dry_run=False)
    child_ids = []
    for i, image_url in enumerate(image_urls, 1):
        print(f"  creating child container {i}/{len(image_urls)}…")
        child_ids.append(create_child(ig_user_id, token, image_url))
        print(f"    id={child_ids[-1]}")

    print("  creating carousel container…")
    carousel_id = create_carousel(ig_user_id, token, child_ids, caption)
    print(f"    id={carousel_id}")

    print("  publishing…")
    media_id = publish_container(ig_user_id, token, carousel_id)
    print(f"\nSUCCESS media_id={media_id}")
    print("Check Instagram app → @sulsulapp feed (may take a few seconds).")


if __name__ == "__main__":
    main()
