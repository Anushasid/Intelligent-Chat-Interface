
import re
import spacy
import openai
from PyPDF2 import PdfReader
import streamlit as st

# ------------------ CONFIG ------------------
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI HR Assistant", layout="wide")

nlp = spacy.load("en_core_web_sm")

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

    # Extract email and phone
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'\+?\d[\d\-\s]{8,}\d', text)
    profile["email"] = email.group(0) if email else ""
    profile["phone"] = phone.group(0) if phone else ""

    # Extract name using SpaCy
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            profile["name"] = ent.text
            break

    # Extract sections by headers
    current_section = None
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ["objective", "summary", "profile"]):
            current_section = "objective"
            profile["objective"] = ""
        elif "project" in line_lower:
            current_section = "projects"
        elif "skill" in line_lower:
            current_section = "skills"
        elif "education" in line_lower:
            current_section = "education"
        elif "experience" in line_lower:
            current_section = "experience"
        elif "certificat" in line_lower:
            current_section = "certifications"
        elif "achiev" in line_lower:
            current_section = "achievements"
        elif "other skill" in line_lower:
            current_section = "other_skills"
        elif "language" in line_lower:
            current_section = "languages"
        else:
            # Append line to the right section
            if current_section == "objective":
                profile["objective"] += " " + line
            elif current_section == "skills":
                profile["skills"].append(line)
            elif current_section == "education":
                profile["education"].append(line)
            elif current_section == "experience":
                profile["experience"].append(line)
            elif current_section == "projects":
                profile["projects"].append(line)
            elif current_section == "certifications":
                profile["certifications"].append(line)
            elif current_section == "achievements":
                profile["achievements"].append(line)
            elif current_section == "other_skills":
                profile["other_skills"].append(line)
            elif current_section == "languages":
                parts = line.split()
                if len(parts) >= 2:
                    lang = parts[0]
                    prof = " ".join(parts[1:])
                    profile["languages"][lang] = prof

    # Remove duplicates and empty lines
    for key in ["skills", "education", "experience", "projects", "certifications", "achievements", "other_skills"]:
        profile[key] = [x for x in profile[key] if x]

    return profile

# ----- LinkedIn Placeholder -----
def get_profile_data_from_linkedin(linkedin_url):
    # Placeholder for real LinkedIn scraping
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+123456789",
        "objective": "To work as a software engineer.",
        "skills": ["Python","AWS","React"],
        "education": ["B.Tech in Computer Science"],
        "experience": ["3 years as Software Engineer"],
        "projects": ["Project X: AI automation tool"],
        "certifications": ["AWS Certified Solutions Architect"],
        "achievements": ["Employee of the Month"],
        "other_skills": ["Time Management", "Teamwork"],
        "languages": {"English":"Full Professional"}
    }

# ----- OpenAI Chat -----
def generate_chatbot_response(user_input, candidate_profile):
    context_str = "\n".join([
        f"{k}: {', '.join(v) if isinstance(v,list) else v}" 
        for k,v in candidate_profile.items()
    ])
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are an HR assistant. Candidate info:\n{context_str}"},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# ------------------ SESSION STATE ------------------
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_candidate" not in st.session_state:
    st.session_state.current_candidate = None

if "temp_profile" not in st.session_state:
    st.session_state.temp_profile = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ SIDEBAR ------------------
st.sidebar.header("Upload / Fetch Candidate Profile")
upload_option = st.sidebar.radio("Choose input method:", ["Upload Resume PDF", "LinkedIn URL"])

if upload_option == "Upload Resume PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        profile = get_profile_data_from_text(text)
        st.session_state.temp_profile = profile
        st.session_state.current_candidate = profile.get("name","Unknown Candidate")
        st.session_state.chats[st.session_state.current_candidate] = profile

elif upload_option == "LinkedIn URL":
    linkedin_url = st.sidebar.text_input("Enter LinkedIn Profile URL")
    if linkedin_url:
        profile = get_profile_data_from_linkedin(linkedin_url)
        st.session_state.temp_profile = profile
        st.session_state.current_candidate = profile.get("name","Unknown Candidate")
        st.session_state.chats[st.session_state.current_candidate] = profile

# ------------------ MAIN APP ------------------
st.title("🤖 AI HR Assistant")

if st.session_state.current_candidate:
    candidate = st.session_state.chats.get(
        st.session_state.current_candidate,
        st.session_state.temp_profile
    )

    st.header(f"📄 Candidate Profile: {candidate.get('name','N/A')}")
    tabs = st.tabs([
        "Basic Info", "Projects", "Skills", "Education", 
        "Experience", "Certifications", "Achievements", 
        "Languages", "Other Skills"
    ])

    with tabs[0]:
        st.write(candidate.get("objective",""))
        st.write("Email:", candidate.get("email",""))
        st.write("Phone:", candidate.get("phone",""))

    with tabs[1]:
        st.write("\n".join(candidate.get("projects",[])))

    with tabs[2]:
        st.write(", ".join(candidate.get("skills",[])))

    with tabs[3]:
        st.write("\n".join(candidate.get("education",[])))

    with tabs[4]:
        st.write("\n".join(candidate.get("experience",[])))

    with tabs[5]:
        st.write("\n".join(candidate.get("certifications",[])))

    with tabs[6]:
        st.write("\n".join(candidate.get("achievements",[])))

    with tabs[7]:
        for lang, prof in candidate.get("languages",{}).items():
            st.write(f"{lang}: {prof}")

    with tabs[8]:
        st.write("\n".join(candidate.get("other_skills",[])))

    st.markdown("---")
    st.header("💬 Chat with AI Assistant")
    user_input = st.chat_input("Ask something about the candidate...")
    if user_input:
        response = generate_chatbot_response(user_input, candidate)
        st.session_state.chat_history.append({"user": user_input, "ai": response})

    for chat in st.session_state.chat_history:
        st.chat_message("user").write(chat["user"])
        st.chat_message("assistant").write(chat["ai"])

else:
    st.info("Please upload a resume or enter LinkedIn URL to get started.")
