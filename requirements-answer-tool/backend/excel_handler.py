import pandas as pd
import io
from typing import List, Dict, Any, Optional
from pathlib import Path

class ExcelHandler:
    def __init__(self):
        self.question_keywords = ['question', 'requirement', 'query', 'q', 'ask', 'item', 'topic',
                                 'frage', 'anfrage', 'anforderung', 'punkt', 'thema']
        self.answer_keywords = ['answer', 'response', 'reply', 'a', 'solution', 'description',
                               'antwort', 'antworten', 'lösung', 'loesung', 'beschreibung']
    
    def extract_questions_from_excel(self, file_content: bytes, filename: str) -> List[str]:
        """Extract questions from uploaded Excel file"""
        try:
            # Read Excel file from bytes
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Find question column
            question_col = self._find_question_column(df)
            
            if question_col is None:
                # If no clear question column, try to extract from first column
                question_col = df.columns[0]
            
            # Extract questions
            questions = []
            for _, row in df.iterrows():
                question = str(row[question_col]).strip()
                if question and question != 'nan' and len(question) > 5:
                    questions.append(question)
            
            return questions
            
        except Exception as e:
            raise ValueError(f"Error processing Excel file {filename}: {str(e)}")
    
    def _find_question_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely question column in the DataFrame"""
        column_scores = {}
        
        for col in df.columns:
            col_lower = str(col).lower()
            score = 0
            
            # Check if column name contains question keywords
            for keyword in self.question_keywords:
                if keyword in col_lower:
                    score += 10
            
            # Check content of first few rows to see if they look like questions
            sample_rows = df[col].head(5).fillna('')
            for row_value in sample_rows:
                text = str(row_value).strip()
                if text and len(text) > 10:
                    # Check for question indicators
                    if text.endswith('?'):
                        score += 5
                    # English question words
                    if any(word in text.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who']):
                        score += 3
                    if any(word in text.lower() for word in ['can', 'will', 'should', 'would', 'could', 'do', 'does']):
                        score += 2
                    # German question words
                    if any(word in text.lower() for word in ['was', 'wie', 'warum', 'wann', 'wo', 'welche', 'wer']):
                        score += 3
                    if any(word in text.lower() for word in ['können', 'wird', 'sollte', 'würde', 'könnten', 'macht', 'machen']):
                        score += 2
            
            column_scores[col] = score
        
        # Return column with highest score, or None if no good match
        if column_scores:
            best_col = max(column_scores.keys(), key=lambda k: column_scores[k])
            return best_col if column_scores[best_col] > 0 else None
        
        return None
    
    def create_excel_template(self) -> bytes:
        """Create an Excel template for client questions (German)"""
        template_data = {
            'Frage': [
                'Welche Erfahrung haben Sie mit ähnlichen Projekten?',
                'Wie ist Ihr vorgeschlagener Zeitplan für dieses Projekt?',
                'Wie ist Ihre Preisstruktur?',
                'Welche Technologien werden Sie verwenden?',
                'Wie handhaben Sie Projektmanagement und Kommunikation?'
            ],
            'Priorität': ['Hoch', 'Hoch', 'Mittel', 'Mittel', 'Niedrig'],
            'Kategorie': ['Erfahrung', 'Zeitplan', 'Preise', 'Technisch', 'Prozess']
        }
        
        df = pd.DataFrame(template_data)
        
        # Save to bytes
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Kundenfragen')
        output.seek(0)
        
        return output.getvalue()
    
    def analyze_excel_structure(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Analyze the structure of an Excel file to understand its format"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            
            analysis = {
                'filename': filename,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'sample_data': {},
                'question_column_candidates': [],
                'answer_column_candidates': []
            }
            
            # Get sample data for each column
            for col in df.columns:
                sample_values = df[col].head(3).fillna('').astype(str).tolist()
                analysis['sample_data'][col] = sample_values
            
            # Find potential question and answer columns
            for col in df.columns:
                col_lower = str(col).lower()
                
                # Check for question column indicators
                if any(keyword in col_lower for keyword in self.question_keywords):
                    analysis['question_column_candidates'].append(col)
                
                # Check for answer column indicators
                if any(keyword in col_lower for keyword in self.answer_keywords):
                    analysis['answer_column_candidates'].append(col)
            
            return analysis
            
        except Exception as e:
            raise ValueError(f"Error analyzing Excel file {filename}: {str(e)}")
    
    def extract_qa_pairs_from_excel(self, file_content: bytes, filename: str, 
                                   question_col: str = None, answer_col: str = None) -> List[Dict[str, str]]:
        """Extract Q&A pairs from Excel file with specified columns"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Auto-detect columns if not specified
            if question_col is None:
                question_col = self._find_question_column(df)
                if question_col is None:
                    raise ValueError("Could not identify question column")
            
            if answer_col is None:
                answer_col = self._find_answer_column(df)
            
            qa_pairs = []
            
            for _, row in df.iterrows():
                question = str(row[question_col]).strip()
                answer = str(row[answer_col]).strip() if answer_col else ""
                
                if question and question != 'nan' and len(question) > 5:
                    qa_pair = {
                        'question': question,
                        'answer': answer if answer and answer != 'nan' else "",
                        'metadata': {
                            'source_file': filename,
                            'row_index': row.name
                        }
                    }
                    qa_pairs.append(qa_pair)
            
            return qa_pairs
            
        except Exception as e:
            raise ValueError(f"Error extracting Q&A pairs from {filename}: {str(e)}")
    
    def _find_answer_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely answer column in the DataFrame"""
        column_scores = {}
        
        for col in df.columns:
            col_lower = str(col).lower()
            score = 0
            
            # Check if column name contains answer keywords
            for keyword in self.answer_keywords:
                if keyword in col_lower:
                    score += 10
            
            # Check content length (answers are typically longer)
            sample_rows = df[col].head(5).fillna('')
            avg_length = sum(len(str(row)) for row in sample_rows) / len(sample_rows)
            if avg_length > 50:  # Answers tend to be longer
                score += 5
            
            column_scores[col] = score
        
        # Return column with highest score, or None if no good match
        if column_scores:
            best_col = max(column_scores.keys(), key=lambda k: column_scores[k])
            return best_col if column_scores[best_col] > 0 else None
        
        return None