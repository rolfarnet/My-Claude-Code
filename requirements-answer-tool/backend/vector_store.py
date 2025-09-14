import chromadb
import uuid
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from models import QAPair

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="qa_pairs",
            metadata={"description": "Q&A pairs for requirements answer tool"}
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_qa_pairs(self, qa_pairs: List[QAPair]) -> None:
        """Add Q&A pairs to the vector store"""
        if not qa_pairs:
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for qa_pair in qa_pairs:
            # Combine question and answer for better semantic search
            combined_text = f"Question: {qa_pair.question_text}\nAnswer: {qa_pair.answer_text}"
            documents.append(combined_text)
            
            metadata = {
                "question_id": qa_pair.question_id,
                "question_text": qa_pair.question_text,
                "answer_text": qa_pair.answer_text,
                "category": qa_pair.category,
                "client": qa_pair.client or "",
                "project_type": qa_pair.project_type or "",
                "confidence_score": qa_pair.confidence_score
            }
            
            if qa_pair.date:
                metadata["date"] = qa_pair.date.isoformat()
            
            # Add custom metadata
            if qa_pair.metadata:
                for key, value in qa_pair.metadata.items():
                    metadata[f"meta_{key}"] = str(value)
            
            metadatas.append(metadata)
            ids.append(qa_pair.question_id)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(qa_pairs)} Q&A pairs to vector store")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[QAPair]:
        """Search for similar Q&A pairs with both vector and fuzzy matching"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['metadatas', 'documents', 'distances']
        )
        
        qa_pairs = []
        
        if results['metadatas'] and results['metadatas'][0]:
            for metadata, document, distance in zip(
                results['metadatas'][0], 
                results['documents'][0], 
                results['distances'][0]
            ):
                # Calculate confidence score based on distance (vector similarity)
                confidence_score = max(0, 1 - distance)
                
                # Calculate fuzzy matching score against question text
                fuzzy_score = fuzz.ratio(query, metadata['question_text']) / 100.0
                
                qa_pair = QAPair(
                    question_id=metadata['question_id'],
                    question_text=metadata['question_text'],
                    answer_text=metadata['answer_text'],
                    category=metadata['category'],
                    client=metadata.get('client'),
                    project_type=metadata.get('project_type'),
                    confidence_score=confidence_score,
                    fuzzy_score=fuzzy_score
                )
                
                qa_pairs.append(qa_pair)
        
        return qa_pairs
    
    def get_by_category(self, category: str, limit: int = 10) -> List[QAPair]:
        """Get Q&A pairs by category"""
        results = self.collection.get(
            where={"category": category},
            limit=limit,
            include=['metadatas']
        )
        
        qa_pairs = []
        
        if results['metadatas']:
            for metadata in results['metadatas']:
                qa_pair = QAPair(
                    question_id=metadata['question_id'],
                    question_text=metadata['question_text'],
                    answer_text=metadata['answer_text'],
                    category=metadata['category'],
                    client=metadata.get('client'),
                    project_type=metadata.get('project_type'),
                    confidence_score=metadata.get('confidence_score', 0.0)
                )
                qa_pairs.append(qa_pair)
        
        return qa_pairs
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        # This is a workaround since ChromaDB doesn't have a direct way to get unique values
        results = self.collection.get(include=['metadatas'])
        categories = set()
        
        if results['metadatas']:
            for metadata in results['metadatas']:
                categories.add(metadata['category'])
        
        return sorted(list(categories))
    
    def count_qa_pairs(self) -> int:
        """Get total count of Q&A pairs"""
        return self.collection.count()
    
    def delete_all(self) -> None:
        """Delete all Q&A pairs (use with caution)"""
        self.client.delete_collection("qa_pairs")
        self.collection = self.client.get_or_create_collection(
            name="qa_pairs",
            metadata={"description": "Q&A pairs for requirements answer tool"}
        )
        print("All Q&A pairs deleted from vector store")
    
    def update_qa_pair(self, qa_pair: QAPair) -> None:
        """Update an existing Q&A pair"""
        # Delete existing
        try:
            self.collection.delete(ids=[qa_pair.question_id])
        except:
            pass
        
        # Add updated version
        self.add_qa_pairs([qa_pair])