from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class GradingHistory(Base):
    __tablename__ = "grading_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    student_answer = Column(Text)
    score = Column(Float)
    max_score = Column(Integer)
    difficulty = Column(String)
    mode = Column(String)  # text | file | image | drive
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
