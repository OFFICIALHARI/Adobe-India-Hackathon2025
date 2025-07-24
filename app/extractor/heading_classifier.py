import re
from typing import List, Dict

def classify_headings(candidates: List[Dict]) -> List[Dict]:
    """Assigns H1/H2/H3 levels based on font size, style, and layout rules."""
    # Step 1: Sort by font size (desc), collect unique sizes
    sizes = sorted({c["size"] for c in candidates}, reverse=True)
    if not sizes:
        return []
    # Heuristic: Top 1-3 sizes = H1, H2, H3 (tune as needed)
    size_to_level = {}
    if len(sizes) >= 3:
        size_to_level = {sizes[0]: "H1", sizes[1]: "H2", sizes[2]: "H3"}
    elif len(sizes) == 2:
        size_to_level = {sizes[0]: "H1", sizes[1]: "H2"}
    else:
        size_to_level = {sizes[0]: "H1"}

    # Refine: Use bold/caps/numbering for further evidence
    outline = []
    for c in candidates:
        level = size_to_level.get(c["size"])
        if not level:
            continue
        # Bold/caps/numbering bonus (simple rules)
        is_bold = "Bold" in c["font"] or c["flags"] & 2
        is_caps = c["text"].isupper()
        is_numbered = bool(re.match(r'^\d+(\.\d+)*\s', c["text"]))
        if is_bold or is_caps or is_numbered:
            outline.append({
                "level": level,
                "text": c["text"],
                "page": c["page"]
            })
        elif level == "H1":
            # Always include largest font as H1
            outline.append({
                "level": level,
                "text": c["text"],
                "page": c["page"]
            })
    # Remove duplicates by (text, page)
    seen = set()
    res = []
    for o in outline:
        key = (o["level"], o["text"], o["page"])
        if key not in seen:
            seen.add(key)
            res.append(o)
    return res