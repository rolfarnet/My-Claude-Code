from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QAPair(BaseModel):
    question_id: str
    question_text: str
    category: str
    answer_text: str
    client: Optional[str] = None
    date: Optional[datetime] = None
    project_type: Optional[str] = None
    confidence_score: float = 0.0
    fuzzy_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = {}

class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None

class AnswerResponse(BaseModel):
    answer: str
    confidence_score: float
    fuzzy_score: float
    sources: List[QAPair]
    generated_at: datetime

class ExcelUploadResponse(BaseModel):
    questions: List[str]
    total_questions: int
    file_name: str

class ProcessedDocument(BaseModel):
    file_name: str
    qa_pairs_extracted: int
    processing_time: float
    status: str