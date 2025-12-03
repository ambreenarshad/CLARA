# NLP Agentic AI Feedback Analysis System

## Quick Reference Guide

### Project Status
**Current Phase:** Pre-Implementation (Fresh Start)
**Timeline:** 3-4 days
**Team Size:** 6 people
**Architecture:** Multi-Agent System with RAG

---

## Tech Stack Committed

### Core Frameworks
- **Agent Framework:** LangChain
- **Backend API:** FastAPI (async)
- **Vector Database:** ChromaDB
- **Testing:** pytest + pytest-asyncio

### NLP Models & Libraries
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Sentiment Analysis:** VADER (vaderSentiment)
- **Topic Modeling:** BERTopic + UMAP
- **Summarization:** TextRank (pytextrank + spaCy)

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Config Management:** PyYAML + python-dotenv
- **API Documentation:** FastAPI Swagger UI (built-in)

---

## System Architecture

### 4 Specialized Agents (LangChain)

#### 1. Data Ingestion Agent
**Role:** Validate and preprocess incoming feedback data
**Tools:**
- File parsers (JSON, CSV)
- Data validation schemas (Pydantic)
- Text cleaning utilities

#### 2. Analysis Agent
**Role:** Perform sentiment classification and topic discovery
**Tools:**
- VADER sentiment analyzer
- BERTopic for topic modeling
- Statistical analysis utilities

#### 3. Retrieval Agent (RAG)
**Role:** Semantic search and context-aware retrieval
**Tools:**
- ChromaDB vector database
- Sentence-transformers embeddings
- Similarity search algorithms

#### 4. Synthesis Agent
**Role:** Generate comprehensive insights and structured reports
**Tools:**
- TextRank summarization
- Report templating
- Aggregation functions

---

## Implementation Plan: 3 Iterations

### Iteration 1: Foundation (Day 1)
**Focus:** Project structure, dependencies, FastAPI scaffold, core services

**Key Deliverables:**
- Complete directory structure
- requirements.txt with all dependencies
- FastAPI application with /health endpoint
- Configuration management (config.yaml, .env)
- ChromaDB integration + embedding service
- Docker setup (Dockerfile + docker-compose.yml)
- Basic logging

**Success Criteria:**
- ✅ FastAPI server starts
- ✅ ChromaDB connects
- ✅ Embeddings generate
- ✅ Docker containers run

---

### Iteration 2: Agents & Pipeline (Day 2)
**Focus:** LangChain agents, NLP processors, API endpoints

**Key Deliverables:**
- All 4 agents implemented with LangChain
- NLP processors (VADER, BERTopic, TextRank)
- Agent orchestrator for multi-agent workflow
- API endpoints:
  - POST /upload - Feedback upload
  - POST /analyze - Generate report
- Pydantic schemas for validation
- Async processing pipeline

**Success Criteria:**
- ✅ All agents execute
- ✅ Upload endpoint accepts data
- ✅ Report endpoint returns insights
- ✅ Sentiment/topics/summary generated

---

### Iteration 3: Production Ready (Day 3)
**Focus:** Testing, error handling, deployment

**Key Deliverables:**
- Unit tests for agents + services
- Integration tests for API
- Exception handling + recovery
- Comprehensive logging/monitoring
- Complete API documentation
- Docker Compose production setup
- README with setup instructions
- Sample test data

**Success Criteria:**
- ✅ Tests pass (80%+ coverage)
- ✅ Error handling prevents crashes
- ✅ Docker deployment works
- ✅ Documentation complete

---

## Project Structure

```
project_root/
├── src/
│   ├── agents/              # 4 LangChain agents
│   │   ├── data_ingestion_agent.py
│   │   ├── analysis_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── synthesis_agent.py
│   │   └── orchestrator.py
│   ├── api/                 # FastAPI application
│   │   ├── main.py
│   │   └── routes.py
│   ├── services/            # Core services
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   └── nlp_processors.py
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   └── utils/               # Configuration & utilities
│       ├── config.py
│       ├── exceptions.py
│       └── logging_config.py
├── tests/                   # Test suite
├── test_data/               # Sample data
├── docs/                    # Documentation
├── requirements.txt
├── config.yaml
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Dependencies (requirements.txt)

```
# Core Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# Agent Framework
langchain>=0.1.0
langchain-community>=0.0.10

