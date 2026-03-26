#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

SITE_ROOT = "https://bsteenkampwrites.com"

ROOT_DIR = Path(__file__).resolve().parent.parent
LATEST_PARTIAL_FILE = ROOT_DIR / "latest-satire.html"
OUTPUT_DIR = ROOT_DIR / "assets" / "images" / "og"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CARD_WIDTH = 1200
CARD_HEIGHT = 630
MARGIN_X = 80
TOP_Y = 70
BOTTOM_Y = CARD_HEIGHT - 70

TITLE_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
BODY_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
]
SMALL_FONT_PATHS = BODY_FONT_PATHS

TITLE_FONT_SIZE = 64
SUBTITLE_FONT_SIZE = 34
FOOTER_FONT_SIZE = 24


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_latest_article_path(latest_partial_html: str) -> Path:
    match = re.search(
        r'<a[^>]+id=["\']radioactive-button["\'][^>]+href=["\']([^"\']+)["\']',
        latest_partial_html,
        flags=re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Could not find #radioactive-button href in latest-satire.html")

    href = html.unescape(match.group(1).strip())

    if href.startswith("/"):
        href = href.lstrip("/")

    article_path = ROOT_DIR / href
    return article_path


def extract_meta_content(page_html: str, prop: str) -> Optional[str]:
    pattern = (
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']'
    )
    match = re.search(pattern, page_html, flags=re.IGNORECASE)
    return html.unescape(match.group(1).strip()) if match else None


def extract_tag_text(page_html: str, tag: str, element_id: Optional[str] = None) -> Optional[str]:
    if element_id:
        pattern = rf'<{tag}[^>]*id=["\']{re.escape(element_id)}["\'][^>]*>(.*?)</{tag}>'
    else:
        pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
    match = re.search(pattern, page_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    raw = re.sub(r"<[^>]+>", "", match.group(1))
    clean = html.unescape(" ".join(raw.split()))
    return clean.strip() or None


def slug_from_name(name: str) -> str:
    stem = Path(name).stem
    slug = stem.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "latest-satire"


def load_font(candidates: list[str], size: int):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        trial = f"{current} {word}"
        bbox = draw.textbbox((0, 0), trial, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y: int,
    font,
    fill,
    line_gap: int,
) -> int:
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, current_y), line, font=font)
        line_height = bbox[3] - bbox[1]
        current_y += line_height + line_gap
    return current_y


def generate_card(title: str, subtitle: str, article_url: str, output_path: Path) -> None:
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (18, 18, 18))
    draw = ImageDraw.Draw(img)

    title_font = load_font(TITLE_FONT_PATHS, TITLE_FONT_SIZE)
    subtitle_font = load_font(BODY_FONT_PATHS, SUBTITLE_FONT_SIZE)
    footer_font = load_font(SMALL_FONT_PATHS, FOOTER_FONT_SIZE)

    draw.rectangle([(0, 0), (CARD_WIDTH, 14)], fill=(210, 210, 210))

    draw.rounded_rectangle(
        [(50, 50), (CARD_WIDTH - 50, CARD_HEIGHT - 50)],
        radius=28,
        outline=(90, 90, 90),
        width=2,
    )

    max_text_width = CARD_WIDTH - (MARGIN_X * 2)

    title_lines = wrap_text(draw, title, title_font, max_text_width)
    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_text_width)

    y = TOP_Y + 35
    y = draw_multiline(
        draw,
        title_lines,
        MARGIN_X,
        y,
        title_font,
        fill=(255, 255, 255),
        line_gap=12,
    )

    y += 28

    y = draw_multiline(
        draw,
        subtitle_lines,
        MARGIN_X,
        y,
        subtitle_font,
        fill=(190, 190, 190),
        line_gap=10,
    )

    footer_left = "B Steenkamp Writes"
    footer_right = article_url

    draw.text((MARGIN_X, BOTTOM_Y - 24), footer_left, font=footer_font, fill=(140, 140, 140))

    right_bbox = draw.textbbox((0, 0), footer_right, font=footer_font)
    right_width = right_bbox[2] - right_bbox[0]
    draw.text(
        (CARD_WIDTH - MARGIN_X - right_width, BOTTOM_Y - 24),
        footer_right,
        font=footer_font,
        fill=(140, 140, 140),
    )

    img.save(output_path, format="PNG", optimize=True)


def main() -> None:
    if not LATEST_PARTIAL_FILE.exists():
        raise FileNotFoundError(f"Missing file: {LATEST_PARTIAL_FILE}")

    latest_partial_html = read_text_file(LATEST_PARTIAL_FILE)
    article_path = find_latest_article_path(latest_partial_html)

    if not article_path.exists():
        raise FileNotFoundError(f"Article file not found: {article_path}")

    article_html = read_text_file(article_path)

    title = (
        extract_meta_content(article_html, "og:title")
        or extract_tag_text(article_html, "h1", "page-title")
        or "Latest Satire"
    )

    subtitle = (
        extract_meta_content(article_html, "og:description")
        or extract_tag_text(article_html, "p", "article-subtitle")
        or "Freshly generated satire."
    )

    relative_article_url = "/" + article_path.relative_to(ROOT_DIR).as_posix()
    article_url = f"{SITE_ROOT}{relative_article_url}"

    slug = slug_from_name(article_path.name)
    output_path = OUTPUT_DIR / f"{slug}.png"

    generate_card(title, subtitle, article_url, output_path)

    print(f"Latest article file: {article_path}")
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()