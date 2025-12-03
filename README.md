# NLP Agentic AI Feedback Analysis System

A production-grade multi-agent AI system for feedback analysis using LangChain, ChromaDB, and FastAPI with sentiment analysis, topic modeling, and RAG capabilities.

## 🚀 Project Status

**Current Phase:** ✅ **PRODUCTION READY** (All 3 Iterations Complete)
**Version:** 1.0.0
**Status:** Fully Operational

## ✨ Features

- 🤖 **Multi-Agent Architecture** - 4 specialized LangChain agents working in harmony
- 📊 **Sentiment Analysis** - VADER-powered emotion detection
- 🔍 **Topic Modeling** - BERTopic automatic theme discovery
- 📝 **Text Summarization** - TextRank extractive summaries
- 🔎 **RAG Retrieval** - Semantic search with ChromaDB
- 🚀 **FastAPI Backend** - Async, high-performance REST API
- 🧪 **Comprehensive Testing** - Unit + integration tests
- 🐳 **Docker Ready** - Complete containerization
- 📚 **API Documentation** - Interactive Swagger UI

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Agent Framework** | LangChain |
| **API** | FastAPI (Async) |
| **Vector Store** | ChromaDB |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Sentiment** | VADER |
| **Topic Modeling** | BERTopic + UMAP |
| **Summarization** | TextRank (spaCy) |
| **Testing** | pytest + pytest-asyncio |
| **Containerization** | Docker + Docker Compose |

## 📋 Quick Start

### Prerequisites

- Python 3.11+
- 4GB+ RAM
- Internet connection (first run only, for model downloads)

### Local Development

1. **Clone and setup**
```powershell
git clone <repo-url>
cd Project

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate  # Unix/Mac
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. **Configure environment**
```powershell
Copy-Item .env.example .env  # Windows
# cp .env.example .env  # Unix/Mac
```

4. **Run the application**
```powershell
python -m uvicorn src.api.main:app --reload
```

5. **Access the system**
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Docker Deployment

```bash
# Build and run
docker-compose up --build

# Verify health
curl http://localhost:8000/health
```

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Welcome message |
| `/health` | GET | System health check |
| `/info` | GET | System information |

### Feedback Analysis

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/upload` | POST | Upload feedback data |
| `/api/v1/analyze` | POST | Analyze existing feedback |
| `/api/v1/process` | POST | Upload + Analyze (one-step) |
| `/api/v1/feedback/{id}` | GET | Get feedback summary |
| `/api/v1/statistics` | GET | System statistics |

## 💡 Usage Examples

### Quick Test with Sample Data

```bash
# Process sample feedback (60 entries)
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d @test_data/sample_feedback.json
```

### Python Example

```python
import requests

# Upload and analyze feedback
feedback_data = {
    "feedback": [
        "Excellent product! Highly recommend.",
        "Poor quality. Very disappointed.",
        "Good value for money."
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/process",
    json=feedback_data
)

result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Insights: {result['report']['key_insights']}")
```

**See [docs/API_USAGE_EXAMPLES.md](docs/API_USAGE_EXAMPLES.md) for complete API documentation.**

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│         (src/api/main.py)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Agent Orchestrator              │
│    (Multi-Agent Coordinator)            │
└──┬──────┬──────┬──────────┬────────────┘
   │      │      │          │
   ▼      ▼      ▼          ▼
┌─────┐ ┌────┐ ┌─────┐  ┌───────┐
│Data │ │Ana │ │Ret  │  │Synth  │
│Ing. │ │lysis│ │rieval│  │esis │
└──┬──┘ └─┬──┘ └──┬──┘  └───┬───┘
   │      │       │         │
   ▼      ▼       ▼         ▼
┌─────────────────────────────────────────┐
│         Core NLP Services               │
│  • VADER (Sentiment)                    │
│  • BERTopic (Topics)                    │
│  • TextRank (Summary)                   │
│  • sentence-transformers (Embeddings)   │
│  • ChromaDB (Vector Store)              │
└─────────────────────────────────────────┘
```

## 📂 Project Structure

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
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   ├── services/            # Core services
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   └── nlp_processors.py
│   └── utils/               # Configuration & utilities
│       ├── config.py
│       ├── exceptions.py
│       └── logging_config.py
├── tests/                   # Complete test suite
│   ├── conftest.py
│   ├── test_nlp_processors.py
│   ├── test_agents.py
│   └── test_api.py
├── test_data/               # Sample data
│   └── sample_feedback.json
├── docs/                    # Documentation
│   └── API_USAGE_EXAMPLES.md
├── config.yaml              # Configuration
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker config
├── docker-compose.yml       # Docker Compose
└── README.md                # This file
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_api.py

# Verbose output
pytest -v
```

