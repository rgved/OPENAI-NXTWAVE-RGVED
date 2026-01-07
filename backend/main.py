# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from grader import grade_answer, companion_feedback
import docx
import fitz
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import numpy as np




app = FastAPI(title="Xaminai Backend")

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Schemas
# ---------------------------
class GradeRequest(BaseModel):
    question: str
    student_answer: str
    correct_answer: str | None = None
    max_score: int = 5
    difficulty: str = "medium"


class CompanionRequest(BaseModel):
    question: str
    student_answer: str
    correct_answer: str | None = None
    max_score: int = 5


# ---------------------------
# Routes
# ---------------------------
@app.post("/grade")
def grade(req: GradeRequest):
    return grade_answer(
        question=req.question,
        student_answer=req.student_answer,
        correct_answer=req.correct_answer or "",
        max_score=req.max_score,
        difficulty=req.difficulty
    )
@app.post("/grade/file")
async def grade_file(
    file: UploadFile = File(...),
    max_score: int = 5,
    difficulty: str = "medium"
):
    raw = await file.read()
    filename = file.filename.lower()

    extracted_text = ""

    try:
        # -------- PDF --------
        if filename.endswith(".pdf"):
            pdf = fitz.open(stream=raw, filetype="pdf")
            extracted_text = "\n".join(page.get_text() for page in pdf)

        # -------- DOCX --------
        elif filename.endswith(".docx"):
            doc = docx.Document(BytesIO(raw))
            extracted_text = "\n".join(
                p.text.strip() for p in doc.paragraphs if p.text.strip()
            )

        # -------- TXT --------
        elif filename.endswith(".txt"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        # -------- JSON --------
        elif filename.endswith(".json"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        else:
            return {
                "score": 0,
                "feedback": f"Unsupported file type: {file.filename}"
            }

    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Failed to read file: {str(e)}"
        }

    if not extracted_text.strip():
        return {
            "score": 0,
            "feedback": "No readable text found in the file."
        }

    # 🔥 REAL GEMINI GRADING
    return grade_answer(
        question="Answer extracted from uploaded file",
        student_answer=extracted_text,
        correct_answer="",
        max_score=max_score,
        difficulty=difficulty
    )


@app.post("/companion")
def companion(req: CompanionRequest):
    return companion_feedback(
        question=req.question,
        student_answer=req.student_answer,
        correct_answer=req.correct_answer or ""
        # max_score=req.max_score
    )

@app.post("/companion/file")
async def companion_file(file: UploadFile = File(...)):
    raw = await file.read()
    filename = file.filename.lower()

    extracted_text = ""

    try:
        # -------- DOCX --------
        if filename.endswith(".docx"):
            doc = docx.Document(BytesIO(raw))
            extracted_text = "\n".join(
                p.text.strip() for p in doc.paragraphs if p.text.strip()
            )

        # -------- PDF --------
        elif filename.endswith(".pdf"):
            pdf = fitz.open(stream=raw, filetype="pdf")
            extracted_text = "\n".join(
                page.get_text().strip() for page in pdf if page.get_text().strip()
            )

        # -------- TXT --------
        elif filename.endswith(".txt"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        # -------- JSON --------
        elif filename.endswith(".json"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        else:
            return {
                "feedback": f"Unsupported file type: {file.filename}",
                "keywords": [],
                "improvement_steps": []
            }

    except Exception as e:
        return {
            "feedback": f"Failed to read file: {str(e)}",
            "keywords": [],
            "improvement_steps": []
        }

    if not extracted_text.strip():
        return {
            "feedback": "No readable text found in the file.",
            "keywords": [],
            "improvement_steps": []
        }

    # 🔥 REAL GEMINI CALL
    return companion_feedback(
        question="Answer extracted from uploaded file",
        student_answer=extracted_text,
        correct_answer=""
    )

# ---------------------------
# GOOGLE DRIVE SETUP
# ---------------------------
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "service_account.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)

def download_drive_file(file_id: str):
    """
    Downloads a file from Google Drive and returns (filename, bytes)
    """
    file_meta = drive_service.files().get(
        fileId=file_id, fields="name, mimeType"
    ).execute()

    filename = file_meta["name"]
    mime_type = file_meta["mimeType"]

    buffer = BytesIO()

    # Google Docs → export as PDF
    if mime_type.startswith("application/vnd.google-apps"):
        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType="application/pdf"
        )
    else:
        request = drive_service.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    return filename, buffer.read()

from fastapi import Query
from grader import grade_answer


@app.post("/grade/drive")
def grade_from_drive(
    file_id: str = Query(...),
    max_score: int = 5,
    difficulty: str = "medium"
):
    filename, raw = download_drive_file(file_id)
    name = filename.lower()

    extracted_text = ""

    try:
        if name.endswith(".pdf"):
            import fitz
            doc = fitz.open(stream=raw, filetype="pdf")
            extracted_text = "\n".join(page.get_text() for page in doc)

        elif name.endswith(".docx"):
            import docx
            d = docx.Document(BytesIO(raw))
            extracted_text = "\n".join(p.text for p in d.paragraphs)

        elif name.endswith(".txt"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        elif name.endswith(".json"):
            extracted_text = raw.decode("utf-8", errors="ignore")

        else:
            return {
                "score": 0,
                "feedback": f"Unsupported file type: {filename}"
            }

    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Failed to read file: {str(e)}"
        }

    if not extracted_text.strip():
        return {
            "score": 0,
            "feedback": "No readable text found in Drive file."
        }

    # 🔥 Send to Gemini grader
    return grade_answer(
        question="Answer extracted from Google Drive file",
        student_answer=extracted_text,
        correct_answer="",
        max_score=max_score,
        difficulty=difficulty
    )

from fastapi import UploadFile, File
from grader import grade_from_image


@app.post("/grade/image")
async def grade_image(
    file: UploadFile = File(...),
    max_score: int = 5,
    difficulty: str = "medium"
):
    image_bytes = await file.read()

    return grade_from_image(
        image_bytes=image_bytes,
        max_score=max_score,
        difficulty=difficulty
    )

from fastapi import UploadFile, File
from grader import companion_from_image

@app.post("/companion/image")
async def companion_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    return companion_from_image(image_bytes)



from fastapi import UploadFile, File
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import BytesIO
import docx
import json
import fitz  # PyMuPDF

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "service_account.json"


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


@app.post("/companion/drive")
def companion_from_drive(file_id: str):
    service = get_drive_service()

    file_meta = service.files().get(
        fileId=file_id,
        fields="name, mimeType"
    ).execute()

    name = file_meta["name"].lower()
    mime = file_meta["mimeType"]

    request = (
        service.files().export_media(fileId=file_id, mimeType="application/pdf")
        if mime.startswith("application/vnd.google-apps")
        else service.files().get_media(fileId=file_id)
    )

    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    text = ""

    try:
        # ---------- PDF ----------
        if name.endswith(".pdf"):
            doc = fitz.open(stream=fh.read(), filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)

        # ---------- DOCX ----------
        elif name.endswith(".docx"):
            doc = docx.Document(fh)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        # ---------- TXT / JSON ----------
        elif name.endswith(".txt") or name.endswith(".json"):
            text = fh.read().decode("utf-8", errors="ignore")

        else:
            return {
                "feedback": "Unsupported file type from Drive",
                "keywords": [],
                "improvement_steps": []
            }

    except Exception as e:
        return {
            "feedback": f"Failed to read Drive file: {str(e)}",
            "keywords": [],
            "improvement_steps": []
        }

    if not text.strip():
        return {
            "feedback": "No readable text found in Drive file",
            "keywords": [],
            "improvement_steps": []
        }

    return companion_feedback(
        question="Answer extracted from Google Drive file",
        student_answer=text,
        correct_answer=""
    )
