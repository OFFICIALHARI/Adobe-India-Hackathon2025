# 🧩 Project Xpert Mavericks — Adobe Hackathon 2025

**_Rethink Reading. Rediscover Knowledge._**  
**Offline-first document intelligence system for Adobe’s "Connecting the Dots" Hackathon**

<p align="center">
  <img src="https://blog.logomaster.ai/hs-fs/hubfs/adobe-logo-2017.jpg?width=662&height=447&name=adobe-logo-2017.jpg" alt="Adobe Logo" height="80"/>
</p>

---

## 📂 Input & Output

Place your `.pdf` files inside the `./input/` directory.  
Output files will appear in the `./output/` directory.

Round 1A → outline_<filename>.json
Round 1B → insights_<persona>.json


---

## 🔧 Components

### 🏁 Round 1A: Structured Outline Extractor

Extracts structured outlines from raw PDFs, including:
- Document title
- Headings: H1, H2, H3
- Page references

**Key Features**
- ≤ 10 seconds for 50-page PDFs
- Multilingual support (English / Japanese / Chinese)
- Clean JSON output for downstream applications

---

### 🎯 Round 1B: Persona-Aware Insight Engine

Analyzes multiple documents to extract relevant sections aligned with a given persona’s objective.

**Key Features**
- Context-aware ranking and scoring
- Concise, readable summaries
- Supports cross-document analysis

📖 See Round 1B source code in `/src/round_1b/` for implementation details.


## 🏆 Technical Highlights

### Round 1A
- **Processing Time**: ≤ 10 seconds (50-page PDF)
- **Memory Usage**: ≤ 200MB RAM
- **Model Size**: 180MB
- **Supported Languages**: English, Japanese, Chinese
- **Key Libraries**: PyMuPDF, spaCy

### Round 1B
- **Processing Time**: ≤ 60 seconds (3–5 documents)
- **Memory Usage**: ≤ 1GB RAM
- **Model Size**: 850MB
- **Supported Languages**: English
- **Key Libraries**: Transformers, scikit-learn


## 👥 Team Xpert Mavericks

**Role Areas**
- Machine Learning Engineering  
- Document AI & NLP  
- Research Engineering  

**📫 Contact**  
- harikrishnan777h@gmail.com

**📄 License**  
- Apache 2.0

> *"We don’t just process documents — we connect knowledge across them."*  
> — The Xpert Mavericks Team
