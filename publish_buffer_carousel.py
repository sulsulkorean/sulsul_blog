#!/usr/bin/env python3
"""
Publish one local Instagram carousel folder via Buffer GraphQL API.

Prereqs (CEO once):
  1. Buffer free account + @sulsulapp connected (INSTAGRAM_BUFFER_SETUP.md)
  2. API key from https://publish.buffer.com/settings/api (or developers.buffer.com API settings)
  3. .env.local:
       BUFFER_API_TOKEN=...
       BUFFER_CHANNEL_ID=...   # optional; auto-detected if only one Instagram channel

Safety:
  - Default dry-run
  - Real post only with --publish
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from tools.load_env import load_env

ROOT = Path(__file__).resolve().parent
DEFAULT_TEST = ROOT / "obsidian_data/4.Repurposed/ig-airport-check-in-korean"
API_URL = "https://api.buffer.com"
LITTERBOX_API = "https://litterbox.catbox.moe/resources/internals/api.php"


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def list_slides(folder: Path) -> list[Path]:
    slides = sorted(folder.glob("[0-9][0-9].png"))
    if not slides:
        slides = sorted(folder.glob("[0-9][0-9].jpg"))
    if len(slides) < 2:
        die(f"Need at least 2 slides in {folder}")
    if len(slides) > 10:
        die(f"Buffer/Instagram API max 10 images; found {len(slides)}")
    return slides


def read_caption(folder: Path) -> str:
    cap = folder / "caption.txt"
    if not cap.is_file():
        die(f"Missing caption.txt in {folder}")
    text = cap.read_text(encoding="utf-8").strip()
    if not text:
        die("caption.txt is empty")
    # Never dump tracking query strings into the Instagram feed caption.
    import re

    text = re.sub(
        r"https?://(?:www\.)?sulsul\.app/?\?[^\s]+",
        "sulsul.app",
        text,
    )
    text = re.sub(r"https?://(?:www\.)?sulsul\.app/?", "sulsul.app", text)
    return text.strip()


def to_jpeg(src: Path, dest: Path, quality: int = 92) -> Path:
    from PIL import Image

    im = Image.open(src).convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=quality, optimize=True)
    return dest


def upload_litterbox(jpeg_path: Path, hours: str = "24h") -> str:
    boundary = "----SulsulBufferBoundary"
    file_bytes = jpeg_path.read_bytes()
    parts: list[bytes] = []
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
    req = urllib.request.Request(
        LITTERBOX_API,
        data=b"".join(parts),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "sulsul-blog-buffer-publisher/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        url = resp.read().decode("utf-8").strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Temp host upload failed: {url}")
    return url


def gql(token: str, query: str, variables: dict | None = None) -> dict:
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "sulsul-blog-buffer-publisher/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {err}") from e
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data.get("data") or {}


def resolve_channel_id(token: str, explicit: str) -> str:
    if explicit:
        return explicit
    orgs = gql(
        token,
        """
        query {
          account {
            organizations { id name }
          }
        }
        """,
    )
    org_list = (orgs.get("account") or {}).get("organizations") or []
    if not org_list:
        die("No Buffer organization on this account.")
    org_id = org_list[0]["id"]
    print(f"  org: {org_id} ({org_list[0].get('name')})")

    data = gql(
        token,
        """
        query($organizationId: OrganizationId!) {
          channels(input: { organizationId: $organizationId }) {
            id
            name
            displayName
            service
            type
            descriptor
            isLocked
            isDisconnected
          }
        }
        """,
        {"organizationId": org_id},
    )
    ig = []
    for ch in data.get("channels") or []:
        service = str(ch.get("service") or "")
        name = ch.get("name") or ""
        print(
            f"  channel: {ch.get('id')}  service={service}  "
            f"name={name}  display={ch.get('displayName')}  "
            f"locked={ch.get('isLocked')} disconnected={ch.get('isDisconnected')}"
        )
        if "instagram" in service.lower():
            ig.append(ch)
    if not ig:
        die("No Instagram channel on this Buffer account. Connect @sulsulapp first.")
    if len(ig) > 1:
        for ch in ig:
            if "sulsul" in (ch.get("name") or "").lower() or "sulsul" in (
                ch.get("displayName") or ""
            ).lower():
                return ch["id"]
        die("Multiple Instagram channels — set BUFFER_CHANNEL_ID in .env.local")
    return ig[0]["id"]


def create_carousel(
    token: str,
    channel_id: str,
    caption: str,
    image_urls: list[str],
    *,
    share_now: bool,
) -> dict:
    assets = [{"image": {"url": u}} for u in image_urls]
    mode = "shareNow" if share_now else "addToQueue"
    # Inline mutation (matches Buffer docs examples; avoids input-type name drift)
    assets_gql = ", ".join("{ image: { url: %s } }" % json.dumps(u) for u in image_urls)
    text_gql = json.dumps(caption)

    def run(mode_name: str) -> dict:
        query = f"""
        mutation {{
          createPost(
            input: {{
              text: {text_gql}
              channelId: {json.dumps(channel_id)}
              schedulingType: automatic
              mode: {mode_name}
              needsApproval: false
              assets: [{assets_gql}]
              metadata: {{
                instagram: {{
                  type: post
                  shouldShareToFeed: true
                }}
              }}
            }}
          ) {{
            ... on PostActionSuccess {{
              post {{ id text status dueAt }}
            }}
            ... on MutationError {{ message }}
          }}
        }}
        """
        return gql(token, query)

    data = run(mode)
    result = data.get("createPost") or {}
    if result.get("message") and not result.get("post"):
        if share_now and mode == "shareNow":
            print("shareNow rejected — falling back to addToQueue…")
            data = run("addToQueue")
            result = data.get("createPost") or {}
        if result.get("message") and not result.get("post"):
            raise RuntimeError(result["message"])
    return result


def main() -> None:
    load_env(str(ROOT))
    parser = argparse.ArgumentParser(description="Publish carousel via Buffer")
    parser.add_argument("folder", nargs="?", default=str(DEFAULT_TEST))
    parser.add_argument("--publish", action="store_true")
    parser.add_argument(
        "--queue",
        action="store_true",
        help="Add to Buffer queue instead of trying Share Now",
    )
    parser.add_argument(
        "--image-base-url",
        default="",
        help="Use {base}/01.jpg … instead of temp upload",
    )
    parser.add_argument("--list-channels", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("BUFFER_API_TOKEN", "").strip()
    channel_env = os.environ.get("BUFFER_CHANNEL_ID", "").strip()

    if args.list_channels:
        if not token:
            die("BUFFER_API_TOKEN missing in .env.local")
        resolve_channel_id(token, "")
        return

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        die(f"Folder not found: {folder}")

    slides = list_slides(folder)
    caption = read_caption(folder)
    dry_run = not args.publish

    print("=== Buffer Instagram carousel ===")
    print(f"folder:  {folder}")
    print(f"slides:  {len(slides)} → {', '.join(p.name for p in slides)}")
    print(f"mode:    {'DRY-RUN' if dry_run else 'PUBLISH'}")
    print(f"caption ({len(caption)} chars):")
    print("---")
    print(caption)
    print("---")
    print(f"token:   {'OK' if token else 'MISSING'}")

    if dry_run:
        print("\nDry-run OK. After BUFFER_API_TOKEN is set:")
        print(f'  python3 publish_buffer_carousel.py "{folder}" --publish')
        return

    if not token:
        die("BUFFER_API_TOKEN missing. See INSTAGRAM_BUFFER_SETUP.md §API key")

    channel_id = resolve_channel_id(token, channel_env)
    print(f"channel: {channel_id}")

    if args.image_base_url:
        base = args.image_base_url.rstrip("/")
        image_urls = [f"{base}/{p.stem}.jpg" for p in slides]
    else:
        image_urls = []
        with tempfile.TemporaryDirectory(prefix="buffer-carousel-") as tmp:
            tmp_path = Path(tmp)
            for p in slides:
                jpeg = to_jpeg(p, tmp_path / f"{p.stem}.jpg")
                print(f"  uploading {p.name}…")
                image_urls.append(upload_litterbox(jpeg, hours="24h"))
                print(f"    {image_urls[-1]}")

    result = create_carousel(
        token,
        channel_id,
        caption,
        image_urls,
        share_now=not args.queue,
    )
    print("\nSUCCESS")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Check Instagram @sulsulapp (or Buffer queue).")


if __name__ == "__main__":
    main()
