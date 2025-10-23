# 🤖 Agentic AI HR Assistant

## 🧠 Overview

**Agentic AI HR Assistant** is an intelligent AI-powered recruitment tool that helps HR professionals **analyze resumes, extract candidate data, and interact through a chatbot** for quick evaluation and decision-making.
The system uses **Natural Language Processing (NLP)** to parse resumes, extract structured candidate information, and enable an interactive **AI chat** interface that can answer queries about each candidate.

This project demonstrates **how AI and automation can simplify hiring** — making resume analysis faster, smarter, and more efficient.

---

## 🚀 Key Features

### 📄 Smart Resume Parsing (PDF)

Automatically extracts candidate information such as:

* Name, Email, and Phone number
* Career Objective / Summary
* Skills and Technical Expertise
* Education Background
* Work Experience
* Projects, Certifications, and Achievements

### 💬 Interactive AI Chatbot

* Chat with the AI assistant about the candidate’s profile
* Ask questions like *“What are this candidate’s strengths?”* or *“Does this profile fit a software developer role?”*
* Uses **Groq LLM (Llama 3.x)** for intelligent and contextual responses

### 🌐 Simple and Interactive Web Interface

* Built using **Streamlit** for fast and smooth deployment
* Minimal UI with sidebar input and tab-based candidate details
* Works instantly in the browser without any backend setup

---

## 🧩 Workflow

1. **Upload Resume (PDF)** → The user uploads a candidate’s resume.
2. **Text Extraction (`PyPDF2`)** → Text is extracted page by page.
3. **Information Parsing (`spaCy + Regex`)** →

   * Detects personal info like name, email, phone
   * Identifies sections (skills, education, experience, etc.)
4. **Data Structuring** → Extracted content is organized into a dictionary (profile).
5. **Chat with AI** → The structured candidate data is sent to the **Groq Llama model**, allowing HR to ask contextual questions.
6. **Display Output** → Candidate details are shown neatly in tabs, and chatbot responses appear in real-time.

---

## 🛠️ Tech Stack

| Technology                 | Purpose                      | Why It’s Used                                         |
| -------------------------- | ---------------------------- | ----------------------------------------------------- |
| 🐍 **Python 3.9+**         | Core programming language    | Easy to integrate AI, NLP, and web frameworks         |
| 🎨 **Streamlit**           | Web framework for UI         | Enables interactive and quick app deployment          |
| 📄 **PyPDF2**              | PDF parsing library          | Extracts text content from uploaded resumes           |
| 🧠 **spaCy**               | NLP processing               | Detects names and entities from resume text           |
| ⚙️ **Regex (re)**          | Pattern extraction           | Identifies email, phone, and structured text sections |
| ⚡ **Groq API (Llama 3.x)** | AI model backend             | Provides fast, context-aware chatbot responses        |
| 🔑 **python-dotenv**       | Environment variable manager | Keeps API keys secure and separate from code          |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Anushasid/Intelligent-Chat-Interface.git
cd Intelligent-Chat-Interface
```

### 2️⃣ Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3️⃣ Add Your API Key

Create a `.env` file in the project root:

```bash
GROQ_API_KEY="your_groq_api_key_here"
```

### 4️⃣ Run the Application

```bash
streamlit run app.py
```

---

## 🖼️ User Interface Overview

| Upload Resume                               | Parsed Profile                              | AI Chat Assistant                           |
| ------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| ![Screenshot1](screenshots/Screenshot1.png) | ![Screenshot2](screenshots/Screenshot2.png) | ![Screenshot3](screenshots/Screenshot3.png) |

---

## 🌟 Advantages

✅ **Completely Automated Resume Parsing** — No manual data entry
✅ **Contextual AI Chat** — HR can interactively ask questions
✅ **Simple Setup** — Just upload and analyze
✅ **Fast Processing** — Uses lightweight NLP + LLM for instant output
✅ **User-Friendly Interface** — Easy for HR professionals to operate

---

## 🔮 Future Enhancements

* Integration with **LinkedIn API** for live profile fetching
* **Job-fit analysis** comparing candidate skills with job descriptions
* Support for **DOCX and image-based resumes (OCR)**
* Export structured data as **JSON or CSV reports**
* Add **voice-based interaction** for HR convenience

---

## 👩‍💻 Project Structure

```
Agentic_AI_HR_ASSISTANT/
│
├── app.py                # Streamlit app (UI + Chatbot)
├── data_extractor.py     # Resume parsing and NLP logic
├── requirements.txt      # Dependencies
├── .env                  # API key (not shared in GitHub)
├── screenshots/          # Screenshots of the app
└── README.md             # Project documentation
```

---

## 💡 Developer

🌐 GitHub: [Anushasid](https://github.com/Anushasid)
