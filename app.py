import streamlit as st
import PyPDF2
import docx
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get AI-powered insights based on a job description.")

# ---------- SIDEBAR ----------
st.sidebar.header("How it works")
st.sidebar.write("""
1. Upload your resume in PDF or DOCX format.    
2. Paste the job description.
3. Click Analyze to get your score, matched skills, and AI suggestions.
4. Download your report.
""")
st.sidebar.markdown("---")
st.sidebar.caption("Made with Streamlit + Gemini AI")


# ---------- FUNCTION: EXTRACT TEXT FROM PDF ----------
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


# ---------- FUNCTION: EXTRACT TEXT FROM DOCX ----------
def extract_text_from_docx(file):
    text = ""
    doc = docx.Document(file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.strip()


# ---------- FUNCTION: DECIDE WHICH EXTRACTOR TO USE ----------
def extract_resume_text(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        return extract_text_from_docx(uploaded_file)
    else:
        return None


# ---------- FUNCTION: ANALYZE WITH GEMINI ----------
def analyze_resume(resume_text, job_description, api_key):

    prompt = f"""
You are an expert resume reviewer and career coach.

Compare the following RESUME with the JOB DESCRIPTION and analyze the match.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY in valid JSON format (no extra text, no markdown, no ```json fences), with exactly this structure:

{{
  "score": <a number between 0 and 100 representing overall match>,
  "matched_skills": [<list of skills present in both resume and job description>],
  "missing_skills": [<list of important skills in job description but missing from resume>],
  "suggestions": [<list of 3-5 specific, actionable suggestions to improve the resume for this job>]
}}
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    raw_text = response.text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    result = json.loads(raw_text)
    return result


# ---------- FUNCTION: BUILD DOWNLOADABLE REPORT ----------
def build_report_text(result, resume_name):
    report = f"""AI RESUME ANALYZER - REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Resume File: {resume_name}

========================================
OVERALL MATCH SCORE: {result['score']} / 100
========================================

MATCHED SKILLS:
"""
    for skill in result['matched_skills']:
        report += f"  - {skill}\n"

    report += "\nMISSING SKILLS:\n"
    for skill in result['missing_skills']:
        report += f"  - {skill}\n"

    report += "\nAI SUGGESTIONS FOR IMPROVEMENT:\n"
    for i, suggestion in enumerate(result['suggestions'], start=1):
        report += f"  {i}. {suggestion}\n"

    return report


# ---------- TWO COLUMNS: UPLOAD + JOB DESCRIPTION ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload your Resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

with col2:
    st.subheader("Job Description")
    job_description = st.text_area("Paste the job description here...", height=200)

st.markdown("---")

# ---------- ANALYZE BUTTON ----------
analyze_clicked = st.button("Analyze Resume", type="primary")

if analyze_clicked:

    if not uploaded_file:
        st.warning("Pehle apna resume upload karein.")
    elif not job_description.strip():
        st.warning("Job description likhein.")
    elif not api_key:
        st.error("API key nahi mili. .env file check karein.")
    else:
        with st.spinner("Extracting resume text..."):
            resume_text = extract_resume_text(uploaded_file)

        if not resume_text:
            st.error("Resume se text extract nahi ho saka. File corrupt ho sakti hai ya scanned image PDF ho sakti hai (jisme text select nahi hota).")
        elif len(resume_text) < 50:
            st.error("Resume mein bahut kam text mila. Please ek valid resume file upload karein.")
        else:
            with st.spinner("Analyzing with AI... yeh thoda time le sakta hai"):
                try:
                    result = analyze_resume(resume_text, job_description, api_key)

                    # Basic validation of AI response structure
                    required_keys = {"score", "matched_skills", "missing_skills", "suggestions"}
                    if not required_keys.issubset(result.keys()):
                        st.error("AI se response format mein masla aaya. Dobara try karein.")
                    else:
                        st.session_state.analysis_result = result
                        st.session_state.resume_name = uploaded_file.name

                except json.JSONDecodeError:
                    st.error("AI ka response process nahi ho saka. Dobara 'Analyze Resume' pe click karein.")
                except Exception as e:
                    st.error(f"Kuch ghalat hua: {e}")


# ---------- RESULTS SECTION ----------
if "analysis_result" in st.session_state:
    result = st.session_state.analysis_result

    st.markdown("---")
    st.subheader("Analysis Results")

    score = result['score']

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Resume Match Score", f"{score} / 100")
    with r2:
        st.progress(score / 100)
        if score >= 75:
            st.success("Great match! 🎉")
        elif score >= 50:
            st.warning("Decent match, thodi improvement ki gunjaish hai.")
        else:
            st.error("Match kam hai, resume ko improve karna zaroori hai.")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("✅ Matched Skills", expanded=True):
            if result['matched_skills']:
                for skill in result['matched_skills']:
                    st.write(f"- {skill}")
            else:
                st.write("Koi matched skill nahi mili.")

    with c2:
        with st.expander("❌ Missing Skills", expanded=True):
            if result['missing_skills']:
                for skill in result['missing_skills']:
                    st.write(f"- {skill}")
            else:
                st.write("Koi missing skill nahi mili — bahut acha!")

    with st.expander("💡 AI Suggestions", expanded=True):
        for suggestion in result['suggestions']:
            st.write(f"- {suggestion}")

    st.markdown("---")

    # ---------- DOWNLOAD REPORT ----------
    report_text = build_report_text(result, st.session_state.resume_name)

    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )