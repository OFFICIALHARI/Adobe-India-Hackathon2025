# Persona-Driven Document Intelligence Solution

## Setup & Usage

### 1. Build Docker Image
```bash
docker build -t adobe_persona_docai .
```

### 2. Prepare Input
- Place 3–10 PDFs in `data/input_pdfs/`
- Edit `data/persona.json` with your persona and job-to-be-done

### 3. Run the Solution
```bash
docker run --rm -v "$PWD:/app" adobe_persona_docai
```
- On Windows (PowerShell):
```powershell
docker run --rm -v "${PWD}:/app" adobe_persona_docai
```
- If you have issues with `${PWD}`, use the full path to your folder:
```powershell
docker run --rm -v "C:\path\to\your\project:/app" adobe_persona_docai
```

### 4. Output
- Results are written to `output/output.json` in strict challenge format.

## Files
- All code is in `main.py` and `utils/pdf_parser.py`
- `approach_explanation.md` explains the full methodology

## Technical
- All dependencies are handled
- No internet is required at runtime
- CPU-only, fast (<60s for 3–5 PDFs), model size ≤1GB

## For technical questions, check `approach_explanation.md` or open an issue.
