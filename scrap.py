import re
import time
import unicodedata
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
import html2text


START_URL = "https://jackhopkins.github.io/factorio-learning-environment/sphinx/build/html/"
OUT_FILE = "FLE_docs.md"

SLEEP_BETWEEN_REQUESTS_S = 0.25
REQUEST_TIMEOUT_S = 30


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # Compacte les blancs (sans casser le markdown)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def is_in_scope(url: str, start_netloc: str, start_path: str) -> bool:
    p = urlparse(url)

    # garde http/https uniquement
    if p.scheme not in ("http", "https"):
        return False

    # même domaine
    if p.netloc != start_netloc:
        return False

    # même sous-chemin Sphinx (évite de partir ailleurs)
    if not p.path.startswith(start_path):
        return False

    # ignore assets / fichiers non-doc
    if any(
        p.path.lower().endswith(ext)
        for ext in (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".css",
            ".js",
            ".map",
            ".zip",
            ".tar",
            ".gz",
            ".tgz",
            ".pdf",
            ".ico",
        )
    ):
        return False

    return True


def extract_main_markdown(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    # Sphinx (ReadTheDocs theme & co)
    main = (
        soup.select_one("div.document")
        or soup.select_one("div[role='main']")
        or soup.select_one("main")
        or soup.body
    )
    if not main:
        return title, ""

    # Supprime navigation / sidebar / footer / search etc.
    for sel in [
        "nav",
        "header",
        "footer",
        ".wy-nav-side",
        ".wy-nav-top",
        ".rst-footer-buttons",
        ".sphinxsidebar",
        ".toctree-wrapper",  # optionnel: enlève certains sommaires répétitifs
    ]:
        for node in main.select(sel):
            node.decompose()

    # Convert HTML -> Markdown propre
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = False
    h.body_width = 0  # pas de wrap forcé
    h.ul_item_mark = "-"  # listes propres
    h.single_line_break = False  # respecte les paragraphes

    md = h.handle(str(main))

    md = normalize_text(md)

    # Petits nettoyages de sortie (optionnels)
    # - évite des lignes de "Table of Contents" trop répétitives si ça reste
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    return title, md


def scrape():
    start = urlparse(START_URL)
    start_netloc = start.netloc
    start_path = start.path  # ex: /factorio-learning-environment/sphinx/build/html/

    session = requests.Session()
    session.headers.update({"User-Agent": "doc-scraper/1.0 (personal use)"})

    queue = deque([START_URL])
    visited = set()
    pages: list[tuple[str, str, str]] = []  # (url, title, markdown)

    while queue:
        url = queue.popleft()
        url, _frag = urldefrag(url)  # retire les #anchors

        if url in visited:
            continue
        visited.add(url)

        print(f"[{len(visited):04d}] GET {url}")

        try:
            r = session.get(url, timeout=REQUEST_TIMEOUT_S)
        except requests.RequestException as e:
            print(f"  !! Request failed: {e}")
            continue

        ctype = r.headers.get("Content-Type", "")
        if r.status_code != 200 or "text/html" not in ctype:
            continue

        title, md = extract_main_markdown(r.text)
        if md:
            pages.append((url, title, md))

        # Découverte des liens
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            if not href:
                continue

            abs_url = urljoin(url, href)
            abs_url, _ = urldefrag(abs_url)

            if is_in_scope(abs_url, start_netloc, start_path) and abs_url not in visited:
                queue.append(abs_url)

        time.sleep(SLEEP_BETWEEN_REQUESTS_S)

    # Écriture fichier final
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Factorio Learning Environment docs (scraped)\n\n")
        f.write(f"- Start URL: {START_URL}\n")
        f.write(f"- Pages scraped: {len(pages)}\n\n")
        f.write("---\n\n")

        for url, title, md in pages:
            # Un séparateur clair entre pages
            page_title = title or url
            f.write(f"## {page_title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write(md)
            f.write("\n\n---\n\n")

    print(f"\n✅ Done: {len(pages)} pages written to {OUT_FILE}")


if __name__ == "__main__":
    scrape()
