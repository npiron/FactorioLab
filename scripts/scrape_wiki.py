"""
Scrape Factorio Wiki for training data
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time
from tqdm import tqdm

BASE_URL = "https://wiki.factorio.com"

# Pages importantes du Wiki Factorio
IMPORTANT_PAGES = [
    # Resources de base
    "/Iron_ore",
    "/Copper_ore",
    "/Coal",
    "/Stone",
    "/Wood",
    "/Crude_oil",
    "/Water",
    "/Uranium_ore",
    # Items intermédiaires
    "/Iron_plate",
    "/Copper_plate",
    "/Steel_plate",
    "/Stone_brick",
    "/Iron_gear_wheel",
    "/Copper_cable",
    "/Electronic_circuit",
    "/Advanced_circuit",
    "/Processing_unit",
    # Buildings de production
    "/Stone_furnace",
    "/Steel_furnace",
    "/Electric_furnace",
    "/Assembling_machine_1",
    "/Assembling_machine_2",
    "/Assembling_machine_3",
    "/Chemical_plant",
    "/Oil_refinery",
    # Mining et extraction
    "/Burner_mining_drill",
    "/Electric_mining_drill",
    "/Pumpjack",
    "/Offshore_pump",
    # Logistique
    "/Transport_belt",
    "/Fast_transport_belt",
    "/Express_transport_belt",
    "/Inserter",
    "/Fast_inserter",
    "/Long_handed_inserter",
    "/Stack_inserter",
    "/Underground_belt",
    "/Splitter",
    # Stockage
    "/Wooden_chest",
    "/Iron_chest",
    "/Steel_chest",
    "/Storage_tank",
    # Énergie
    "/Burner_inserter",
    "/Electric_mining_drill",
    "/Steam_engine",
    "/Boiler",
    "/Solar_panel",
    "/Accumulator",
    "/Nuclear_reactor",
    # Technologies clés
    "/Automation",
    "/Logistics",
    "/Electronics",
    "/Steel_processing",
    "/Oil_processing",
    "/Advanced_oil_processing",
    # Concepts
    "/Tutorial:Main_bus",
    "/Tutorial:Train_signals",
    "/Balancer_mechanics",
    "/Tutorial:Circuit_network_cookbook",
]


def scrape_page(url):
    """Scrape une page Wiki et extrait le contenu"""
    try:
        response = requests.get(BASE_URL + url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Titre
        title_elem = soup.find("h1", {"id": "firstHeading"})
        if not title_elem:
            return None
        title = title_elem.text.strip()

        # Contenu principal
        content_div = soup.find("div", {"class": "mw-parser-output"})
        if not content_div:
            return None

        # Extraire paragraphes
        paragraphs = content_div.find_all("p", limit=5)
        text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

        # Filtrage qualité
        if len(text) < 100:
            return None

        # Nettoyer le texte
        text = text.replace("\n\n\n", "\n")
        text = text[:600]  # Limiter longueur

        return {
            "instruction": "Explain based on Factorio documentation:",
            "input": f"What is {title} in Factorio?",
            "output": text,
        }

    except Exception as e:
        print(f"  ❌ Error scraping {url}: {e}")
        return None


def scrape_wiki_category(category_url, limit=20):
    """Scrape une catégorie entière du Wiki"""
    examples = []
    try:
        response = requests.get(BASE_URL + category_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Trouver tous les liens dans la catégorie
        links = soup.find_all("a", href=True, limit=limit)
        wiki_links = [
            link_tag["href"]
            for link_tag in links
            if link_tag["href"].startswith("/") and ":" not in link_tag["href"]
        ]

        for link in tqdm(wiki_links[:limit], desc=f"Scraping {category_url}"):
            example = scrape_page(link)
            if example:
                examples.append(example)
            time.sleep(0.5)  # Rate limiting

    except Exception as e:
        print(f"Error with category {category_url}: {e}")

    return examples


def main():
    print("🌐 Starting Factorio Wiki scraping...")
    examples = []

    # Scraper pages importantes
    for page in tqdm(IMPORTANT_PAGES, desc="Scraping Wiki"):
        example = scrape_page(page)
        if example:
            examples.append(example)
        time.sleep(1.0)  # Respecter le serveur

    # Optionnel: scraper catégories supplémentaires
    # category_examples = scrape_wiki_category("/Category:Items", limit=30)
    # examples.extend(category_examples)

    # Sauvegarder
    if examples:
        output_path = Path("training_data/wiki_scraped.jsonl")
        with open(output_path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"\n✅ Scraped {len(examples)} wiki pages")
        print(f"✅ Saved to: {output_path}")

        # Stats
        avg_len = sum(len(ex["output"]) for ex in examples) / len(examples)
        print(f"📊 Average output length: {avg_len:.0f} chars")
    else:
        print("❌ No examples scraped")


if __name__ == "__main__":
    main()
