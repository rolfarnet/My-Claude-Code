# Requirements Answer Tool

An AI-powered application that automatically generates answers to client proposal questions using historical Q&A data and RAG (Retrieval-Augmented Generation) technology.

## Features

- **Historical Data Processing**: Import and process Q&A data from Excel, Word, PDF, and text files
- **Excel Question Import**: Upload client questions from Excel files with automatic question detection
- **AI-Powered Answers**: Generate contextual answers using Claude AI and similar historical examples
- **Vector Search**: Semantic similarity matching to find relevant historical Q&A pairs
- **Category Filtering**: Organize and filter questions by categories (technical, pricing, timeline, etc.)
- **Confidence Scoring**: Get confidence ratings for generated answers
- **Web Interface**: User-friendly interface for managing data and generating answers
- **Batch Processing**: Process multiple questions simultaneously
- **Export Results**: Export generated answers for proposal documents

## Architecture

### Backend (FastAPI)
- **Document Processor**: Extracts Q&A pairs from various file formats
- **Vector Store**: ChromaDB for semantic search and storage
- **RAG System**: Claude AI integration for answer generation
- **Excel Handler**: Smart Excel parsing and question extraction
- **API Endpoints**: RESTful API for all operations

### Frontend (Vanilla JavaScript)
- **Upload Interface**: Drag-and-drop file uploads
- **Question Review**: Preview and validate extracted questions
- **Answer Generation**: Display generated answers with confidence scores
- **Data Management**: Historical data upload and management
- **Statistics Dashboard**: System statistics and category breakdown

## Installation

### Prerequisites
- Python 3.11 or higher
- uv package manager
- Anthropic API key (Claude Pro subscription)

### Setup Steps

1. **Clone/Download** the Requirements Answer Tool to your desired location

2. **Install uv package manager** (if not already installed):
   ```bash
   pip install uv
   ```

3. **Set up environment**:
   ```bash
   cd requirements-answer-tool
   uv sync
   ```

4. **Configure API Key**:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to `.env`:
     ```
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```

5. **Start the application**:
   
   **Windows:**
   ```bash
   run.bat
   ```
   
   **Manual start:**
   ```bash
   cd backend
   uv run uvicorn app:app --reload --port 8000
   ```

6. **Access the application**:
   - Web Interface: http://localhost:8000/app
   - API Documentation: http://localhost:8000/docs

## Usage Guide

### 1. Upload Historical Data

First, build your knowledge base by uploading historical Q&A documents:

1. Go to the "Manage Historical Data" tab
2. Upload files containing your past Q&A data:
   - **Excel files**: Should have question and answer columns
   - **Word documents**: Q&A pairs in text format
   - **PDF files**: Extracted text with Q&A patterns
   - **Text files**: Structured Q&A content
3. Review the processing results
4. Check statistics to confirm data was imported

### 2. Process Client Questions

Upload and process new client questions:

1. Go to the "Upload Questions" tab
2. Upload Excel file with client questions
   - Download the template for proper formatting
   - Tool automatically detects question columns
3. Review extracted questions
4. Click "Generate All Answers" to process all questions
5. Review generated answers and confidence scores
6. Export results for your proposal

### 3. Single Question Mode

For individual questions:

1. Go to the "Single Question" tab
2. Enter your question
3. Optionally add context or filter by category
4. Generate answer and review sources
5. Use suggestions to improve manual answers

### 4. Data Management

Monitor and manage your knowledge base:

1. Go to the "Statistics" tab
2. View total Q&A pairs and categories
3. Monitor system performance
4. Clear data if needed (use with caution)

## File Format Guidelines

### Excel Files (Client Questions)
- Use clear column headers like "Question", "Requirement", or "Query"
- One question per row
- Include priority or category columns if available

### Historical Q&A Files
- **Excel**: Separate columns for questions and answers
- **Word**: Use clear Q&A patterns (Q:, A:, Question:, Answer:)
- **PDF**: Structured text with identifiable Q&A sections
- **Text**: Formatted Q&A pairs with clear separators

## API Endpoints

The tool provides a comprehensive REST API:

- `POST /upload-historical-data` - Upload historical Q&A files
- `POST /upload-client-questions` - Upload Excel with client questions
- `POST /generate-answer` - Generate answer for single question
- `POST /generate-answers` - Batch generate answers
- `GET /categories` - List all categories
- `GET /search` - Search Q&A pairs
- `GET /stats` - System statistics
- `DELETE /clear-data` - Clear all data

Full API documentation available at: http://localhost:8000/docs

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)

### Data Storage
- Vector database: `data/chroma_db/`
- Uploaded files: `data/uploads/`
- Processed files: `data/processed/`

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Anthropic API key is set in `.env`
   - Verify you have Claude Pro subscription

2. **File Processing Error**
   - Check file format is supported
   - Ensure files contain readable Q&A content
   - Try processing files one at a time

3. **No Questions Detected**
   - Review Excel column headers
   - Use the provided template
   - Manually specify question column if needed

4. **Low Confidence Scores**
   - Add more historical data
   - Ensure questions are similar to historical examples
   - Provide additional context

5. **Installation Issues**
   - Ensure Python 3.11+ is installed
   - Install uv: `pip install uv`
   - Run `uv sync` to install dependencies

### Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the console logs for error details
3. Ensure all dependencies are properly installed

## Development

### Adding New Features
- Backend code in `backend/` directory
- Frontend code in `frontend/` directory
- Models defined in `backend/models.py`
- API routes in `backend/app.py`

### Testing
```bash
uv run pytest
```

### Code Quality
```bash
uv run black .
uv run ruff check .
```

## License

This tool is designed for internal use in proposal generation workflows.