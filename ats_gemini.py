import streamlit as st
from google import genai

from dotenv import load_dotenv
import os
import PyPDF2 as pdf
import json
import re
import ast

# Load environment variables
load_dotenv()
api_key = os.getenv("Google_Api_key")
client = genai.Client(api_key=api_key)

# Extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += str(reader.pages[page].extract_text())
    return text

# Function to clean and parse JSON safely
def safe_json_parse(raw_text):
    # Remove markdown formatting
    clean_text = raw_text.strip().replace("```", "").replace("json", "").strip()
    # Fix common JSON issues (single quotes, trailing commas, \n inside)
    clean_text = re.sub(r"[\n\r\t]", " ", clean_text)
    clean_text = clean_text.replace("'", '"')
    try:
        return json.loads(clean_text)
    except:
        try:
            return ast.literal_eval(clean_text)
        except:
            # return None, clean_text
            return ast.literal_eval(clean_text)

# Prompt Template
input_prompt = """
You are an **Applicant Tracking System (ATS)** specialized ONLY in evaluating 
resumes for **Data Science** and **Data Analyst** roles.  

Your task is to evaluate the given resume against the provided Job Description (JD).  

### Rules for Response:
1. Response must be in **pure JSON format** only (no markdown, no explanations, no code blocks).
2. Follow this JSON schema strictly:
{
  "JD Match": "78%",
  "MissingKeywords": ["Python", "SQL"],
  "Profile Summary": "Candidate has strong Python skills but lacks SQL expertise."
}
3. JD Match should be based on **keywords overlap**.
4. MissingKeywords must include only job-relevant missing skills.
5. Profile Summary must be 4-5 line and professional.
"""

# Smart Suggestions Prompt
suggestions_prompt = """
You are a recruitment assistant.  
Based on the candidate's resume and the given job description, suggest **3-4 specific improvements** 
that can make the resume stronger for this role.  

Response Rules:
- Write only bullet points.
- Keep it concise and practical.
- Avoid extra explanations.
"""

# Streamlit UI
st.set_page_config(page_title="Smart ATS - Data Science Edition", layout="wide")
st.title(" Smart ATS - Data Science & Analyst Edition")
st.caption(" Upload your resume & get ATS-based evaluation")

jd = st.text_area(" Paste the Job Description", height=200)
uploaded_file = st.file_uploader(" Upload Resume (PDF)", type="pdf")

submit = st.button(" Submit for Analysis")

if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner(" Analyzing Resume..."):
            try:
                text = input_pdf_text(uploaded_file)
                prompt = input_prompt + f"\n### Resume:\n{text}\n\n### Job Description:\n{jd}"

                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                
                raw_text = response.text

                result = safe_json_parse(raw_text)

                if result and isinstance(result, dict):
                    
                    # Strength Meter
                    jd_match = result.get("JD Match", "0%").replace("%", "")
                    try:
                        score = int(jd_match)
                    except:
                        score = 0

                    if score > 85:
                        strength = "💪 Excellent Fit"
                    elif score > 70:
                        strength = "👍 Good Fit"
                    elif score > 50:
                        strength = "🤔 Average Fit"
                    else:
                        strength = "❌ Poor Fit"

                    st.subheader(" Resume Strength Meter")
                    st.success(f"{strength} ({jd_match}%)")

                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(" JD Match", f"{jd_match}%")
                    with col2:
                        st.metric(" Missing Keywords", len(result.get("MissingKeywords", [])))

                    with st.expander(" Missing Keywords"):
                        st.write(", ".join(result.get("MissingKeywords", [])))
                        
                    with st.expander(" Profile Summary"):
                        st.write(result.get("Profile Summary", ""))    
                        
                    # Smart Suggestions Panel
                    with st.expander("💡 Smart Resume Suggestions"):
                        sug_prompt = suggestions_prompt + f"\n\nResume:\n{text}\n\nJob Description:\n{jd}"
                        sug_response = client.models.generate_content(model="gemini-2.5-flash", contents=sug_prompt)
                        st.write(sug_response.text)
                        
                else:
                    st.error("❌ Model did not return valid JSON.")
                    st.write(raw_text)

            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning(" Please upload a resume and paste a job description.")
