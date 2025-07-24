from extractor.heading_classifier import classify_headings

def test_classify_headings_basic():
    candidates = [
        {"text": "MAIN TITLE", "font": "Arial-Bold", "size": 24, "flags": 2, "bbox": (0,0,100,20), "color": 0, "page": 1},
        {"text": "Section 1", "font": "Arial-Bold", "size": 18, "flags": 2, "bbox": (0,20,100,40), "color": 0, "page": 1},
        {"text": "Detail", "font": "Arial", "size": 14, "flags": 0, "bbox": (0,40,100,55), "color": 0, "page": 2},
    ]
    outline = classify_headings(candidates)
    assert outline[0]["level"] == "H1"
    assert outline[1]["level"] == "H2"
    assert outline[2]["level"] == "H3"
