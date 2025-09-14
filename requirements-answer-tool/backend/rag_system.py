import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import anthropic
from dotenv import load_dotenv

from models import QAPair, AnswerResponse
from vector_store import VectorStore

load_dotenv()

class RAGSystem:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def generate_answer(self, question: str, context: Optional[str] = None, 
                       num_sources: int = 5) -> AnswerResponse:
        """Generate an answer for a given question using RAG"""
        
        # Search for similar Q&A pairs
        similar_qa_pairs = self.vector_store.search_similar(question, n_results=num_sources)
        
        if not similar_qa_pairs:
            return AnswerResponse(
                answer="I don't have enough historical data to answer this question confidently. Please provide more context or add this to your Q&A knowledge base.",
                confidence_score=0.0,
                fuzzy_score=0.0,
                sources=[],
                generated_at=datetime.now()
            )
        
        # Build the prompt with context and sources
        prompt = self._build_prompt(question, similar_qa_pairs, context)
        
        try:
            # Generate answer using Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            generated_answer = response.content[0].text
            
            # Calculate overall scores based on source similarities
            avg_confidence = sum(qa.confidence_score for qa in similar_qa_pairs) / len(similar_qa_pairs)
            avg_fuzzy_score = sum(qa.fuzzy_score for qa in similar_qa_pairs) / len(similar_qa_pairs)
            
            return AnswerResponse(
                answer=generated_answer,
                confidence_score=avg_confidence,
                fuzzy_score=avg_fuzzy_score,
                sources=similar_qa_pairs,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            return AnswerResponse(
                answer=f"Error generating answer: {str(e)}",
                confidence_score=0.0,
                fuzzy_score=0.0,
                sources=similar_qa_pairs,
                generated_at=datetime.now()
            )
    
    def _build_prompt(self, question: str, sources: List[QAPair], context: Optional[str]) -> str:
        """Build the German prompt for Claude with question and context"""
        
        prompt = f"""Sie sind ein Experte für Ausschreibungen und helfen dabei, Kundenfragen basierend auf historischen Q&A-Daten zu beantworten.

Aktuelle Frage: {question}

"""
        
        if context:
            prompt += f"Zusätzlicher Kontext: {context}\n\n"
        
        prompt += "Historische Q&A-Beispiele (als Referenz für Konsistenz verwenden):\n\n"
        
        for i, qa_pair in enumerate(sources, 1):
            prompt += f"Beispiel {i} (Vector distance metric: {qa_pair.confidence_score:.2f}):\n"
            prompt += f"Frage: {qa_pair.question_text}\n"
            prompt += f"Antwort: {qa_pair.answer_text}\n"
            if qa_pair.client:
                prompt += f"Kunde: {qa_pair.client}\n"
            if qa_pair.project_type:
                prompt += f"Projekttyp: {qa_pair.project_type}\n"
            prompt += "\n"
        
        prompt += """Anweisungen:
1. Erstellen Sie eine umfassende Antwort, die die aktuelle Frage beantwortet
2. Nutzen Sie die historischen Beispiele als Referenz für Ton, Stil und Detailgrad
3. Bewahren Sie Konsistenz mit vorherigen Antworten bei gleichzeitiger Anpassung an die spezifische Frage
4. Falls die Frage sehr ähnlich zu einem historischen Beispiel ist, passen Sie diese Antwort entsprechend an
5. Falls die Frage anders aber verwandt ist, synthetisieren Sie Informationen aus mehreren Beispielen
6. Seien Sie professionell, detailliert und kundenorientiert
7. Beziehen Sie spezifische Details und Beispiele mit ein, wo relevant
8. Falls Sie keine vertrauensvolle Antwort basierend auf den verfügbaren Beispielen geben können, sagen Sie dies klar

Generieren Sie eine professionelle Antwort:"""
        
        return prompt
    
    def batch_generate_answers(self, questions: List[str], context: Optional[str] = None) -> List[AnswerResponse]:
        """Generate answers for multiple questions"""
        answers = []
        
        for question in questions:
            answer = self.generate_answer(question, context)
            answers.append(answer)
        
        return answers
    
    def get_answer_with_category_filter(self, question: str, category: str, 
                                      context: Optional[str] = None) -> AnswerResponse:
        """Generate answer focusing on a specific category"""
        # Get category-specific sources
        category_qa_pairs = self.vector_store.get_by_category(category, limit=3)
        
        # Also get general similar questions
        similar_qa_pairs = self.vector_store.search_similar(question, n_results=3)
        
        # Combine and deduplicate sources
        all_sources = category_qa_pairs + similar_qa_pairs
        seen_ids = set()
        unique_sources = []
        
        for qa in all_sources:
            if qa.question_id not in seen_ids:
                unique_sources.append(qa)
                seen_ids.add(qa.question_id)
        
        if not unique_sources:
            return AnswerResponse(
                answer=f"I don't have enough historical data in the '{category}' category to answer this question confidently.",
                confidence_score=0.0,
                sources=[],
                generated_at=datetime.now()
            )
        
        # Build prompt with category focus
        prompt = self._build_category_prompt(question, unique_sources, category, context)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            generated_answer = response.content[0].text
            
            # Calculate confidence score
            avg_confidence = sum(qa.confidence_score for qa in unique_sources) / len(unique_sources)
            
            return AnswerResponse(
                answer=generated_answer,
                confidence_score=avg_confidence,
                sources=unique_sources,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            return AnswerResponse(
                answer=f"Error generating answer: {str(e)}",
                confidence_score=0.0,
                sources=unique_sources,
                generated_at=datetime.now()
            )
    
    def _build_category_prompt(self, question: str, sources: List[QAPair], 
                              category: str, context: Optional[str]) -> str:
        """Build a category-focused prompt"""
        
        prompt = f"""You are an expert proposal writer specializing in {category} questions. Answer the client question based on historical {category}-related Q&A data.

Current Question: {question}
Category Focus: {category}

"""
        
        if context:
            prompt += f"Additional Context: {context}\n\n"
        
        prompt += f"Historical {category} Q&A Examples:\n\n"
        
        for i, qa_pair in enumerate(sources, 1):
            prompt += f"Example {i} (Category: {qa_pair.category}, Confidence: {qa_pair.confidence_score:.2f}):\n"
            prompt += f"Question: {qa_pair.question_text}\n"
            prompt += f"Answer: {qa_pair.answer_text}\n"
            if qa_pair.client:
                prompt += f"Client: {qa_pair.client}\n"
            prompt += "\n"
        
        prompt += f"""Instructions:
1. Focus specifically on the {category} aspects of the question
2. Use the historical {category} examples as your primary reference
3. Maintain consistency with previous {category} answers
4. Be detailed and specific to {category} concerns
5. Include relevant technical details, processes, or methodologies for {category}

Generate a professional {category}-focused answer:"""
        
        return prompt
    
    def suggest_improvements(self, question: str, current_answer: str) -> str:
        """Suggest improvements to a manually written answer"""
        similar_qa_pairs = self.vector_store.search_similar(question, n_results=3)
        
        if not similar_qa_pairs:
            return "No similar examples found for comparison."
        
        prompt = f"""Compare the current answer with historical examples and suggest improvements.

Question: {question}

Current Answer:
{current_answer}

Historical Examples:
"""
        
        for i, qa_pair in enumerate(similar_qa_pairs, 1):
            prompt += f"\nExample {i}:\nQ: {qa_pair.question_text}\nA: {qa_pair.answer_text}\n"
        
        prompt += "\nAnalyze the current answer and provide specific suggestions for improvement based on the historical examples. Focus on tone, completeness, structure, and alignment with previous responses."
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating suggestions: {str(e)}"