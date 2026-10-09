# 🎯 SkillSync AI — By Farise aml — Smart Resume Gap Analyzer

**AI-powered resume analysis tool that identifies skill gaps against target job roles and generates personalized learning paths using RAG (Retrieval-Augmented Generation).**

---

## ✨ Features

- 📄 **Resume Parsing**: Extracts text from PDF, DOCX, and TXT files
- 🧠 **AI Skill Extraction**: Identifies 60+ technical and soft skills from resume text
- 🔍 **RAG-Powered Matching**: Compares your skills against curated job role requirements
- 📊 **Gap Analysis**: Visual dashboard showing missing, partial, and present skills
- 🎓 **Learning Path**: Curated course recommendations with time estimates
- 📈 **Match Score**: Gauge chart showing readiness level for target role
- 📥 **Export**: Downloadable Markdown and JSON reports

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd skillsync-ai
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

### 3. Use
- Upload your resume (PDF/DOCX/TXT)
- Select a target role (Software Engineer, Data Scientist, etc.)
- Click **Analyze My Resume**
- View your skill gaps and personalized learning path

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Resume     │────▶│  Resume Parser  │────▶│ Skill Extractor │
│  (PDF/DOCX) │     │  (PyMuPDF)      │     │ (Keyword + NLP) │
└─────────────┘     └─────────────────┘     └─────────────────┘
                                                      │
                              ┌───────────────────────┘
                              ▼
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Course DB  │◀────│  Gap Analyzer   │◀────│   RAG Engine    │
│ (courses)   │     │  (Scoring +     │     │ (Vector Store + │
└─────────────┘     │   Recommend)    │     │  Retrieval)     │
                    └─────────────────┘     └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Streamlit UI    │
                    │ (Charts +       │
                    │  Dashboard)     │
                    └─────────────────┘
```

---

## 📁 Project Structure

```
skillsync-ai/
├── app.py                 # Main Streamlit application
├── resume_parser.py       # PDF/DOCX/TXT text extraction
├── skill_extractor.py     # Skill detection from text
├── rag_engine.py          # Vector store and retrieval
├── gap_analyzer.py        # Gap analysis and recommendations
├── requirements.txt       # Python dependencies
├── data/
│   ├── job_roles.json     # 5 job role skill frameworks
│   └── courses.json       # 95 curated learning resources
└── README.md
```

---

## 🎯 Workshop Presentation Tips

1. **Hook**: "73% of resumes are rejected before a human sees them — usually due to missing keywords."
2. **Demo**: Upload a sample resume and show the gap analysis in real-time
3. **RAG Explanation**: "We vectorized 75 job requirements and retrieve the most relevant ones for comparison"
4. **Impact**: "This turns a 2-hour manual resume review into a 10-second AI analysis"
5. **Future**: "Next: LinkedIn integration, real-time job posting matching, and interview question generation"

---

## 🛠️ Customization

**Add a new job role**: Edit `data/job_roles.json` and add a new role with required skills.

**Add courses**: Edit `data/courses.json` — the system matches courses to skills automatically.

**Use real embeddings**: Replace `SimpleEmbedding` in `rag_engine.py` with OpenAI, Cohere, or sentence-transformers embeddings.

---

## 📜 License

Built by **Farise aml** for workshop presentation.

MIT License — Free for workshop and educational use.
