"""
Extract training examples from PDF documents
"""

import PyPDF2
import json
import argparse
from pathlib import Path


def pdf_to_examples(pdf_path):
    """Convert PDF to training examples"""
    print(f"Processing {pdf_path}...")

    try:
        reader = PyPDF2.PdfReader(pdf_path)
    except Exception as e:
        print(f"  ❌ Failed to read: {e}")
        return []

    examples = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for para in paragraphs:
            # Skip very short text
            if len(para) < 100:
                continue

            # Skip if doesn't seem Factorio-related
            factorio_keywords = [
                "factorio",
                "resource",
                "mining",
                "craft",
                "smelt",
                "belt",
                "inserter",
                "furnace",
                "drill",
                "assembly",
            ]
            if not any(kw in para.lower() for kw in factorio_keywords):
                continue

            examples.append(
                {
                    "instruction": "Explain based on Factorio documentation:",
                    "input": f"From {pdf_path.name}, page {page_num + 1}",
                    "output": para[:400],  # Limit length
                }
            )

    print(f"  ✅ Extracted {len(examples)} examples")
    return examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default=".", help="Directory containing PDFs")
    parser.add_argument(
        "--output", type=str, default="training_data/from_pdfs.jsonl", help="Output file"
    )
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    pdf_files = list(input_path.glob("**/*.pdf"))

    if not pdf_files:
        print(f"❌ No PDFs found in {input_path}")
        return

    print(f"Found {len(pdf_files)} PDF files")

    all_examples = []
    for pdf_file in pdf_files:
        examples = pdf_to_examples(pdf_file)
        all_examples.extend(examples)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex) + "\n")

    print(f"\n✅ Total: {len(all_examples)} examples")
    print(f"✅ Saved to: {output_path}")


if __name__ == "__main__":
    main()
