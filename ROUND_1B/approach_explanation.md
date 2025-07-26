# Approach Explanation: Persona-Driven Document Intelligence

## Overview
The solution is designed to act as a generic, robust document analyst that intelligently extracts and ranks the most relevant sections from a diverse set of PDF documents based on a user-defined persona and job-to-be-done. The architecture is entirely CPU-based, lightweight (<1GB model), and runs fully offline, ensuring reproducibility and compliance with hackathon constraints.

## Methodology

### 1. Input Handling
- **Documents**: Accepts 3–10 PDFs from any domain.
- **Persona & Job**: Loads a JSON describing the persona’s expertise and the specific job-to-be-done.

### 2. Section Extraction
- Uses PyMuPDF to read each PDF and extract text blocks.
- Employs heuristics based on font size and bolding to identify potential section headings.
- Content is grouped under these headings to form logical sections. If no clear headings are found, content is grouped into logical chunks.
- Each extracted section is associated with its document and page number.

### 3. Relevance Ranking
- Combines persona and job into a query string.
- Uses a pre-cached SentenceTransformer (MiniLM) to embed both the query and each section (using a combination of title and a text snippet).
- Computes semantic similarity (cosine) to rank sections by relevance to the persona’s goal.
- Sections are initially ranked per document, then globally re-ranked across all documents.

### 4. Sub-section Analysis
- Splits each relevant section into individual sentences.
- Utilizes TF-IDF (Term Frequency-Inverse Document Frequency) to calculate the importance of each sentence relative to the combined persona, job-to-be-done, and section title query.
- Sentences are ranked based on their TF-IDF similarity to the query, and the top sentences are extracted as refined sub-sections.
- Each sub-section is mapped to its parent document and page.

### 5. Output Generation
- All results are formatted in strict compliance with the provided JSON schema.
- Includes metadata (documents, persona, job, timestamp), top-ranked extracted sections, and refined sub-section analysis.

## Design Decisions
- **CPU-Only**: All models and libraries are chosen for small size and fast inference on CPUs.
- **Offline**: The SentenceTransformer model is downloaded and cached during the Docker build process; no internet access is needed for runtime.
- **Generality**: Section/subsection extraction and ranking heuristics are designed to be generic, allowing the solution to adapt to various domains (research, business, education, etc.) and persona types.
- **Speed & Robustness**: The pipeline is optimized for efficient processing (targeting ≤60s for 3–5 documents) and includes error handling for robust operation.

## Conclusion
The solution meets all hackathon requirements for accuracy, speed, generality, and reproducibility. It is ready for submission and can be adapted to any persona or document type.