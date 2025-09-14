import os
import re
import uuid
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import docx
from pypdf import PdfReader
from pathlib import Path

from models import QAPair

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.docx', '.pdf', '.txt']
    
    def process_file(self, file_path: str) -> List[QAPair]:
        """Process a single file and extract Q&A pairs"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.xlsx', '.xls']:
            return self._process_excel(file_path)
        elif file_ext == '.docx':
            return self._process_docx(file_path)
        elif file_ext == '.pdf':
            return self._process_pdf(file_path)
        elif file_ext == '.txt':
            return self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _process_excel(self, file_path: str) -> List[QAPair]:
        """Extract Q&A pairs from Excel files"""
        qa_pairs = []
        
        try:
            df = pd.read_excel(file_path)
            
            # Look for common column patterns (English and German)
            question_keywords = ['question', 'requirement', 'query', 'q', 'frage', 'anfrage', 'abfrage']
            answer_keywords = ['answer', 'response', 'reply', 'a', 'antwort', 'antworten', 'lösung', 'loesung']
            
            question_cols = [col for col in df.columns if any(keyword in col.lower() 
                           for keyword in question_keywords)]
            answer_cols = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in answer_keywords)]
            
            if question_cols and answer_cols:
                for _, row in df.iterrows():
                    question = str(row[question_cols[0]]).strip()
                    answer = str(row[answer_cols[0]]).strip()
                    
                    if question and answer and question != 'nan' and answer != 'nan':
                        qa_pair = QAPair(
                            question_id=str(uuid.uuid4()),
                            question_text=question,
                            answer_text=answer,
                            category=self._categorize_question(question),
                            client=Path(file_path).stem,
                            date=datetime.now(),
                            metadata={'source_file': file_path}
                        )
                        qa_pairs.append(qa_pair)
        
        except Exception as e:
            print(f"Error processing Excel file {file_path}: {e}")
        
        return qa_pairs
    
    def _process_docx(self, file_path: str) -> List[QAPair]:
        """Extract Q&A pairs from Word documents"""
        qa_pairs = []
        
        try:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            qa_pairs = self._extract_qa_from_text(text, file_path)
        
        except Exception as e:
            print(f"Error processing DOCX file {file_path}: {e}")
        
        return qa_pairs
    
    def _process_pdf(self, file_path: str) -> List[QAPair]:
        """Extract Q&A pairs from PDF files"""
        qa_pairs = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                qa_pairs = self._extract_qa_from_text(text, file_path)
        
        except Exception as e:
            print(f"Error processing PDF file {file_path}: {e}")
        
        return qa_pairs
    
    def _process_txt(self, file_path: str) -> List[QAPair]:
        """Extract Q&A pairs from text files"""
        qa_pairs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                qa_pairs = self._extract_qa_from_text(text, file_path)
        
        except Exception as e:
            print(f"Error processing TXT file {file_path}: {e}")
        
        return qa_pairs
    
    def _extract_qa_from_text(self, text: str, file_path: str) -> List[QAPair]:
        """Extract Q&A pairs from raw text using patterns"""
        qa_pairs = []
        
        # Common Q&A patterns
        patterns = [
            r'Q:?\s*(.*?)\s*A:?\s*(.*?)(?=Q:|$)',
            r'Question:?\s*(.*?)\s*Answer:?\s*(.*?)(?=Question:|$)',
            r'\d+\.\s*(.*?)\s*Answer:?\s*(.*?)(?=\d+\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            for question, answer in matches:
                question = question.strip()
                answer = answer.strip()
                
                if len(question) > 10 and len(answer) > 10:
                    qa_pair = QAPair(
                        question_id=str(uuid.uuid4()),
                        question_text=question,
                        answer_text=answer,
                        category=self._categorize_question(question),
                        client=Path(file_path).stem,
                        date=datetime.now(),
                        metadata={'source_file': file_path}
                    )
                    qa_pairs.append(qa_pair)
        
        return qa_pairs
    
    def _categorize_question(self, question: str) -> str:
        """Categorize questions based on content"""
        question_lower = question.lower()
        
        categories = {
            'technical': ['technical', 'architecture', 'database', 'api', 'integration', 'technology'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'compliance'],
            'pricing': ['cost', 'price', 'budget', 'payment', 'billing', 'license'],
            'timeline': ['timeline', 'schedule', 'delivery', 'deadline', 'when', 'how long'],
            'support': ['support', 'maintenance', 'training', 'documentation', 'help'],
            'legal': ['contract', 'terms', 'liability', 'warranty', 'legal', 'sla']
        }
        
        for category, keywords in categories.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def process_directory(self, directory_path: str) -> List[QAPair]:
        """Process all supported files in a directory"""
        all_qa_pairs = []
        
        for file_path in Path(directory_path).glob('**/*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    qa_pairs = self.process_file(str(file_path))
                    all_qa_pairs.extend(qa_pairs)
                    print(f"Processed {file_path}: {len(qa_pairs)} Q&A pairs extracted")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return all_qa_pairs