import re
from PyPDF2 import PdfReader
import spacy
import openai
import os
from dotenv import load_dotenv

# ---------------- Load Environment and Setup ----------------
# Load API keys from .env file
load_dotenv()

# Set OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ---------------- PDF / Text Parsing ----------------
def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def get_profile_data_from_text(text):
    """Extracts structured data (name, email, etc.) from resume text."""
    doc = nlp(text)
    profile = {
        "name": "",
        "email": "",
        "phone": "",
        "objective": "",
        "skills": [],
        "education": [],
        "experience": [],
        "certifications": []
    }

    # Extract email and phone
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'\+?\d[\d\-\s]{8,}\d', text)
    profile["email"] = email.group(0) if email else ""
    profile["phone"] = phone.group(0) if phone else ""

    # Extract name (first PERSON entity)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            profile["name"] = ent.text
            break

    # Extract objective or summary
    obj_match = re.search(r'(Objective|Career Objective|Summary)(:|-)?\s*(.*)', text, re.I)
    profile["objective"] = obj_match.group(3).strip() if obj_match else ""

    # Extract skills
    skills_list = ["Python", "Java", "C++", "SQL", "AWS", "Docker", "React", "Node.js"]
    profile["skills"] = [s for s in skills_list if s.lower() in text.lower()]

    # Extract education
    profile["education"] = [
        line.strip() for line in text.split("\n")
        if any(edu in line for edu in ["B.Tech", "M.Tech", "MBA", "BE", "BSc"])
    ]

    # Extract experience
    profile["experience"] = [
        line.strip() for line in text.split("\n") if "experience" in line.lower()
    ]

    # Extract certifications
    profile["certifications"] = [
        line.strip() for line in text.split("\n")
        if "certification" in line.lower() or "certified" in line.lower()
    ]

    return profile

# ---------------- LinkedIn Placeholder ----------------
def get_profile_data_from_linkedin(linkedin_url):
    """Mock LinkedIn data (to be replaced with real scraping logic)."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+123456789",
        "objective": "To work as a software engineer.",
        "skills": ["Python", "AWS", "React"],
        "education": ["B.Tech in Computer Science"],
        "experience": ["3 years as Software Engineer"],
        "certifications": ["AWS Certified Solutions Architect"]
    }

# ---------------- Chatbot Interaction ----------------
def generate_chatbot_response(user_input, context=None):
    """Generates AI-based conversational replies using candidate context."""
    messages = []

    if context:
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        messages.append({"role": "system", "content": f"Candidate Profile:\n{context_str}"})

    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
