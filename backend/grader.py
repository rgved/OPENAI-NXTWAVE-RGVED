# grader.py
import os
import re
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

# -------- Groq (TEXT) --------
from groq import Groq

# -------- Gemini (IMAGE) --------
import google.generativeai as genai

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# CLIENTS
# =========================

# Groq → TEXT ONLY
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

GROQ_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

# Gemini → IMAGE + TEXT
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# SHARED PROMPTS
# =========================
def build_grading_prompt(
    question,
    student_answer,
    correct_answer,
    max_score,
    difficulty
):
    return f"""
You are an expert academic exam evaluator.

Your goal is to grade fairly, consistently, and according to the specified difficulty level.

----------------------------------
GRADING RULES
----------------------------------

1. THEORY QUESTIONS
- If keywords or a correct answer are provided, check for conceptual correctness.
- Exact wording is NOT required. Synonyms, paraphrasing, and equivalent explanations are valid.
- Do NOT reduce marks simply because the answer could be more concise.
- Extra but correct details MUST NOT reduce the score.
- Award partial credit whenever understanding is demonstrated.

2. NUMERIC QUESTIONS
- Exact match required for integers.
- For decimal values, allow a tolerance of ±0.1.
- Correct method with a small arithmetic mistake deserves partial credit.

3. CHEMISTRY QUESTIONS
- Chemical symbols must be exact.
- Do NOT treat different symbols as partially correct (e.g., Au ≠ Ag, N ≠ Ne).

----------------------------------
DIFFICULTY ADJUSTMENT (VERY IMPORTANT)
----------------------------------

Apply grading strictness based on difficulty:

EASY:
- Be lenient.
- Focus on basic understanding.
- Minor conceptual gaps should NOT heavily reduce marks.
- If the core idea is correct, award at least 70–80% of max_score.

MEDIUM:
- Balance strictness and fairness.
- Expect correct concepts with reasonable explanation.
- Small mistakes should reduce marks slightly (≈0.5).
- Missing important points should reduce ≈1 mark per issue.

HARD:
- Be strict and analytical.
- Expect depth, precision, and completeness.
- Superficial or partially correct answers should lose significant marks.
- Minor errors still reduce marks, even if understanding is shown.

----------------------------------
SCORING RULES (MANDATORY)
----------------------------------

- Give a FINAL SCORE between 0 and {max_score}.
- Scores MUST be in decimal format (e.g., 2.5, 3.0, 4.5).
- For a very small, negligible mistake → reduce ≈0.5 marks.
- For each significant mistake → reduce ≈1.0 mark.
- Prefer partial credit over all-or-nothing scoring.

----------------------------------
FEEDBACK RULES
----------------------------------

- Always include BOTH: FINAL SCORE and FINAL FEEDBACK.
- If you give a score even 0.5 maks less than {max_score} justify why did you cut marks.
- Feedback must be 1–2 short, constructive sentences.
- Even for a perfect answer, give positive feedback such as:
  "Excellent answer, clearly explained and complete."

----------------------------------
RESPONSE FORMAT (STRICT)
----------------------------------

FINAL SCORE = <number out of {max_score}>
FINAL FEEDBACK = <1–2 sentences explaining the score>

----------------------------------
QUESTION
----------------------------------
{question}

----------------------------------
STUDENT ANSWER
----------------------------------
{student_answer}

----------------------------------
CORRECT ANSWER (REFERENCE)
----------------------------------
{correct_answer or "Not provided"}

----------------------------------
DIFFICULTY LEVEL
----------------------------------
{difficulty.upper()}
"""


# =========================
# TEXT GRADING (GROQ)
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

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a strict exam evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=900
    )

    text = response.choices[0].message.content.strip()
    return parse_grader_output(text, max_score)

