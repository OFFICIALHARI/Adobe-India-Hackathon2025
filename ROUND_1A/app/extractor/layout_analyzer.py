from typing import List, Dict

def extract_headings_from_blocks(pages_blocks: List[list]) -> List[Dict]:
    """Extracts candidate headings from page blocks with font/size/pos info."""
    candidates = []
    for page_num, blocks in enumerate(pages_blocks, 1):
        for block in blocks:
            if block['type'] != 0:  # text only
                continue
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span['text'].strip()
                    if not text or len(text) < 2:
                        continue
                    candidates.append({
                        "text": text,
                        "font": span['font'],
                        "size": span['size'],
                        "flags": span['flags'],
                        "bbox": span['bbox'],
                        "color": span['color'],
                        "page": page_num
                    })
    return candidates