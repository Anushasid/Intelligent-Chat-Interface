import os
import re
import spacy
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ------------------ CONFIG ------------------
load_dotenv()  # Load from .env file
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("🚨 GROQ_API_KEY not found! Please create a .env file.")
    st.stop()

client = Groq(api_key=groq_api_key)
nlp = spacy.load("en_core_web_sm")
st.set_page_config(page_title="AI HR Assistant", layout="wide")

# ------------------ FUNCTIONS ------------------

# ----- PDF Parsing -----
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# ----- Resume Text Parsing -----
def get_profile_data_from_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    profile = {
        "name": "",
        "email": "",
        "phone": "",
        "objective": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "other_skills": [],
        "languages": {}
    }

    # Email and phone
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'\+?\d[\d\-\s]{8,}\d', text)
    profile["email"] = email.group(0) if email else ""
    profile["phone"] = phone.group(0) if phone else ""

    # Name (via SpaCy)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            profile["name"] = ent.text
            break

    # Section detection
    current_section = None
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in ["objective", "summary", "profile"]):
            current_section = "objective"
            profile["objective"] = ""
        elif "project" in lower:
            current_section = "projects"
        elif "skill" in lower:
            current_section = "skills"
        elif "education" in lower:
            current_section = "education"
        elif "experience" in lower:
            current_section = "experience"
        elif "certificat" in lower:
            current_section = "certifications"
        elif "achiev" in lower:
            current_section = "achievements"
        elif "language" in lower:
            current_section = "languages"
        elif "other skill" in lower:
            current_section = "other_skills"
        else:
            if current_section == "objective":
                profile["objective"] += " " + line
            elif current_section in profile and isinstance(profile[current_section], list):
                profile[current_section].append(line)

    return profile

# ----- LinkedIn Placeholder -----
def get_profile_data_from_linkedin(linkedin_url):
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+123456789",
        "objective": "To work as a software engineer.",
        "skills": ["Python", "AWS", "React"],
        "education": ["B.Tech in Computer Science"],
        "experience": ["3 years as Software Engineer"],
        "projects": ["AI automation tool for HR"],
        "certifications": ["AWS Certified Solutions Architect"],
        "achievements": ["Employee of the Month"],
        "other_skills": ["Time Management", "Teamwork"],
        "languages": {"English": "Professional Proficiency"}
    }

# ----- Chat with Groq -----
def generate_chatbot_response(user_input, profile):
    context = "\n".join([
        f"{k}: {', '.join(v) if isinstance(v, list) else v}"
        for k, v in profile.items()
    ])
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are an AI HR Assistant. Candidate details:\n{context}"},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

# ------------------ STREAMLIT UI ------------------

# Initialize session variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

candidate = None  # ✅ Initialize candidate to prevent NameError

st.sidebar.header("Upload / Fetch Candidate")
upload_option = st.sidebar.radio("Input method:", ["Upload Resume PDF", "LinkedIn URL"])

if upload_option == "Upload Resume PDF":
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        candidate = get_profile_data_from_text(text)
elif upload_option == "LinkedIn URL":
    linkedin_url = st.sidebar.text_input("LinkedIn Profile URL")
    if linkedin_url:
        candidate = get_profile_data_from_linkedin(linkedin_url)

# ------------------ MAIN CONTENT ------------------
st.title("🤖 AI HR Assistant")

if candidate:
    st.header(f"📄 Candidate: {candidate.get('name', 'Unknown')}")
    tabs = st.tabs([
        "Basic Info", "Skills", "Education", "Experience",
        "Certifications", "Achievements"
    ])

    with tabs[0]:
        st.write("**Objective:**", candidate.get("objective", ""))
        st.write("**Email:**", candidate.get("email", ""))
        st.write("**Phone:**", candidate.get("phone", ""))

    with tabs[1]:
        st.write(", ".join(candidate.get("skills", [])))

    with tabs[2]:
        st.write("\n".join(candidate.get("education", [])))

    with tabs[3]:
        st.write("\n".join(candidate.get("experience", [])))

    with tabs[4]:
        st.write("\n".join(candidate.get("certifications", [])))

    with tabs[5]:
        st.write("\n".join(candidate.get("achievements", [])))

    st.markdown("---")
    st.subheader("💬 Chat with AI Assistant")
    user_input = st.chat_input("Ask something about this candidate...")

    if user_input:
        reply = generate_chatbot_response(user_input, candidate)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", reply))

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)
else:
    st.info("Please upload a resume or enter a LinkedIn URL to continue.")
