# grader.py
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# =========================
# SAFE JSON EXTRACTOR
# =========================
def safe_json_extract(text: str, fallback: dict):
    """
    Safely extract the largest JSON object from Gemini output.
    """
    try:
        matches = re.findall(r"\{[\s\S]*?\}", text)
        if not matches:
            return fallback

        block = max(matches, key=len)

        # Auto-fix unbalanced braces
        open_braces = block.count("{")
        close_braces = block.count("}")
        if open_braces > close_braces:
            block += "}" * (open_braces - close_braces)

        return json.loads(block)

    except Exception:
        return fallback

def parse_companion_text(text: str):
    sections = {
        "feedback": "",
        "keywords": [],
        "improvement_steps": []
    }

    current = None
    for line in text.splitlines():
        line = line.strip()

        if line.upper().startswith("FEEDBACK"):
            current = "feedback"
            continue
        elif line.upper().startswith("KEYWORDS"):
            current = "keywords"
            continue
        elif line.upper().startswith("IMPROVEMENT"):
            current = "improvement_steps"
            continue

        if not line:
            continue

        if current == "feedback":
            sections["feedback"] += line + " "
        elif current == "keywords" and line.startswith("-"):
            sections["keywords"].append(line[1:].strip())
        elif current == "improvement_steps" and line.startswith("-"):
            sections["improvement_steps"].append(line[1:].strip())

    sections["feedback"] = sections["feedback"].strip()

    return sections

def parse_grader_output(text: str, max_score: int):
    score = 0.0
    feedback = "No feedback generated."

    score_match = re.search(
        r"final\s*score\s*=\s*(\d+(?:\.\d+)?)",
        text,
        re.I
    )
    if score_match:
        score = float(score_match.group(1))

    feedback_match = re.search(
        r"final\s*feedback\s*=\s*(.+)",
        text,
        re.I
    )
    if feedback_match:
        feedback = feedback_match.group(1).strip()

    return {
        "score": min(score, max_score),
        "feedback": feedback
    }


# =========================
# PROMPT BUILDER
# =========================
def build_grading_prompt(
    question,
    student_answer,
    correct_answer,
    max_score,
    difficulty
):
    return f"""
You are an exam evaluator.

You MUST respond in EXACTLY this format.
You MUST fill in ALL fields with meaningful content.
DO NOT leave anything blank.

FORMAT (follow strictly):

FINAL SCORE = <number out of {max_score}>
FINAL FEEDBACK = <at least 1 full sentence explaining the score>

EXAMPLE RESPONSE:
FINAL SCORE = 4
FINAL FEEDBACK = The answer is mostly correct but misses a clear definition.

Now evaluate:

Question:
{question}

Student Answer:
{student_answer}

Correct Answer:
{correct_answer if correct_answer else "Not provided"}

Grading strictness: {difficulty}
"""


# =========================
# EXAM GRADER
# =========================
def grade_answer(
    question: str,
    student_answer: str,
    correct_answer: str = "",
    max_score: int = 5,
    difficulty: str = "medium"
):
    prompt = build_grading_prompt(
        question,
        student_answer,
        correct_answer,
        max_score,
        difficulty
    )

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 900
        }
    )

    raw_text = response.text.strip()

    print("\n===== GEMINI RAW OUTPUT =====")
    print(raw_text)
    print("===== END OUTPUT =====\n")

    return parse_grader_output(raw_text, max_score)

# grader.py
import google.generativeai as genai
from PIL import Image
from io import BytesIO

def grade_from_image(
    image_bytes: bytes,
    max_score: int = 5,
    difficulty: str = "medium"
):
    from PIL import Image
    from io import BytesIO
    import re

    image = Image.open(BytesIO(image_bytes))

    prompt = f"""
You are a professional exam grader.

The image contains a student's handwritten or printed answer.

TASK:
1. Read and understand the answer from the image
2. Grade it fairly
3. Give short feedback

Respond in natural language.
Clearly mention the final score out of {max_score}.
Difficulty: {difficulty}
"""

    response = model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 300
        }
    )

    raw_text = response.text.strip()

    print("\n===== GEMINI RAW OUTPUT =====")
    print(raw_text)
    print("===== END OUTPUT =====\n")

    # -----------------------------
    # 🔎 SMART SCORE EXTRACTION
    # -----------------------------
    score = 0

    score_match = re.search(
        rf"(\d+(\.\d+)?)\s*/\s*{max_score}", raw_text
    ) or re.search(
        r"score\s*[:\-]?\s*(\d+(\.\d+)?)", raw_text, re.IGNORECASE
    )

    if score_match:
        score = float(score_match.group(1))

    score = max(0, min(score, max_score))

    # -----------------------------
    # 📝 FEEDBACK EXTRACTION
    # -----------------------------
    feedback = raw_text

    # Remove score line from feedback if present
    feedback = re.sub(r"score.*", "", feedback, flags=re.IGNORECASE).strip()

    if not feedback:
        feedback = "Feedback could not be generated."

    return {
        "score": score,
        "feedback": feedback
    }



