import os
import json
import time
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import numpy as np
from tqdm import tqdm
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import io

# Redirect stdout and stderr to a StringIO object
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = new_stdout = io.StringIO()
sys.stderr = new_stderr = io.StringIO()

# Load persona/job
with open('data/persona.json', 'r', encoding='utf-8') as f:
    persona_data = json.load(f)

persona = persona_data.get("persona")
job_to_be_done = persona_data.get("job_to_be_done")

# Model load (offline, from local path)
# Ensure 'all-MiniLM-L6-v2' is downloaded and saved to './models/embed_model' during Docker build
embed_model = SentenceTransformer('./models/embed_model')

input_dir = "data/input_pdfs"
pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    all_sections = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        current_section_title = f"Page {page_num + 1} Content" # Default title
        current_section_content_lines = []
        
        # Determine the most common font size on the page (likely body text)
        all_font_sizes = []
        for b in blocks:
            if b["type"] == 0: # text block
                for line in b["lines"]:
                    for span in line["spans"]:
                        all_font_sizes.append(span["size"])
        
        if not all_font_sizes:
            # If no text on page, and there's accumulated content, save it
            if current_section_content_lines:
                all_sections.append({
                    "title": current_section_title,
                    "page": page_num + 1,
                    "text": "\n".join(current_section_content_lines).strip()
                })
            continue # Skip to next page if no text
            
        # Calculate body_font_size more robustly, e.g., median or mode of smaller fonts
        # For now, keep it simple, but acknowledge this might be an issue for complex PDFs
        body_font_size = Counter(all_font_sizes).most_common(1)[0][0]
        print(f"Page {page_num + 1} Body Font Size: {body_font_size}") # Debug print

        for b_idx, b in enumerate(blocks):
            if b["type"] == 0: # text block
                if not b["lines"]:
                    continue

                first_span_of_block = b["lines"][0]["spans"][0]
                span_text = first_span_of_block["text"].strip()
                span_size = first_span_of_block["size"]
                span_is_bold = bool(first_span_of_block["flags"] & 1)
                
                print(f"  Span: '{span_text}', Size: {span_size}, Bold: {span_is_bold}") # Detailed debug print

                is_potential_heading = False
                # Heuristic for a heading: significantly larger font size OR bold and at least body font size
                # Relaxed font size threshold and removed length constraints
                if (span_size > body_font_size * 1.1) or (span_is_bold and span_size >= body_font_size):
                    is_potential_heading = True
                
                # Special consideration for the very first text block on a page
                if b_idx == 0 and not is_potential_heading and len(span_text) < 100: # If first block and not already a heading
                    is_potential_heading = True # Treat it as a heading
                    print(f"  First block on page treated as heading: '{span_text}'") # Debug print

                # Extract content of the current block
                block_content_lines = []
                for line in b["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    block_content_lines.append(line_text.strip())

                if is_potential_heading:
                    # If we have accumulated content for the previous section, save it
                    if current_section_content_lines:
                        all_sections.append({
                            "title": current_section_title,
                            "page": page_num + 1,
                            "text": "\n".join(current_section_content_lines).strip()
                        })
                        print(f"  Saved section: '{current_section_title}' with content snippet: '{current_section_content_lines[0][:50]}...')") # Debug print

                    # Start a new section with this heading
                    current_section_title = span_text
                    current_section_content_lines = [] # Reset content for the new section
                    print(f"  New Section Title Set: '{current_section_title}'") # Debug print

                # Add the content of the current block to the current section
                current_section_content_lines.extend(block_content_lines)

        # After processing all blocks on a page, add the last accumulated section
        if current_section_content_lines:
            all_sections.append({
                "title": current_section_title,
                "page": page_num + 1,
                "text": "\n".join(current_section_content_lines).strip()
            })
            print(f"  Saved final section on page: '{current_section_title}' with content snippet: '{current_section_content_lines[0][:50]}...')") # Debug print

    doc.close()
    print("Extracted Sections (Final):") # Debug print
    for sec in all_sections:
        print(f"  Title: {sec['title']}, Page: {sec['page']}, Text Snippet: {sec['text'][:100]}...") # Debug print
    return all_sections

def rank_sections(sections, persona, job_to_be_done):
    query = f"{persona}: {job_to_be_done}"
    query_emb = embed_model.encode([query])[0]
    scores = []
    for sec in sections:
        # Use a combination of title and a snippet of text for embedding
        text_snippet = sec['text'][:200] # Take first 200 chars of text
        sec_emb = embed_model.encode([sec['title'] + " " + text_snippet])[0]
        sim = np.dot(query_emb, sec_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(sec_emb))
        scores.append(sim)
    
    # Sort sections by score and assign importance_rank
    ranked_sections_with_scores = sorted(zip(sections, scores), key=lambda x: x[1], reverse=True)
    
    final_ranked_sections = []
    for i, (sec, score) in enumerate(ranked_sections_with_scores):
        sec['importance_rank'] = i + 1
        sec['score'] = score # Keep score for debugging/analysis if needed
        final_ranked_sections.append(sec)
        
    return final_ranked_sections

def extract_subsections(section, persona, job_to_be_done):
    # Split text into sentences, filter out very short ones
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', section['text']) if len(s.strip()) > 20]
    if not sentences:
        return []
    
    # Combine persona, job, and section title for a more relevant TF-IDF weighting
    query_text = f"{persona} {job_to_be_done} {section['title']}"
    
    # Add the query to the sentences for TF-IDF calculation to get terms relevant to the query
    corpus = [query_text] + sentences
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # The first row of tfidf_matrix corresponds to the query
    # We want to find sentences most similar to the query based on TF-IDF
    query_vector = tfidf_matrix[0]
    
    sentence_scores = []
    # Iterate through original sentences (skip the query in corpus)
    for i, sentence in enumerate(sentences):
        # Get the TF-IDF vector for the current sentence (index i+1 because corpus includes query)
        sentence_vector = tfidf_matrix[i+1]
        
        # Calculate cosine similarity between query_vector and sentence_vector
        # For sparse matrices, dot product is efficient
        similarity = (query_vector * sentence_vector.T).toarray()[0][0]
        sentence_scores.append(similarity)

    # Rank sentences by their calculated score
    ranked_sentences_with_scores = sorted(zip(sentences, sentence_scores), key=lambda x: x[1], reverse=True)
    
    subsections = []
    # Take top 3 sentences, or fewer if not enough
    for sent, score in ranked_sentences_with_scores[:3]:
        subsections.append({
            "document": section.get("document", ""),
            "refined_text": sent,
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
    
    # Collect all sections from all documents first, then rank globally.
    for sec in ranked_sections: # All sections from this PDF
        sec['document'] = os.path.basename(pdf_path)
        extracted_sections.append(sec) # Add the full section object

# Now, globally rank all extracted sections
# The 'importance_rank' and 'score' are already set per-document.
# We need to re-rank them globally.
# Let's re-sort `extracted_sections` based on their 'score'
extracted_sections = sorted(extracted_sections, key=lambda x: x['score'], reverse=True)

# Re-assign importance_rank globally
for i, sec in enumerate(extracted_sections):
    sec['importance_rank'] = i + 1

# Now, process sub-sections for the top N sections (e.g., top 5 or all if few)
# Let's take the top 5 sections for sub-section analysis as per the original code's intent
for sec in extracted_sections[:5]: # Process top 5 sections for sub-sections
    # Ensure 'document' and 'page' are present in the section object for extract_subsections
    # They should be from the previous steps.
    for sub in extract_subsections(sec, persona, job_to_be_done):
        sub_sections.append(sub)

# Filter extracted_sections to only include the fields required by the output format
final_extracted_sections_output = []
for sec in extracted_sections:
    final_extracted_sections_output.append({
        "document": sec['document'],
        "page_number": sec['page'],
        "section_title": sec['title'],
        "importance_rank": sec['importance_rank']
    })
    
# Limit to top 5 extracted sections for the output JSON, as per sample output
final_extracted_sections_output = final_extracted_sections_output[:5]


output_json = {
    "metadata": metadata,
    "extracted_sections": final_extracted_sections_output,
    "sub_section_analysis": sub_sections
}

print(f"output_json content: {output_json}")
os.makedirs("output", exist_ok=True)
with open("output/output.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)

# Restore stdout and stderr
sys.stdout = old_stdout
sys.stderr = old_stderr

# Write captured output to a file
with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write(new_stdout.getvalue())
    f.write(new_stderr.getvalue())

print("Output written to output/output.json and debug_output.txt")