# Vector Store
chromadb>=0.4.22

# NLP Models
sentence-transformers>=2.3.1
vaderSentiment>=3.3.2
bertopic>=0.16.0
spacy>=3.7.0
pytextrank>=3.2.5

# Data Processing
pandas>=2.2.0
numpy>=1.26.0

# Validation & Config
pydantic>=2.6.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
PyYAML>=6.0.1

# API & File Handling
python-multipart>=0.0.9

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0

# Utilities
umap-learn>=0.5.5
```

---

## API Endpoints (Planned)

### Health Check
```
GET /health
Response: { "status": "healthy" }
```

### Upload Feedback
```
POST /upload
Body: { "feedback": ["text1", "text2", ...] }
Response: { "id": "uuid", "status": "processing" }
```

### Generate Report
```
POST /analyze
Body: { "id": "uuid" }
Response: {
  "sentiment": {...},
  "topics": [...],
  "summary": "...",
  "insights": [...]
}
```

---

## Configuration Files

### config.yaml
```yaml
models:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  spacy_model: "en_core_web_sm"

chromadb:
  persist_directory: "./chroma_db"
  collection_name: "feedback_embeddings"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4

logging:
  level: "INFO"
  format: "json"
```

### .env.example
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Vector Store
CHROMA_PERSIST_DIR=./chroma_db

# Model Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Logging
LOG_LEVEL=INFO
```

---

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
    environment:
      - CHROMA_PERSIST_DIR=/app/chroma_db
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

---

## Getting Started (After Implementation)

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run application
uvicorn src.api.main:app --reload
```

### Docker Deployment
```bash
# Build and run
docker-compose up --build

# Access API
curl http://localhost:8000/health
```

---

## Testing Strategy

### Unit Tests
- Test each agent independently
- Test NLP processors (VADER, BERTopic, TextRank)
- Test embedding generation
- Test vector store operations

### Integration Tests
- Test API endpoints end-to-end
- Test multi-agent orchestration
- Test full feedback analysis pipeline

### Test Coverage Target
- Minimum 80% code coverage
- Focus on critical paths

---

## Development Workflow

1. **Iteration 1:** Build foundation → Stop for review
2. **Iteration 2:** Implement agents → Stop for review
3. **Iteration 3:** Add testing/deployment → Final review

Each iteration ends with a checkpoint for:
- Code review
- Testing
- Team alignment
- Issue resolution

---

## Critical Notes

- **All models are CPU-friendly** (no GPU required)
- **ChromaDB persists locally** (./chroma_db directory)
- **FastAPI uses async patterns** for scalability
- **LangChain orchestrates all agents**
- **Configuration supports both local and Docker runs**
- **All dependencies are open-source and free**

---

## Team Distribution Suggestion (6 People)

**Iteration 1:**
- Person 1-2: Project setup + FastAPI scaffold
- Person 3-4: ChromaDB + embedding service
- Person 5-6: Docker + configuration

**Iteration 2:**
- Person 1: Data Ingestion Agent
- Person 2: Analysis Agent
- Person 3: Retrieval Agent (RAG)
- Person 4: Synthesis Agent
- Person 5: Orchestrator + API routes
- Person 6: NLP processors

**Iteration 3:**
- Person 1-2: Unit tests
- Person 3-4: Integration tests + error handling
- Person 5: Documentation + README
- Person 6: Final deployment + demo preparation

---

## Resources

### Documentation Links
- [LangChain Docs](https://python.langchain.com/docs/get_started/introduction)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [BERTopic Docs](https://maartengr.github.io/BERTopic/)
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment)

---

## Current Status

**Phase:** Planning Complete ✅
**Next Step:** Begin Iteration 1 Implementation
**Action Required:** Team approval to proceed

---

*Last Updated: 2025-12-03*
*Project: CS4063 NLP Development Track*
*Architecture: Multi-Agent RAG System*