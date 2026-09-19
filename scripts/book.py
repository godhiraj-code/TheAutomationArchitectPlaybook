#!/usr/bin/env python3
"""Offline integrity checks and a deterministic static-site build."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "book_final.md"
HTML = ROOT / "index.html"
ASSETS = ROOT / "assets"
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


class BookHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.headings: list[str] = []
        self._heading_tag: str | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if element_id := attributes.get("id"):
            self.ids.append(element_id)
        for attribute in ("href", "src"):
            if value := attributes.get(attribute):
                self.references.append((attribute, value))
        if re.fullmatch(r"h[1-6]", tag):
            self._heading_tag = tag
            self._heading_text = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag:
            self.headings.append(" ".join("".join(self._heading_text).split()))
            self._heading_tag = None
            self._heading_text = []


def normalize_heading(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"[`*_]", "", value)
    return " ".join(value.split()).casefold()


def markdown_headings_and_links(text: str) -> tuple[list[str], list[str]]:
    headings: list[str] = []
    links: list[str] = []
    fence: str | None = None

    for line_number, line in enumerate(text.splitlines(), 1):
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        if heading_match := re.match(r"^#{1,6}\s+(.+?)\s*$", line):
            headings.append(heading_match.group(1))
        for link_match in re.finditer(r"!?\[[^]]*\]\(([^)]+)\)", line):
            links.append(link_match.group(1).split(maxsplit=1)[0].strip("<>"))

    if fence is not None:
        raise ValueError("book_final.md has an unclosed fenced code block")
    return headings, links


def local_target(reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme.casefold() in EXTERNAL_SCHEMES or parsed.netloc:
        return None
    if not parsed.path:
        return None
    return ROOT / unquote(parsed.path)


def check() -> None:
    errors: list[str] = []
    markdown_text = MARKDOWN.read_text(encoding="utf-8")
    html_text = HTML.read_text(encoding="utf-8")

    try:
        markdown_headings, markdown_links = markdown_headings_and_links(markdown_text)
    except ValueError as exc:
        errors.append(str(exc))
        markdown_headings, markdown_links = [], []

    for reference in markdown_links:
        if target := local_target(reference):
            if not target.exists():
                errors.append(f"book_final.md references missing file: {reference}")

    parser = BookHTMLParser()
    parser.feed(html_text)
    parser.close()

    duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    for element_id in duplicate_ids:
        errors.append(f"index.html contains duplicate id: {element_id}")

    known_ids = set(parser.ids)
    for attribute, reference in parser.references:
        parsed = urlsplit(reference)
        if reference.startswith("#"):
            anchor = unquote(parsed.fragment)
            if anchor and anchor not in known_ids:
                errors.append(f"index.html references missing anchor: #{anchor}")
            continue
        if target := local_target(reference):
            if not target.exists():
                errors.append(
                    f"index.html {attribute} references missing file: {reference}"
                )

    markdown_chapters = [
        heading for heading in markdown_headings if re.match(r"Chapter \d+:", heading)
    ]
    html_heading_set = {normalize_heading(heading) for heading in parser.headings}
    for chapter in markdown_chapters:
        if normalize_heading(chapter) not in html_heading_set:
            errors.append(f"index.html is missing Markdown chapter heading: {chapter}")

    if not html_text.lstrip().casefold().startswith("<!doctype html>"):
        errors.append("index.html is missing an HTML5 doctype")

    if errors:
        raise SystemExit("Book checks failed:\n- " + "\n- ".join(errors))

    print(
        "Book checks passed: "
        f"{len(markdown_headings)} Markdown headings, "
        f"{len(markdown_chapters)} source chapters, "
        f"{len(parser.ids)} HTML ids, and "
        f"{len(parser.references)} HTML references checked."
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output: Path) -> None:
    check()
    output = output.resolve()
    default_output = (ROOT / "dist").resolve()
    if output.is_relative_to(ROOT) and output != default_output:
        raise SystemExit(
            "Refusing output inside the source tree; use ./dist or a directory "
            f"outside the repository: {output}"
        )
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise SystemExit(f"Refusing non-empty output directory: {output}")
    else:
        output.mkdir(parents=True)
    (output / "index.html").write_bytes(HTML.read_bytes())
    target_assets = output / "assets"
    target_assets.mkdir()
    for source in sorted(path for path in ASSETS.rglob("*") if path.is_file()):
        destination = target_assets / source.relative_to(ASSETS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    built_files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = {
        "files": {
            path.relative_to(output).as_posix(): sha256(path) for path in built_files
        },
        "source": {
            "book_final.md": sha256(MARKDOWN),
            "index.html": sha256(HTML),
        },
    }
    (output / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Built verified static site in {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="validate Markdown and HTML integrity")
    build_parser = subparsers.add_parser("build", help="build a verified static site")
    build_parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    if args.command == "check":
        check()
    else:
        build(args.output)


if __name__ == "__main__":
    main()
