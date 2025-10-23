import os
import re
import spacy
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ------------------ CONFIG ------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("🚨 GROQ_API_KEY not found! Please create a .env file with your key.")
    st.stop()

client = Groq(api_key=groq_api_key)
nlp = spacy.load("en_core_web_sm")
st.set_page_config(page_title="AI HR Assistant", layout="wide")

# ------------------ FUNCTIONS ------------------

def extract_text_from_pdf(file):
    """Extracts text from uploaded PDF."""
    reader = PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])


def get_profile_data_from_text(text):
    """Extract structured candidate data from resume text."""
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
        "languages": []
    }

    # Basic info
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'\+?\d[\d\-\s]{8,}\d', text)
    profile["email"] = email.group(0) if email else ""
    profile["phone"] = phone.group(0) if phone else ""

    # Name extraction using NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            profile["name"] = ent.text
            break

    # Section parsing
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
        else:
            if current_section == "objective":
                profile["objective"] += " " + line
            elif current_section in profile and isinstance(profile[current_section], list):
                profile[current_section].append(line)

    return profile


def get_profile_data_from_linkedin(linkedin_url):
    """Mock LinkedIn data extraction (can be extended)."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "objective": "To contribute as a Software Engineer and grow with the organization.",
        "skills": ["Python", "React", "AWS", "Node.js"],
        "education": ["B.Tech in Computer Science - XYZ University"],
        "experience": ["Software Engineer at ABC Corp (3 years)"],
        "projects": ["AI-Powered Resume Screening System"],
        "certifications": ["AWS Certified Solutions Architect"],
        "achievements": ["Employee of the Month - ABC Corp"],
        "languages": ["English", "Hindi"]
    }


def generate_chatbot_response(user_input, profile, chat_history):
    """AI HR Chatbot response generator."""
    context = "\n".join([
        f"{k}: {', '.join(v) if isinstance(v, list) else v}"
        for k, v in profile.items()
        if v
    ])

    messages = [{"role": "system", "content": f"You are an AI HR Assistant. Candidate details:\n{context}"}]
    for role, msg in chat_history:
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ Correct, active Groq model
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


# ------------------ STREAMLIT APP ------------------

st.title("🤖 AI HR Assistant")
st.caption("An intelligent chat-based interface for resume parsing and HR interactions.")

st.sidebar.header("📂 Candidate Source")
upload_option = st.sidebar.radio("Choose input method:", ["Upload Resume PDF", "LinkedIn URL"])

candidate = None

if upload_option == "Upload Resume PDF":
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded_file:
        with st.spinner("Extracting information from resume..."):
            text = extract_text_from_pdf(uploaded_file)
            candidate = get_profile_data_from_text(text)

elif upload_option == "LinkedIn URL":
    linkedin_url = st.sidebar.text_input("Enter LinkedIn Profile URL")
    if linkedin_url:
        with st.spinner("Fetching data from LinkedIn..."):
            candidate = get_profile_data_from_linkedin(linkedin_url)

if candidate:
    st.header(f"📄 Candidate: {candidate.get('name', 'Unknown')}")
    tabs = st.tabs([
        "Basic Info", "Skills", "Education", "Experience",
        "Projects", "Certifications", "Achievements", "Languages"
    ])

    with tabs[0]:
        st.write("**Objective:**", candidate.get("objective", ""))
        st.write("**Email:**", candidate.get("email", ""))
        st.write("**Phone:**", candidate.get("phone", ""))

    with tabs[1]:
        st.write(", ".join(candidate.get("skills", [])) or "N/A")

    with tabs[2]:
        st.write("\n".join(candidate.get("education", [])) or "N/A")

    with tabs[3]:
        st.write("\n".join(candidate.get("experience", [])) or "N/A")

    with tabs[4]:
        st.write("\n".join(candidate.get("projects", [])) or "N/A")

    with tabs[5]:
        st.write("\n".join(candidate.get("certifications", [])) or "N/A")

    with tabs[6]:
        st.write("\n".join(candidate.get("achievements", [])) or "N/A")

    with tabs[7]:
        st.write(", ".join(candidate.get("languages", [])) or "N/A")

    st.markdown("---")
    st.subheader("💬 Interactive HR Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

    user_input = st.chat_input("Ask something about this candidate...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            reply = generate_chatbot_response(user_input, candidate, st.session_state.chat_history)

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", reply))
else:
    st.info("📁 Please upload a resume or enter a LinkedIn URL to begin.")
