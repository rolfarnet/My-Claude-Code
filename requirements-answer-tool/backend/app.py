from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
from typing import List, Optional
from datetime import datetime
import shutil
import traceback

from models import QAPair, QuestionRequest, AnswerResponse, ExcelUploadResponse, ProcessedDocument
from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_system import RAGSystem
from excel_handler import ExcelHandler

app = FastAPI(
    title="Requirements Answer Tool",
    description="Automated tool for generating answers to client proposal questions using historical Q&A data",
    version="1.0.7"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
vector_store = VectorStore()
document_processor = DocumentProcessor()
rag_system = RAGSystem(vector_store)
excel_handler = ExcelHandler()

# Ensure directories exist
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Requirements Answer Tool API", "version": "1.0.7"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "qa_pairs_count": vector_store.count_qa_pairs()
    }

@app.post("/upload-historical-data")
async def upload_historical_data(files: List[UploadFile] = File(...)):
    """Upload and process historical Q&A documents"""
    results = []
    
    for file in files:
        try:
            # Save uploaded file
            file_path = f"data/uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process the file
            start_time = datetime.now()
            qa_pairs = document_processor.process_file(file_path)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if qa_pairs:
                # Add to vector store
                vector_store.add_qa_pairs(qa_pairs)
                
                results.append(ProcessedDocument(
                    file_name=file.filename,
                    qa_pairs_extracted=len(qa_pairs),
                    processing_time=processing_time,
                    status="success"
                ))
            else:
                results.append(ProcessedDocument(
                    file_name=file.filename,
                    qa_pairs_extracted=0,
                    processing_time=processing_time,
                    status="no_qa_pairs_found"
                ))
            
        except Exception as e:
            results.append(ProcessedDocument(
                file_name=file.filename,
                qa_pairs_extracted=0,
                processing_time=0.0,
                status=f"error: {str(e)}"
            ))
    
    return {"results": results}

@app.post("/upload-client-questions", response_model=ExcelUploadResponse)
async def upload_client_questions(file: UploadFile = File(...)):
    """Upload Excel file with client questions"""
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")
    
    try:
        file_content = await file.read()
        questions = excel_handler.extract_questions_from_excel(file_content, file.filename)
        
        return ExcelUploadResponse(
            questions=questions,
            total_questions=len(questions),
            file_name=file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@app.post("/generate-answer", response_model=AnswerResponse)
async def generate_answer(request: QuestionRequest):
    """Generate an answer for a single question"""
    
    try:
        answer_response = rag_system.generate_answer(
            question=request.question,
            context=request.context
        )
        return answer_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.post("/generate-answers", response_model=List[AnswerResponse])
async def generate_answers(questions: List[str]):
    """Generate answers for multiple questions"""
    
    try:
        answers = rag_system.batch_generate_answers(questions)
        return answers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answers: {str(e)}")

@app.post("/generate-answer-by-category", response_model=AnswerResponse)
async def generate_answer_by_category(
    question: str = Form(...),
    category: str = Form(...),
    context: Optional[str] = Form(None)
):
    """Generate an answer with category filtering"""
    
    try:
        answer_response = rag_system.get_answer_with_category_filter(
            question=question,
            category=category,
            context=context
        )
        return answer_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.get("/categories")
async def get_categories():
    """Get all available categories"""
    
    try:
        categories = vector_store.get_all_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@app.get("/qa-pairs/category/{category}")
async def get_qa_pairs_by_category(category: str, limit: int = 10):
    """Get Q&A pairs by category"""
    
    try:
        qa_pairs = vector_store.get_by_category(category, limit=limit)
        return {"qa_pairs": qa_pairs, "count": len(qa_pairs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Q&A pairs: {str(e)}")

@app.get("/search")
async def search_qa_pairs(query: str, limit: int = 10):
    """Search for similar Q&A pairs"""
    
    try:
        qa_pairs = vector_store.search_similar(query, n_results=limit)
        return {"qa_pairs": qa_pairs, "query": query, "count": len(qa_pairs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching Q&A pairs: {str(e)}")

@app.post("/suggest-improvements")
async def suggest_improvements(
    question: str = Form(...),
    current_answer: str = Form(...)
):
    """Suggest improvements to a manually written answer"""
    
    try:
        suggestions = rag_system.suggest_improvements(question, current_answer)
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    
    try:
        total_qa_pairs = vector_store.count_qa_pairs()
        categories = vector_store.get_all_categories()
        
        return {
            "total_qa_pairs": total_qa_pairs,
            "categories": categories,
            "category_count": len(categories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.delete("/clear-data")
async def clear_all_data():
    """Clear all Q&A data (use with caution)"""
    
    try:
        vector_store.delete_all()
        return {"message": "All Q&A data cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

@app.get("/download-template")
async def download_template():
    """Download Excel template for client questions"""
    
    try:
        template_content = excel_handler.create_excel_template()
        
        # Save template to file
        template_path = "data/client_questions_template.xlsx"
        with open(template_path, "wb") as f:
            f.write(template_content)
        
        return FileResponse(
            template_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="client_questions_template.xlsx"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

# Serve the frontend
@app.get("/app")
async def serve_frontend():
    return FileResponse("../frontend/index.html")

# Mount static files for frontend - must be last to avoid conflicts
app.mount("/", StaticFiles(directory="../frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)