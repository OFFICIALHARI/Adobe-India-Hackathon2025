import fitz

def extract_pdf_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")
        sections.append({
            "title": f"Page {page_num+1}",
            "page": page_num + 1,
            "text": text
        })
    doc.close()
    return sections