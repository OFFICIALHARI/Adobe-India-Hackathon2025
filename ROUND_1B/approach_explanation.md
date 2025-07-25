# Approach Explanation: Persona-Driven Document Intelligence

## Overview
The solution is designed to act as a generic, robust document analyst that intelligently extracts and ranks the most relevant sections from a diverse set of PDF documents based on a user-defined persona and job-to-be-done. The architecture is entirely CPU-based, lightweight (<1GB model), and runs fully offline, ensuring reproducibility and compliance with hackathon constraints.

## Methodology

### 1. Input Handling
- **Documents**: Accepts 3–10 PDFs from any domain.
- **Persona & Job**: Loads a JSON describing the persona’s expertise and the specific job-to-be-done.

### 2. Section Extraction
- Uses PyMuPDF to read each PDF and extract text page by page.
- Applies spaCy NLP to detect section headings via heuristics (uppercase sentences, bold text, or fallback to first sentences per page).
- Each detected section is associated with its document and page number.

### 3. Relevance Ranking
- Combines persona and job into a query string.
- Uses a pre-cached SentenceTransformer (MiniLM) to embed both the query and each section.
- Computes semantic similarity (cosine) to rank sections by relevance to the persona’s goal.

### 4. Sub-section Analysis
- Applies TF-IDF across section sentences to surface granular, high-importance subsections.
- Each subsection is refined for conciseness and mapped to its parent section, document, and page.

### 5. Output Generation
- All results are formatted in strict compliance with the provided JSON schema.
- Includes metadata (documents, persona, job, timestamp), ranked sections, and refined sub-section analysis.

## Design Decisions
- **CPU-Only**: All models and libraries are chosen for small size and fast inference on CPUs.
- **Offline**: The model is downloaded and cached at build time; no internet access is needed for runtime.
- **Generality**: Section/subsection extraction is not tuned to any domain, so it generalizes to research, business, education, etc.
- **Speed & Robustness**: Pipeline is optimized for ≤60s processing (3–5 docs) and strict error handling.

## Conclusion
The solution meets all hackathon requirements for accuracy, speed, generality, and reproducibility. It is ready for submission and can be adapted to any persona or document type.