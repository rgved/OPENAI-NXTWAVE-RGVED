# Xaminai – AI Grader + Student Companion

Xaminai is an AI-powered evaluation and learning assistant designed from **both an examiner’s and a student’s perspective**.  
It aims to modernize academic evaluation by saving time for faculty and giving students clarity and confidence in their answers.

---

## Real-World Use Case

**Best real-life use case:**  
Xaminai can be integrated into **University and College Portals**, allowing students and faculty to access AI-powered grading and feedback seamlessly within existing academic systems.

---

## Examiner / Faculty Perspective

In most universities, **exam papers are evaluated by teaching faculty themselves**, not by dedicated examiners. This leads to:

- Huge time consumption  
- Manual effort for repetitive grading  
- Less time for research, skill development, and teaching improvement  

### How Xaminai Helps Faculty

- Faculty can **upload answer scripts** (text, documents, images, or Drive files)
- Xaminai automatically grades answers based on:
  - Difficulty level
  - Correct answers / reference material
  - Academic evaluation rules
- Saves **hours of manual checking**
- Allows faculty to focus on **learning, research, and professional growth**

---

##  Student Perspective

Students often struggle with questions like:
- *Is my answer correct?*
- *Did I cover all important points?*
- *Is my answer framed properly?*
- *Why did I lose marks?*

### How Xaminai Helps Students

- Students can submit their answers
- Receive:
  - Clear feedback
  - Missing points
  - Keywords they should have included
  - Steps to improve
- Acts like a **personal tutor**, not just a grader

---

## Tech Stack

### Frontend
- **React.js**
- Clean UI for grading, companion mode, and dashboard

### Backend
- **FastAPI**
- REST-based architecture

### AI Models & APIs
- **Gemini 2.5 Flash** (for grading + vision-based evaluation)
- **LLaMA-4 Maverick 17B Instruct** (via **Groq API**) for companion/tutor mode

> We intentionally use **two different APIs** because our **future roadmap** involves shifting to a fully **local, fine-tuned LLM**, such as:
- GPT-OSS-20B
- LLaMA-4 Maverick Instruct  
(Instruct models are best suited for fine-tuning)

### Database
- **SQLite**
- Used to store grading history and power the dashboard

### Other Integrations
- **Google Drive API** (import answer scripts directly)
- **PDF / DOCX parsing**
- **Image-based evaluation using Gemini Vision**

---

## Key Features

---

## AI Grading Mode (Examiner-Focused)

### Input Flexibility
- Text input
- Upload files:
  - PDF
  - DOC / DOCX
  - TXT / JSON
- Import from **Google Drive** (saves local storage)
- Grade **handwritten or printed answers from images**

### Evaluation Settings
- Choose grading strictness:
  - Easy
  - Medium
  - Hard
- Provide correct answers / reference material  
  *(Very useful in university exams with fixed syllabi)*
- Set maximum marks per question or paper

### Output & Results
- Structured evaluation including:
  - Question
  - Student Answer
  - Correct Answer (optional)
  - Feedback
  - AI-generated score

### Enhanced Feedback
- Expandable sections with **detailed explanations**
- Clear reasoning behind mark deductions

### Export Options
- Download results as:
  - **PDF**
  - **DOC**
- Useful for record-keeping and sharing

---

## Companion Mode (Student-Focused)

### Input Flexibility
- Text input
- Upload:
  - PDF
  - DOC / DOCX
- Import from **Google Drive**

### Evaluation Settings
- Provide correct answers / reference material
- Set expected score level (optional guidance)

### Output & Learning-Oriented Feedback
Instead of grading harshly, Companion Mode focuses on learning:

- **Improvements**  
  What was missing or weak in the answer

- **Steps to Improve**  
  How the student can refine their response

- **Keywords to Consider**  
  Important terms and concepts to include

---

## Dashboard

- View **all previously graded answers**
- Filter by:
  - Mode (Text / File / Image / Drive)
  - Difficulty
- Export grading history as CSV
- Useful for:
  - Faculty analytics
  - Academic audits
  - Long-term performance tracking

---

## Future Scope


- **Fully Local Fine-Tuned LLM**
  - Reduced dependency on external APIs
  - Better privacy and lower cost

- **Mental Health & Well-being Features**
  - Support for students and faculty
  - Stress-aware academic assistance

- **Advanced Analytics Dashboard**
  - Performance trends
  - Common mistakes analysis
  - Course-wise insights for examiners

---

## Summary

Xaminai is not just an AI grader —  
it is a **time-saving academic assistant for faculty** and a **clarity-providing learning companion for students**, designed with real-world university workflows in mind.

---
