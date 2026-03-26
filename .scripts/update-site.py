#!/usr/bin/env python3

from __future__ import annotations

import html
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree.ElementTree import Element, SubElement, tostring


REPO_ROOT = Path(__file__).resolve().parent.parent
SATIRE_DIR = REPO_ROOT / "satire"
LATEST_SATIRE_FILE = REPO_ROOT / "latest-satire.html"
SITEMAP_FILE = REPO_ROOT / "sitemap.xml"

SITE_URL = "https://bsteenkampwrites.com"

# Files that should never appear in the sitemap.
EXCLUDED_FILES = {
    "nav.html",
    "foot.html",
    "access.html",
    "latest-satire.html",
}

# Optional directories to skip completely.
EXCLUDED_DIR_NAMES = {
    ".git",
    ".github",
    ".scripts",
    "node_modules",
    "__pycache__",
}


@dataclass
class SatirePiece:
    published_raw: str
    published_dt: datetime
    title: str
    subtitle: str
    url: str


def extract(pattern: str, text: str, flags: int = re.IGNORECASE | re.DOTALL) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else None


def strip_tags(value: str) -> str:
    no_tags = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(no_tags)).strip()


def parse_datetime(value: str) -> datetime:
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f"Unsupported datetime format: {value}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def collect_satire_pieces() -> list[SatirePiece]:
    if not SATIRE_DIR.exists():
        raise SystemExit("satire directory not found")

    pieces: list[SatirePiece] = []

    for file_path in sorted(SATIRE_DIR.glob("*.html")):
        html_text = file_path.read_text(encoding="utf-8")

        published = extract(r'<time[^>]*datetime="([^"]+)"', html_text)
        title = extract(r'<h1[^>]*id="page-title"[^>]*>(.*?)</h1>', html_text)
        subtitle = extract(r'<p[^>]*class="subtitle"[^>]*>(.*?)</p>', html_text)

        if not published or not title:
            continue

        title_clean = strip_tags(title)
        subtitle_clean = strip_tags(subtitle) if subtitle else ""

        try:
            published_dt = parse_datetime(published)
        except ValueError:
            continue

        pieces.append(
            SatirePiece(
                published_raw=published,
                published_dt=published_dt,
                title=title_clean,
                subtitle=subtitle_clean,
                url=f"/satire/{file_path.name}",
            )
        )

    if not pieces:
        raise SystemExit("No valid satire pages with <time datetime> and page-title found")

    return pieces


def write_latest_satire_partial(latest: SatirePiece) -> None:
    output = (
        f'<p>\n'
        f'  <a id="radioactive-button" href="{latest.url}">\n'
        f'    Read the latest satire: {html.escape(latest.title)}\n'
        f'  </a>\n'
        f'</p>\n'
    )
    LATEST_SATIRE_FILE.write_text(output, encoding="utf-8")


def iter_html_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.html"):
        relative = path.relative_to(root)

        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
            continue

        if path.name in EXCLUDED_FILES:
            continue

        yield path


def path_to_url(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).as_posix()

    if relative == "index.html":
        return f"{SITE_URL}/"

    if relative.endswith("/index.html"):
        directory = relative[:-len("index.html")].rstrip("/")
        return f"{SITE_URL}/{directory}/"

    return f"{SITE_URL}/{relative}"


def get_last_commit_iso(path: Path) -> str | None:
    relative = path.relative_to(REPO_ROOT).as_posix()

    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", relative],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    value = result.stdout.strip()
    return value or None


def build_sitemap() -> None:
    urlset = Element(
        "urlset",
        attrib={"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"},
    )

    html_files = sorted(iter_html_files(REPO_ROOT))

    for file_path in html_files:
        url = SubElement(urlset, "url")

        loc = SubElement(url, "loc")
        loc.text = path_to_url(file_path)

        last_commit = get_last_commit_iso(file_path)
        if last_commit:
            lastmod = SubElement(url, "lastmod")
            lastmod.text = last_commit

    xml_bytes = tostring(urlset, encoding="utf-8", xml_declaration=True)
    SITEMAP_FILE.write_bytes(xml_bytes + b"\n")


def main() -> None:
    pieces = collect_satire_pieces()
    latest = max(pieces, key=lambda p: p.published_dt)

    write_latest_satire_partial(latest)
    build_sitemap()

    print("Generated latest-satire.html for:")
    print(f"  Title: {latest.title}")
    print(f"  URL:   {latest.url}")
    print(f"  Date:  {latest.published_raw}")
    print("Generated sitemap.xml")


if __name__ == "__main__":
    main()