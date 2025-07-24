import os
from extractor.loader import load_pdf, get_pdf_title, get_page_text_blocks
from extractor.layout_analyzer import extract_headings_from_blocks
from extractor.heading_classifier import classify_headings
from extractor.serializer import write_json_outline
from extractor.utils import list_pdfs
from extractor.multilingual import detect_lang

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def process_pdf(pdf_path, output_path):
    doc = load_pdf(pdf_path)
    title = get_pdf_title(doc)
    blocks = get_page_text_blocks(doc)
    candidates = extract_headings_from_blocks(blocks)
    outline = classify_headings(candidates)
    write_json_outline(title, outline, output_path)

def main():
    pdfs = list_pdfs(INPUT_DIR)
    for pdf_file in pdfs:
        in_path = os.path.join(INPUT_DIR, pdf_file)
        base = os.path.splitext(pdf_file)[0]
        out_path = os.path.join(OUTPUT_DIR, f"{base}.json")
        print(f"Processing {pdf_file}...")
        process_pdf(in_path, out_path)
        print(f"Saved {base}.json")

if __name__ == "__main__":
    main()