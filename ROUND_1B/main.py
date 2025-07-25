import os
import json
import time
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

# Load persona/job
with open('data/persona.json', 'r', encoding='utf-8') as f:
    persona_data = json.load(f)

persona = persona_data.get("persona")
job_to_be_done = persona_data.get("job_to_be_done")

# Model load (offline, cached)
embed_model = SentenceTransformer('./models/embed_model')

# Load Spacy model (small, fast)
spacy_nlp = spacy.load("en_core_web_sm")

input_dir = "data/input_pdfs"
pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")
        # Section detection: Use Spacy for heading detection (simple heuristic)
        doc_nlp = spacy_nlp(text)
        for sent in doc_nlp.sents:
            if sent.text.strip().isupper() and len(sent.text.strip()) > 5:
                sections.append({
                    "title": sent.text.strip(),
                    "page": page_num + 1,
                    "text": text
                })
    # If no uppercase headings, fallback to first N sentences as sections
    if not sections:
        for page_num in range(len(doc)):
            text = doc[page_num].get_text("text")
            doc_nlp = spacy_nlp(text)
            for i, sent in enumerate(doc_nlp.sents):
                if i < 3:  # first 3 sentences as "sections"
                    sections.append({
                        "title": f"Section page {page_num+1}-{i+1}",
                        "page": page_num + 1,
                        "text": sent.text
                    })
    doc.close()
    return sections

def rank_sections(sections, persona, job_to_be_done):
    # Combine persona and job into a query embedding
    query = f"{persona}: {job_to_be_done}"
    query_emb = embed_model.encode([query])[0]
    scores = []
    for sec in sections:
        sec_emb = embed_model.encode([sec['title'] + " " + sec['text']])[0]
        sim = np.dot(query_emb, sec_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(sec_emb))
        scores.append(sim)
    ranked = sorted(zip(sections, scores), key=lambda x: x[1], reverse=True)
    for i, (sec, score) in enumerate(ranked):
        sec['importance_rank'] = i + 1
        sec['score'] = score
    return [sec for sec, score in ranked]

def extract_subsections(section):
    # Use TF-IDF to extract top sentences as "subsections"
    sentences = [s for s in section['text'].split('\n') if len(s.strip()) > 20]
    if not sentences:
        sentences = section['text'].split('.')
    tfidf = TfidfVectorizer().fit_transform(sentences)
    scores = np.asarray(tfidf.sum(axis=1)).ravel()
    ranked_idx = np.argsort(scores)[::-1][:3]
    subsections = []
    for idx in ranked_idx:
        subsections.append({
            "document": section.get("doc", ""),
            "refined_text": sentences[idx].strip(),
            "page_number": section["page"]
        })
    return subsections

metadata = {
    "input_documents": [os.path.basename(f) for f in pdf_files],
    "persona": persona,
    "job_to_be_done": job_to_be_done,
    "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

extracted_sections = []
sub_sections = []

for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
    sections = extract_sections(pdf_path)
    ranked_sections = rank_sections(sections, persona, job_to_be_done)
    for sec in ranked_sections[:5]:  # top 5 sections per doc
        sec['document'] = os.path.basename(pdf_path)
        extracted_sections.append({
            "document": sec['document'],
            "page_number": sec['page'],
            "section_title": sec['title'],
            "importance_rank": sec['importance_rank']
        })
        for sub in extract_subsections(sec):
            sub['document'] = sec['document']
            sub['page_number'] = sec['page']
            sub_sections.append(sub)

output_json = {
    "metadata": metadata,
    "extracted_sections": extracted_sections,
    "sub_section_analysis": sub_sections
}

os.makedirs("output", exist_ok=True)
with open("output/output.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)

print("✅ Output written to output/output.json")