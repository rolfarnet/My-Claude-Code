# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This repository contains two distinct projects:

### 1. Interactive Particle Visualization
- `interactive_visualization/interactive_visualization.html` - Self-contained HTML5 canvas particle system

### 2. Course Materials RAG System
- `starting-ragchatbot-codebase-main/` - Full-stack RAG (Retrieval-Augmented Generation) application
- **Backend**: FastAPI server with ChromaDB vector store and Anthropic Claude integration
- **Frontend**: Vanilla JavaScript web interface for querying course materials

## Running the Projects

### Interactive Visualization
```bash
start interactive_visualization/interactive_visualization.html
```

### RAG System
Prerequisites: Python 3.13+, uv package manager, Anthropic API key

```bash
cd starting-ragchatbot-codebase-main
# Install dependencies
uv sync

# Set environment variable
# Create .env file with: ANTHROPIC_API_KEY=your_key_here

# Start the application
./run.sh
# Or manually: cd backend && uv run uvicorn app:app --reload --port 8000
```

Access at: http://localhost:8000

## RAG System Architecture

The RAG system follows a layered architecture with clear separation of concerns:

### Core Components
- **RAGSystem** (`backend/rag_system.py`): Main orchestrator coordinating all components
- **VectorStore** (`backend/vector_store.py`): ChromaDB interface for semantic search
- **AIGenerator** (`backend/ai_generator.py`): Anthropic Claude API integration with tool use
- **DocumentProcessor** (`backend/document_processor.py`): Course content chunking and processing
- **SessionManager** (`backend/session_manager.py`): Conversation history management
- **ToolManager** (`backend/search_tools.py`): Tool-based search capabilities

### API Layer
- **FastAPI App** (`backend/app.py`): REST API endpoints with CORS and middleware
- **Models** (`backend/models.py`): Pydantic schemas for requests/responses
- **Frontend**: Static files served by FastAPI (`frontend/`)

### Data Flow
1. User query → Frontend → FastAPI endpoint
2. Session management and history retrieval
3. AI Generator processes query with optional tool use
4. Vector search retrieves relevant course chunks
5. Claude generates contextual response
6. Sources and response returned to frontend

### Key Features
- **Tool-Enhanced AI**: Claude can search course content using function calling
- **Session Continuity**: Conversation history maintained across queries
- **Source Attribution**: Transparent citations for all responses
- **Semantic Search**: Vector similarity matching for course content retrieval

## Dependencies
- **Python**: chromadb, anthropic, sentence-transformers, fastapi, uvicorn
- **Vector Store**: ChromaDB with sentence transformers embeddings
- **AI**: Anthropic Claude with function calling capabilities

## Development Notes
- **Package Management**: Always use `uv` to manage ALL dependencies - never use `pip` directly
- **Installing Packages**: Use `uv add package_name` to add new dependencies
- **Running Commands**: Use `uv run command` for all Python execution
- **Server Commands**: Use `uv run uvicorn app:app --reload --port 8000` instead of direct uvicorn calls