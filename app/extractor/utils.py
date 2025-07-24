import os

def list_pdfs(input_dir: str):
    return [
        f for f in os.listdir(input_dir)
        if f.lower().endswith('.pdf')
    ]