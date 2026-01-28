#!/usr/bin/env python3
"""
Script pour scraper toute la documentation Factorio Learning Environment
et générer un fichier Markdown avec tout le contenu
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque
import re


class DocScraper:
    def __init__(self, base_urls):
        self.base_urls = base_urls
        self.visited = set()
        self.content = []
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    def is_valid_url(self, url):
        """Vérifie si l'URL appartient à la documentation"""
        parsed = urlparse(url)
        for base_url in self.base_urls:
            base_parsed = urlparse(base_url)
            if parsed.netloc == base_parsed.netloc and parsed.path.startswith(
                base_parsed.path.rsplit("/", 1)[0]
            ):
                return True
        return False

    def clean_text(self, text):
        """Nettoie le texte en supprimant les espaces superflus"""
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()

    def extract_content(self, soup, url):
        """Extrait le contenu principal de la page"""
        # Essayer différents sélecteurs pour le contenu principal
        main_content = None

        # Pour les pages Sphinx
        selectors = [
            "div.document",
            "div.body",
            "main",
            'div[role="main"]',
            "article",
            "div.content",
        ]

        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.find("body")

        if not main_content:
            return None

        # Récupérer le titre
        title = soup.find("h1")
        if not title:
            title = soup.find("title")

        title_text = title.get_text().strip() if title else url

        # Créer le contenu markdown
        md_content = f"\n\n{'='*80}\n"
        md_content += f"# {title_text}\n"
        md_content += f"**URL:** {url}\n"
        md_content += f"{'='*80}\n\n"

        # Convertir le HTML en Markdown basique
        md_content += self.html_to_markdown(main_content)

        return md_content

    def html_to_markdown(self, element):
        """Convertit HTML en Markdown de manière basique"""
        md = ""

        for child in element.children:
            if child.name is None:  # Texte brut
                text = str(child).strip()
                if text:
                    md += text + " "

            elif child.name == "h1":
                md += f"\n\n# {child.get_text().strip()}\n\n"
            elif child.name == "h2":
                md += f"\n\n## {child.get_text().strip()}\n\n"
            elif child.name == "h3":
                md += f"\n\n### {child.get_text().strip()}\n\n"
            elif child.name == "h4":
                md += f"\n\n#### {child.get_text().strip()}\n\n"
            elif child.name == "h5":
                md += f"\n\n##### {child.get_text().strip()}\n\n"
            elif child.name == "h6":
                md += f"\n\n###### {child.get_text().strip()}\n\n"

            elif child.name == "p":
                md += f"\n{child.get_text().strip()}\n"

            elif child.name == "pre":
                code = child.get_text().strip()
                md += f"\n```\n{code}\n```\n"

            elif child.name == "code":
                md += f"`{child.get_text().strip()}`"

            elif child.name == "ul":
                for li in child.find_all("li", recursive=False):
                    md += f"- {li.get_text().strip()}\n"
                md += "\n"

            elif child.name == "ol":
                for i, li in enumerate(child.find_all("li", recursive=False), 1):
                    md += f"{i}. {li.get_text().strip()}\n"
                md += "\n"

            elif child.name == "a":
                href = child.get("href", "")
                text = child.get_text().strip()
                if href and text:
                    md += f"[{text}]({href})"
                else:
                    md += text

            elif child.name == "strong" or child.name == "b":
                md += f"**{child.get_text().strip()}**"

            elif child.name == "em" or child.name == "i":
                md += f"*{child.get_text().strip()}*"

            elif child.name == "table":
                md += self.table_to_markdown(child)

            elif child.name in ["div", "section", "article", "dl", "dd", "dt"]:
                md += self.html_to_markdown(child)

            elif child.name == "br":
                md += "\n"

            else:
                # Pour les autres éléments, récupérer le texte
                text = child.get_text().strip()
                if text:
                    md += text + " "

        return md

    def table_to_markdown(self, table):
        """Convertit une table HTML en Markdown"""
        md = "\n"
        rows = table.find_all("tr")

        if not rows:
            return md

        # En-têtes
        headers = rows[0].find_all(["th", "td"])
        if headers:
            md += "| " + " | ".join(h.get_text().strip() for h in headers) + " |\n"
            md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Lignes de données
        for row in rows[1:] if headers else rows:
            cells = row.find_all(["td", "th"])
            if cells:
                md += "| " + " | ".join(c.get_text().strip() for c in cells) + " |\n"

        return md + "\n"

    def get_all_links(self, soup, current_url):
        """Extrait tous les liens de la page"""
        links = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Ignorer les ancres, mailto, etc.
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
                continue

            # Convertir en URL absolue
            absolute_url = urljoin(current_url, href)

            # Retirer les fragments
            absolute_url = absolute_url.split("#")[0]

            if self.is_valid_url(absolute_url):
                links.add(absolute_url)

        return links

    def scrape(self):
        """Lance le scraping de toutes les pages"""
        queue = deque(self.base_urls)

        print("Début du scraping...")

        while queue:
            url = queue.popleft()

            if url in self.visited:
                continue

            print(f"Scraping: {url}")
            self.visited.add(url)

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Extraire le contenu
                content = self.extract_content(soup, url)
                if content:
                    self.content.append(content)

                # Trouver tous les liens
                links = self.get_all_links(soup, url)
                for link in links:
                    if link not in self.visited:
                        queue.append(link)

                # Petit délai pour ne pas surcharger le serveur
                time.sleep(0.5)

            except Exception as e:
                print(f"Erreur lors du scraping de {url}: {e}")
                continue

        print(f"\nScraping terminé! {len(self.visited)} pages visitées.")

    def save_to_file(self, filename):
        """Sauvegarde tout le contenu dans un fichier Markdown"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Documentation Factorio Learning Environment\n\n")
            f.write(f"Documentation complète scrapée le {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total de pages scrapées:** {len(self.visited)}\n\n")
            f.write("---\n\n")

            # Table des matières
            f.write("## Table des matières\n\n")
            for i, url in enumerate(sorted(self.visited), 1):
                f.write(f"{i}. {url}\n")
            f.write("\n---\n")

            # Contenu
            for content in self.content:
                cleaned = self.clean_text(content)
                f.write(cleaned)
                f.write("\n\n")

        print(f"Documentation sauvegardée dans: {filename}")


if __name__ == "__main__":
    # URLs de départ
    base_urls = [
        "https://jackhopkins.github.io/factorio-learning-environment/versions/0.3.0.html",
        "https://jackhopkins.github.io/factorio-learning-environment/sphinx/build/html/",
    ]

    scraper = DocScraper(base_urls)
    scraper.scrape()
    scraper.save_to_file("factorio_doc_complete.md")

    print("\n✅ Scraping terminé avec succès!")