# =========================
# IMAGE GRADING (GEMINI)
# =========================
def grade_from_image(
    image_bytes: bytes,
    max_score: int = 5,
    difficulty: str = "medium"
):
    image = Image.open(BytesIO(image_bytes))

    prompt = f"""
You are an expert academic exam evaluator.

The image contains a student's handwritten or printed exam answer.

Your tasks (VERY IMPORTANT):
1. Read the answer carefully from the image.
2. Infer the EXACT question being answered.
3. Rewrite the student's answer clearly in plain text.
4. Then evaluate the answer.

----------------------------------
MANDATORY OUTPUT FORMAT
----------------------------------

QUESTION:
<write the inferred question here — do NOT leave blank>

STUDENT ANSWER:
<rewrite the student's answer text here>

FINAL SCORE = <number out of {max_score}>
FINAL FEEDBACK = <1–2 sentences explaining the score>

Rules:
- NEVER skip QUESTION or STUDENT ANSWER.
- If the question is unclear, still infer the closest possible question.
- Do NOT combine lines.
- Each section MUST be present.

----------------------------------
DIFFICULTY LEVEL
----------------------------------
{difficulty.upper()}
"""

    response = gemini_model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 900
        }
    )

    raw = response.text.strip()

    # -----------------------------
    # EXTRACT QUESTION
    # -----------------------------
    q_match = re.search(
        r"QUESTION:\s*(.*?)\s*STUDENT ANSWER:",
        raw,
        re.DOTALL | re.IGNORECASE
    )

    question = (
        q_match.group(1).strip()
        if q_match
        else "Question could not be inferred from image"
    )

    # -----------------------------
    # EXTRACT STUDENT ANSWER
    # -----------------------------
    a_match = re.search(
        r"STUDENT ANSWER:\s*(.*?)\s*FINAL SCORE",
        raw,
        re.DOTALL | re.IGNORECASE
    )

    student_answer = (
        a_match.group(1).strip()
        if a_match
        else "Answer could not be inferred from image"
    )
    # -----------------------------
    # EXTRACT SCORE & FEEDBACK
    # -----------------------------
    graded = extract_score_and_feedback(raw, max_score)

    return {
        "question": question,
        "student_answer": student_answer,
        "score": graded["score"],
        "feedback": graded["feedback"]
    }

# =========================
# COMPANION MODE (TEXT → GROQ)
# =========================
def companion_feedback(
    question: str,
    student_answer: str,
    correct_answer: str = ""
):
    prompt = f"""
You are a helpful tutor. A student has answered a question, and you must guide them to a perfect answer.

Give feedback in the following format:

FEEDBACK:
<1–2 sentence explanation>

KEYWORDS:
- keyword 1
- keyword 2

IMPROVEMENT STEPS:
- step 1
- step 2

Instructions:
1. Summarize the student's answer and politely highlight what they did well.
2. List the essential keywords/points that a perfect answer should contain.
3. Give clear, constructive steps the student can follow to improve their answer.
4. Do NOT grade harshly here; focus on teaching.
5. Avoid scoring; this is only feedback and guidance.

Question:
{question}

Student Answer:
{student_answer}

Correct Answer:
{correct_answer or "Not provided"}
"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful tutor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=900
    )

    text = response.choices[0].message.content.strip()
    return parse_companion_text(text)

# =========================
# COMPANION FROM IMAGE (GEMINI)
# =========================
def companion_from_image(image_bytes: bytes):
    image = Image.open(BytesIO(image_bytes))

    prompt = """
You are a helpful tutor. A student has answered a question shown in the image.

Respond STRICTLY in the following format:

FEEDBACK:
<1–2 sentences explaining what the student did well and what can improve>

KEYWORDS:
- keyword 1
- keyword 2
- keyword 3

IMPROVEMENT STEPS:
- step 1
- step 2

Rules:
- Be polite and encouraging
- Do NOT assign a score
"""

    response = gemini_model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.4,
            "max_output_tokens": 900
        }
    )

    text = response.text.strip()

    return parse_companion_text(text)


# =========================
# PARSERS
# =========================
def parse_grader_output(text: str, max_score: int):
    score = 0
    feedback = "No feedback generated."

    score_match = re.search(
        r"final\s*score\s*=\s*(\d+(\.\d+)?)",
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

import re

def extract_score_and_feedback(raw: str, max_score: int):
    """
    Robustly extracts score and feedback even if they appear on the same line.
    """

    # ---------- SCORE ----------
    score_match = re.search(
        r"FINAL\s*SCORE\s*=\s*([0-9]+(?:\.[0-9]+)?)",
        raw,
        re.IGNORECASE
    )

    if score_match:
        score = float(score_match.group(1))
        score = max(0, min(score, max_score))  # clamp
    else:
        score = 0.0

    # ---------- FEEDBACK ----------
    feedback_match = re.search(
        r"FINAL\s*FEEDBACK\s*=\s*(.*)",
        raw,
        re.IGNORECASE | re.DOTALL
    )

    feedback = (
        feedback_match.group(1).strip()
        if feedback_match
        else "No feedback provided."
    )

    return {
        "score": score,
        "feedback": feedback
    }


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
