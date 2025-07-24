import json

def write_json_outline(title: str, outline: list, out_path: str):
    data = {
        "title": title,
        "outline": outline
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)