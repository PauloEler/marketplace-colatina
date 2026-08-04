"""Auditoria técnica de SEO, somente leitura, para o Mercado Colatina."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from xml.etree import ElementTree

import requests


class SEOHTMLParser(HTMLParser):
    """Extrai sinais de SEO sem executar scripts da página."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.open_graph: set[str] = set()
        self.twitter_cards: set[str] = set()
        self.json_ld_count = 0
        self.image_count = 0
        self.images_without_alt: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attributes.get("name", "").lower()
            prop = attributes.get("property", "").lower()
            content = attributes.get("content", "").strip()
            if name == "description":
                self.description = content
            elif name == "robots":
                self.robots = content
            if prop.startswith("og:"):
                self.open_graph.add(prop)
            if name.startswith("twitter:"):
                self.twitter_cards.add(name)
        elif tag == "link":
            rel = {item.lower() for item in attributes.get("rel", "").split()}
            if "canonical" in rel:
                self.canonical = attributes.get("href", "").strip()
        elif (
            tag == "script"
            and attributes.get("type", "").lower() == "application/ld+json"
        ):
            self.json_ld_count += 1
        elif tag == "img":
            self.image_count += 1
            if "alt" not in attributes:
                self.images_without_alt.append(attributes.get("src", ""))
        elif tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def parse_html(html: str) -> SEOHTMLParser:
    parser = SEOHTMLParser()
    parser.feed(html)
    return parser


def normalize_internal_url(base_url: str, current_url: str, href: str) -> str | None:
    absolute = urldefrag(urljoin(current_url, href))[0]
    parsed = urlparse(absolute)
    base = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base.netloc:
        return None
    if parsed.query:
        return None
    path = parsed.path or "/"
    return urlunparse((base.scheme, base.netloc, path, "", "", ""))


def sitemap_urls(xml: str) -> list[str]:
    root = ElementTree.fromstring(xml)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    return [
        node.text.strip()
        for node in root.findall(f"{namespace}url/{namespace}loc")
        if node.text
    ]


def audit_site(base_url: str, max_pages: int = 80) -> dict:
    base_url = base_url.rstrip("/")
    root_url = f"{base_url}/"
    session = requests.Session()
    session.headers["User-Agent"] = "MercadoColatinaSEOAudit/1.0"

    robots_response = session.get(f"{base_url}/robots.txt", timeout=20)
    sitemap_response = session.get(f"{base_url}/sitemap.xml", timeout=20)
    listed_urls = sitemap_urls(sitemap_response.text) if sitemap_response.ok else []

    queue = deque([root_url])
    discovered = {root_url}
    visited: set[str] = set()
    pages: list[dict] = []
    broken: list[dict] = []
    external_redirects: list[dict] = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            response = session.get(url, timeout=20, allow_redirects=True)
        except requests.RequestException as exc:
            broken.append({"url": url, "error": type(exc).__name__})
            continue

        final_parsed = urlparse(response.url)
        if final_parsed.netloc != urlparse(base_url).netloc:
            external_redirects.append(
                {
                    "url": url,
                    "status": response.history[0].status_code
                    if response.history
                    else response.status_code,
                    "destination_host": final_parsed.netloc,
                }
            )
            continue
        if response.status_code >= 400:
            broken.append({"url": url, "status": response.status_code})
        if "text/html" not in response.headers.get("content-type", ""):
            continue

        parser = parse_html(response.text)
        page = {
            "url": url,
            "status": response.status_code,
            "final_url": response.url,
            "title": parser.title,
            "description": parser.description,
            "canonical": parser.canonical,
            "robots": parser.robots,
            "open_graph": sorted(parser.open_graph),
            "twitter_cards": sorted(parser.twitter_cards),
            "json_ld_count": parser.json_ld_count,
            "image_count": parser.image_count,
            "images_without_alt": parser.images_without_alt,
        }
        pages.append(page)

        for href in parser.links:
            target = normalize_internal_url(base_url, response.url, href)
            if target and target not in discovered:
                discovered.add(target)
                queue.append(target)

    title_groups: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        title_groups[page["title"]].append(page["url"])

    return {
        "base_url": base_url,
        "robots": {
            "status": robots_response.status_code,
            "content_type": robots_response.headers.get("content-type", ""),
            "declares_sitemap": "/sitemap.xml" in robots_response.text,
        },
        "sitemap": {
            "status": sitemap_response.status_code,
            "content_type": sitemap_response.headers.get("content-type", ""),
            "url_count": len(listed_urls),
            "urls": listed_urls,
        },
        "summary": {
            "pages_crawled": len(pages),
            "broken_internal_links": broken,
            "external_redirects": external_redirects,
            "missing_canonical": [
                page["url"] for page in pages if not page["canonical"]
            ],
            "missing_description": [
                page["url"] for page in pages if not page["description"]
            ],
            "missing_json_ld": [
                page["url"] for page in pages if page["json_ld_count"] == 0
            ],
            "images_without_alt": {
                page["url"]: page["images_without_alt"]
                for page in pages
                if page["images_without_alt"]
            },
            "duplicate_titles": {
                title: urls
                for title, urls in title_groups.items()
                if title and len(urls) > 1
            },
            "crawlable_not_in_sitemap": [
                page["url"]
                for page in pages
                if page["status"] == 200 and page["url"] not in listed_urls
            ],
            "sitemap_orphans": [url for url in listed_urls if url not in discovered],
        },
        "pages": pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auditoria técnica de SEO somente leitura"
    )
    parser.add_argument("--base-url", default="https://mercadocolatina.com.br")
    parser.add_argument("--max-pages", type=int, default=80)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_site(args.base_url, args.max_pages)
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)


if __name__ == "__main__":
    main()