# =========================
# COMPANION MODE
# =========================
def companion_feedback(question, student_answer, correct_answer=""):
    prompt = f"""
You are a helpful tutor.

Give feedback in the following format:

FEEDBACK:
<1–2 sentence explanation>

KEYWORDS:
- keyword 1
- keyword 2
- keyword n


IMPROVEMENT STEPS:
- step 1
- step 2
- step n

Rules:
- Always include all three sections
- Even if the answer is perfect,say that its almost perfect and suggest refinement
- Be concise and clear

Question:
{question}

Student Answer:
{student_answer}

Correct Answer:
{correct_answer if correct_answer else "Not provided"}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 900
        }
    )

    text = response.text.strip()

    # ---------------------------
    # Manual parsing (RELIABLE)
    # ---------------------------
    feedback = ""
    keywords = []
    steps = []

    try:
        if "FEEDBACK:" in text:
            feedback = text.split("FEEDBACK:")[1].split("KEYWORDS:")[0].strip()

        if "KEYWORDS:" in text:
            kw_block = text.split("KEYWORDS:")[1].split("IMPROVEMENT STEPS:")[0]
            keywords = [
                k.strip("- ").strip()
                for k in kw_block.splitlines()
                if k.strip()
            ]

        if "IMPROVEMENT STEPS:" in text:
            steps = [
                s.strip("- ").strip()
                for s in text.split("IMPROVEMENT STEPS:")[1].splitlines()
                if s.strip()
            ]

    except Exception:
        pass

    return {
        "feedback": feedback or "Feedback generated but could not be parsed cleanly.",
        "keywords": keywords,
        "improvement_steps": steps
    }

def companion_from_image(
    image_bytes: bytes
):
    from PIL import Image
    from io import BytesIO
    import re

    image = Image.open(BytesIO(image_bytes))

    prompt = """
You are a friendly AI tutor.

The image contains a student's handwritten or printed answer.

TASK:
1. Read the answer from the image
2. Explain briefly what the student did well
3. Explain briefly how the student can improve
4. Mention important keywords naturally inside the explanation

STRICT RULES:
- Do NOT use headings
- Do NOT use bullet points
- Do NOT use *, **, #, -, or emojis
- Write in plain text only
- Use 2 to 3 short paragraphs
- Be concise and encouraging

Respond in natural language only.
"""


    response = model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.4,
            "max_output_tokens": 400
        }
    )

    raw_text = response.text.strip()

    print("\n===== GEMINI RAW COMPANION OUTPUT =====")
    print(raw_text)
    print("===== END OUTPUT =====\n")

    # -----------------------------
    # 🧠 HEURISTIC EXTRACTION
    # -----------------------------
    keywords = []
    steps = []

    # Keywords (best effort)
    kw_match = re.search(r"keywords?\s*[:\-]\s*(.*)", raw_text, re.IGNORECASE)
    if kw_match:
        keywords = [k.strip() for k in kw_match.group(1).split(",") if k.strip()]

    # Steps (bullet points or numbered)
    steps = re.findall(r"(?:\d+\.|\-)\s*(.+)", raw_text)

    return {
        "feedback": raw_text,
        "keywords": keywords,
        "improvement_steps": steps
    }



def grade_from_image(
    image_bytes: bytes,
    max_score: int = 5,
    difficulty: str = "medium"
):
    from PIL import Image
    from io import BytesIO
    import re

    image = Image.open(BytesIO(image_bytes))

    prompt = f"""
You are a professional exam grader.

The image contains a student's handwritten or printed answer.

TASK:
1. Read and understand the answer from the image
2. Grade it fairly
3. Give short feedback

Respond in natural language.
Clearly mention the final score out of {max_score}.
Difficulty: {difficulty}
"""

    response = model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 900
        }
    )

    raw_text = response.text.strip()

    print("\n===== GEMINI RAW OUTPUT =====")
    print(raw_text)
    print("===== END OUTPUT =====\n")

    # -----------------------------
    # 🔎 SMART SCORE EXTRACTION
    # -----------------------------
    score = 0

    score_match = re.search(
        rf"(\d+(\.\d+)?)\s*/\s*{max_score}", raw_text
    ) or re.search(
        r"score\s*[:\-]?\s*(\d+(\.\d+)?)", raw_text, re.IGNORECASE
    )

    if score_match:
        score = float(score_match.group(1))

    score = max(0, min(score, max_score))

    # -----------------------------
    # 📝 FEEDBACK EXTRACTION
    # -----------------------------
    

    feedback = raw_text

    # Remove score line from feedback if present
    feedback = re.sub(r"score.*", "", feedback, flags=re.IGNORECASE).strip()

    if not feedback:
        feedback = "Feedback could not be generated."

    return {
        "score": score,
        "feedback": feedback
    }