### Test Coverage

- **Unit Tests**: NLP processors, agents, services
- **Integration Tests**: API endpoints, multi-agent workflows
- **Target Coverage**: 80%+

## ⚙️ Configuration

### config.yaml

Main configuration file:
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

nlp:
  min_topic_size: 5
  max_topics: 10
  sentiment_threshold: 0.05
```

### Environment Variables

Create `.env` from `.env.example`:
```bash
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CHROMA_PERSIST_DIR=./chroma_db
```

## 📊 What It Does

### 1. Data Ingestion
- Validates feedback text quality
- Cleans and normalizes text
- Stores in ChromaDB with embeddings
- Generates unique batch IDs

### 2. Sentiment Analysis
- VADER compound scoring
- Positive/Negative/Neutral classification
- Aggregated statistics
- Distribution analysis

### 3. Topic Modeling
- Automatic theme discovery
- Keyword extraction per topic
- Representative document identification
- Topic assignment for each feedback

### 4. Text Summarization
- Extractive summarization
- Key phrase extraction
- Configurable summary length

### 5. RAG Retrieval
- Semantic similarity search
- Context-aware retrieval
- Topic-based document matching

### 6. Report Generation
- Comprehensive insights
- Actionable recommendations
- Executive summaries
- Key findings highlights

## 🚀 Performance

- **Processing Speed**: ~100 feedback entries in 3-5 seconds
- **Memory Usage**: ~1-2GB for moderate datasets
- **Scalability**: Async processing for large batches
- **Storage**: Efficient vector embeddings (384 dimensions)

## 📚 Documentation

- **[API Usage Guide](docs/API_USAGE_EXAMPLES.md)** - Complete API examples
- **[CLAUDE.md](CLAUDE.md)** - Architecture & implementation details
- **[Swagger UI](http://localhost:8000/docs)** - Interactive API docs

## 🔍 Example Output

### Input
```json
{
  "feedback": [
    "Great product! Very satisfied.",
    "Terrible service. Will not recommend.",
    "Good value for money."
  ]
}
```

### Output
```json
{
  "sentiment": {
    "average_compound": 0.15,
    "sentiment_distribution": {
      "positive": 1,
      "neutral": 1,
      "negative": 1
    }
  },
  "report": {
    "key_insights": [
      "Mixed feedback: 33.3% positive, 33.3% negative",
      "Overall sentiment is neutral"
    ],
    "recommendations": [
      "Focus on addressing negative feedback themes"
    ]
  }
}
```

## 🎯 Use Cases

- **Product Feedback Analysis** - Analyze customer reviews
- **Support Ticket Analysis** - Identify common issues
- **Survey Response Analysis** - Extract key themes
- **Social Media Monitoring** - Sentiment tracking
- **Employee Feedback** - HR insights
- **Market Research** - Competitor analysis

## 🐛 Troubleshooting

### Common Issues

**1. Import errors**
```bash
# Solution: Ensure all dependencies installed
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**2. Port already in use**
```bash
# Solution: Use different port
uvicorn src.api.main:app --port 8001
```

**3. ChromaDB errors**
```bash
# Solution: Clear database
rm -rf chroma_db/
```

## 👥 Team

6-person development team
CS4063 - Natural Language Processing
Development Track Project

## 📝 License

Educational Project - CS4063 NLP Course

## 🙏 Acknowledgments

- **Course**: CS4063 Natural Language Processing
- **Technologies**: LangChain, FastAPI, ChromaDB, VADER, BERTopic
- **Models**: Hugging Face, spaCy

---

## 📈 Development Progress

```
[██████████] 100% Complete

✅ Iteration 1: Foundation
✅ Iteration 2: Agents & Pipeline
✅ Iteration 3: Testing & Production
```

**Status**: Production Ready | **Version**: 1.0.0 | **Last Updated**: 2025-12-03

---

**Ready to analyze feedback!** 🚀

For questions or issues, check the [API documentation](docs/API_USAGE_EXAMPLES.md) or review the [complete architecture guide](CLAUDE.md).
