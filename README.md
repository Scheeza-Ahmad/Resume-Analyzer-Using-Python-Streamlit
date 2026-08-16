# 📄 AI Resume Analyzer

An AI-powered web app that analyzes resumes against job descriptions and provides a match score, skills comparison, and actionable improvement suggestions — built with Streamlit and Google Gemini AI.

## Features

- **Resume Upload** — Supports PDF and DOCX formats
- **Job Description Input** — Paste any job description for comparison
- **Skills Matching** — Automatically identifies matched and missing skills
- **Resume Score** — AI-generated match score out of 100
- **AI Suggestions** — Specific, actionable tips to improve your resume
- **Downloadable Report** — Export the full analysis as a text file

## Tech Stack

- **Python**
- **Streamlit** — frontend/UI framework
- **Google Gemini API** (`google-genai`) — AI analysis
- **PyPDF2** — PDF text extraction
- **python-docx** — DOCX text extraction
- **python-dotenv** — environment variable management

## Project Structure

```
resume-analyzer/
│
├── ai_resume_analyzer.py      # Main application file
├── requirements.txt           # Python dependencies
├── .env                       # API key (not tracked by Git)
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd resume-analyzer
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the app
```bash
streamlit run ai_resume_analyzer.py
```

The app will open in your browser at `http://localhost:8501`.

## How It Works

1. Upload your resume (PDF or DOCX)
2. Paste the job description you're targeting
3. Click **Analyze Resume**
4. The app extracts text from your resume and sends it, along with the job description, to Gemini AI
5. AI returns a structured analysis: match score, matched skills, missing skills, and improvement suggestions
6. Download the full report as a text file

## Notes

- Scanned/image-based PDFs (no selectable text) are not supported for text extraction.
- Requires an active internet connection to reach the Gemini API.
