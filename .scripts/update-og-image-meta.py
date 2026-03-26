#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

SITE_ROOT = "https://bsteenkampwrites.com"

ROOT_DIR = Path(__file__).resolve().parent.parent
SATIRE_DIR = ROOT_DIR / "satire"
OG_DIR = ROOT_DIR / "assets" / "images" / "og"


def slug_from_name(name: str) -> str:
    stem = Path(name).stem
    slug = stem.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "untitled"


def build_og_image_url(article_path: Path) -> str:
    slug = slug_from_name(article_path.name)
    return f"{SITE_ROOT}/assets/images/og/{slug}.png"


def build_meta_line(property_or_name: str, key: str, content: str) -> str:
    return f'<meta {property_or_name}="{key}" content="{content}">'


def upsert_meta_tag(html_text: str, attr_name: str, attr_value: str, content: str) -> str:
    pattern = re.compile(
        rf'<meta\b[^>]*\b{attr_name}=["\']{re.escape(attr_value)}["\'][^>]*>',
        flags=re.IGNORECASE,
    )

    replacement = build_meta_line(attr_name, attr_value, content)

    if pattern.search(html_text):
        return pattern.sub(replacement, html_text, count=1)

    head_open_pattern = re.compile(r"<head[^>]*>", flags=re.IGNORECASE)
    match = head_open_pattern.search(html_text)
    if not match:
        raise RuntimeError("No <head> tag found")

    insert_at = match.end()
    insertion = f"\n  {replacement}"
    return html_text[:insert_at] + insertion + html_text[insert_at:]


def update_article_meta(article_path: Path) -> tuple[bool, str]:
    slug = slug_from_name(article_path.name)
    image_path = OG_DIR / f"{slug}.png"

    if not image_path.exists():
        return False, f"Missing image: {image_path.name}"

    html_text = article_path.read_text(encoding="utf-8")

    og_image_url = build_og_image_url(article_path)

    updated = html_text

    # Open Graph (Facebook and others)
    updated = upsert_meta_tag(updated, "property", "og:image", og_image_url)
    updated = upsert_meta_tag(updated, "property", "og:image:secure_url", og_image_url)
    updated = upsert_meta_tag(updated, "property", "og:image:type", "image/png")

    # Twitter
    updated = upsert_meta_tag(updated, "name", "twitter:card", "summary_large_image")
    updated = upsert_meta_tag(updated, "name", "twitter:image", og_image_url)

    changed = updated != html_text
    if changed:
        article_path.write_text(updated, encoding="utf-8")

    return changed, f"Updated {article_path.name}" if changed else f"No change {article_path.name}"


def iter_satire_files() -> list[Path]:
    return sorted(
        [p for p in SATIRE_DIR.glob("*.html") if p.is_file()],
        key=lambda p: p.name.lower(),
    )


def main() -> None:
    if not SATIRE_DIR.exists():
        raise FileNotFoundError(f"Missing satire directory: {SATIRE_DIR}")

    if not OG_DIR.exists():
        raise FileNotFoundError(f"Missing OG directory: {OG_DIR}")

    files = iter_satire_files()
    if not files:
        raise RuntimeError(f"No HTML files found in: {SATIRE_DIR}")

    updated_count = 0
    unchanged_count = 0
    failed_count = 0

    for article_path in files:
        try:
            changed, message = update_article_meta(article_path)
            if changed:
                updated_count += 1
                print(f"[OK] {message}")
            else:
                unchanged_count += 1
                print(f"[SKIP] {message}")
        except Exception as exc:
            failed_count += 1
            print(f"[FAIL] {article_path.name}: {exc}")

    print()
    print(
        f"Done. Updated: {updated_count}, Unchanged: {unchanged_count}, Failed: {failed_count}"
    )


if __name__ == "__main__":
    main()