# API Usage Examples

Complete guide to using the NLP Agentic AI Feedback Analysis System API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (development mode).

---

## Quick Start

### 1. Health Check

Check if the system is running:

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "embedding_service": "operational",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_store": "operational",
  "document_count": "0"
}
```

---

## Upload & Analyze Workflow

### Option A: Two-Step Process

#### Step 1: Upload Feedback

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": [
      "Great product! Very satisfied with the quality.",
      "Terrible service. Will not recommend.",
      "Good value for money. Decent quality."
    ]
  }'
```

**Response:**
```json
{
  "feedback_id": "feedback_abc123xyz",
  "status": "success",
  "count": 3,
  "timestamp": "2025-12-03T12:00:00.000Z"
}
```

#### Step 2: Analyze Uploaded Feedback

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type": application/json" \
  -d '{
    "feedback_id": "feedback_abc123xyz"
  }'
```

**Response:**
```json
{
  "success": true,
  "feedback_id": "feedback_abc123xyz",
  "status": "completed",
  "sentiment": {
    "average_compound": 0.15,
    "average_positive": 0.25,
    "average_negative": 0.12,
    "average_neutral": 0.63,
    "sentiment_distribution": {
      "positive": 1,
      "neutral": 1,
      "negative": 1
    }
  },
  "topics": {
    "topics": [],
    "num_topics": 0,
    "message": "Insufficient texts for topic modeling"
  },
  "report": {
    "feedback_id": "feedback_abc123xyz",
    "summary": "Great product! Very satisfied with the quality...",
    "key_insights": [
      "Mixed feedback: 33.3% positive, 33.3% negative",
      "Overall sentiment is neutral"
    ],
    "recommendations": [
      "Monitor feedback trends over time for emerging patterns"
    ]
  }
}
```

### Option B: One-Step Process (Combined)

Upload and analyze in a single request:

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d @test_data/sample_feedback.json
```

Or with inline data:

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": [
      "Excellent quality and fast shipping!",
      "Product broke after one week. Very disappointed.",
      "Average experience. Nothing special.",
      "Love it! Best purchase this year.",
      "Customer service was unhelpful."
    ]
  }'
```

---

## Advanced Usage

### Upload with Metadata

Add custom metadata to track feedback sources:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": [
      "Great product!",
      "Not satisfied.",
      "Good value."
    ],
    "metadata": [
      {"source": "website", "rating": 5, "user_id": "user_001"},
      {"source": "email", "rating": 2, "user_id": "user_002"},
      {"source": "survey", "rating": 4, "user_id": "user_003"}
    ]
  }'
```

### Analyze with Custom Options

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_id": "feedback_abc123xyz",
    "options": {
      "include_summary": true,
      "include_topics": false
    }
  }'
```

---

## Retrieve Feedback Information

### Get Feedback Summary

```bash
curl http://localhost:8000/api/v1/feedback/feedback_abc123xyz
```

**Response:**
```json
{
  "success": true,
  "feedback_id": "feedback_abc123xyz",
  "total_documents": 60,
  "representative_samples": [
    "The product quality is absolutely outstanding!",
    "Good value for money. Works as expected.",
    "Absolutely love it! Best purchase this year."
  ],
  "sample_count": 5
}
```

### Get System Statistics

```bash
curl http://localhost:8000/api/v1/statistics
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_documents": 150,
    "collection_name": "feedback_embeddings"
  }
}
```

---

## Python Examples

### Using `requests` Library

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Upload feedback
feedback_data = {
    "feedback": [
        "Excellent product! Highly recommend.",
        "Poor quality. Very disappointed.",
        "Good service and fast delivery."
    ]
}

response = requests.post(
    f"{BASE_URL}/api/v1/upload",
    json=feedback_data
)

if response.status_code == 201:
    upload_result = response.json()
    feedback_id = upload_result["feedback_id"]
    print(f"Uploaded successfully: {feedback_id}")

    # Analyze feedback
    analysis_request = {"feedback_id": feedback_id}

    analysis_response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=analysis_request
    )

    if analysis_response.status_code == 200:
        analysis_result = analysis_response.json()

        # Print sentiment
        sentiment = analysis_result["sentiment"]
        print(f"\nAverage Sentiment: {sentiment['average_compound']}")
        print(f"Distribution: {sentiment['sentiment_distribution']}")

        # Print insights
        report = analysis_result["report"]
        print(f"\nKey Insights:")
        for insight in report["key_insights"]:
            print(f"  - {insight}")
```

### One-Step Process

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload and analyze in one step
feedback_data = {
    "feedback": [
        "Amazing quality! Five stars.",
        "Terrible experience. Would not buy again.",
        "Decent product for the price.",
        "Love the design and functionality!",
        "Packaging was poor. Item arrived damaged."
    ]
}

response = requests.post(
    f"{BASE_URL}/api/v1/process",
    json=feedback_data
)

if response.status_code == 201:
    result = response.json()

    print(f"Feedback ID: {result['feedback_id']}")
    print(f"Status: {result['status']}")

    # Sentiment analysis
    sentiment = result["sentiment"]
    dist = sentiment["sentiment_distribution"]

    print(f"\nSentiment Distribution:")
    print(f"  Positive: {dist['positive']}")
    print(f"  Neutral: {dist['neutral']}")
    print(f"  Negative: {dist['negative']}")

    # Summary and insights
    report = result["report"]
    print(f"\nSummary: {report['summary'][:100]}...")
    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")
```

---

## Error Handling

### Empty Feedback

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{"feedback": []}'
```

**Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "feedback"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```

### Nonexistent Feedback ID

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"feedback_id": "invalid_id"}'
```

**Response:** `404 Not Found`
```json
{
  "detail": "Feedback ID 'invalid_id' not found"
}
```

---

## Interactive API Documentation

Visit the automatically generated Swagger UI documentation:

```
http://localhost:8000/docs
```

Features:
- Interactive API testing
- Request/response schemas
- Example values
- Try it out functionality

---

## Rate Limits

Currently no rate limits (development mode).

## Response Formats

All responses are in JSON format with appropriate HTTP status codes:

- `200 OK` - Successful GET/POST
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Tips for Best Results

1. **Minimum Feedback for Topics**: Provide at least 10-15 feedback entries for meaningful topic modeling

2. **Quality Over Quantity**: Well-written, descriptive feedback produces better insights

3. **Batch Processing**: For large datasets (100+ items), use the `/process` endpoint

4. **Metadata Usage**: Add metadata to track feedback sources and filter results

5. **Representative Samples**: Use `/feedback/{id}` endpoint to get representative examples

---

## Complete Workflow Example

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Upload large dataset
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d @test_data/sample_feedback.json \
  > analysis_result.json

# 3. View results
cat analysis_result.json | jq '.report.key_insights'

# 4. Get system statistics
curl http://localhost:8000/api/v1/statistics

# 5. Retrieve feedback summary
FEEDBACK_ID=$(cat analysis_result.json | jq -r '.feedback_id')
curl http://localhost:8000/api/v1/feedback/$FEEDBACK_ID
```

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs and feature requests
- **README**: See project documentation

