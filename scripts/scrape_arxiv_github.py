"""
Scrape ArXiv paper and GitHub repo for additional training data
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path


def scrape_arxiv_paper(url):
    """Extract information from ArXiv HTML paper"""
    print(f"📄 Scraping ArXiv paper: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        examples = []

        # Extract sections
        sections = soup.find_all(["section", "h2", "h3"])
        current_section = ""

        for elem in sections:
            if elem.name in ["h2", "h3"]:
                current_section = elem.get_text().strip()
            elif "factorio" in elem.get_text().lower():
                text = elem.get_text()[:400]
                if len(text) > 100:
                    examples.append(
                        {
                            "instruction": f"Explain from FLE research: {current_section}",
                            "input": "",
                            "output": text,
                        }
                    )

        print(f"  ✅ Extracted {len(examples)} examples from ArXiv")
        return examples

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return []


def scrape_github_repo(repo_url):
    """Extract examples from GitHub repo"""
    print(f"🐙 Scraping GitHub repo: {repo_url}")

    examples = []

    try:
        # Get README
        readme_url = f"{repo_url}/raw/main/README.md"
        response = requests.get(readme_url)

        if response.status_code == 200:
            readme = response.text

            # Extract code blocks
            code_blocks = []
            in_code = False
            current_block = []

            for line in readme.split("\n"):
                if line.startswith("```python"):
                    in_code = True
                    current_block = []
                elif line.startswith("```") and in_code:
                    in_code = False
                    if current_block:
                        code = "\n".join(current_block)
                        if len(code) > 50:
                            code_blocks.append(code)
                elif in_code:
                    current_block.append(line)

            for i, code in enumerate(code_blocks[:10]):  # Limit to 10
                examples.append(
                    {
                        "instruction": "Generate Factorio agent code from FLE examples:",
                        "input": f"Example {i + 1} from official repo",
                        "output": code[:400],
                    }
                )

            print(f"  ✅ Extracted {len(examples)} code examples from README")

        return examples

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return []


def main():
    all_examples = []

    # ArXiv paper
    arxiv_examples = scrape_arxiv_paper("https://arxiv.org/html/2503.09617v1")
    all_examples.extend(arxiv_examples)

    # GitHub repo
    github_examples = scrape_github_repo(
        "https://github.com/JackHopkins/factorio-learning-environment"
    )
    all_examples.extend(github_examples)

    # Save
    if all_examples:
        output_path = Path("training_data/arxiv_github.jsonl")
        with open(output_path, "w") as f:
            for ex in all_examples:
                f.write(json.dumps(ex) + "\n")

        print(f"\n✅ Total: {len(all_examples)} examples")
        print(f"✅ Saved to: {output_path}")
    else:
        print("❌ No examples extracted")


if __name__ == "__main__":
    main()
