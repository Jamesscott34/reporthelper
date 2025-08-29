# 🔌 API Reference

Complete REST API documentation for AI Report Writer. All endpoints require authentication and return JSON responses.

## 🔐 Authentication

### API Token Authentication
```http
Authorization: Token your-api-token-here
Content-Type: application/json
```

### Getting Your Token
```bash
# Via Django shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from rest_framework.authtoken.models import Token
>>> user = User.objects.get(username='your-username')
>>> token, created = Token.objects.get_or_create(user=user)
>>> print(token.key)
```

## 📄 Documents API

### List Documents
```http
GET /api/documents/
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "My Document",
      "original_filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "upload_date": "2025-08-29T10:00:00Z",
      "processed": true,
      "user": 1
    }
  ]
}
```

### Upload Document
```http
POST /api/documents/
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token your-token" \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  http://localhost:8000/api/documents/
```

**Response:**
```json
{
  "id": 1,
  "title": "My Document",
  "original_filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_date": "2025-08-29T10:00:00Z",
  "processed": false,
  "user": 1,
  "processing_status": "pending"
}
```

### Get Document Details
```http
GET /api/documents/{id}/
```

**Response:**
```json
{
  "id": 1,
  "title": "My Document",
  "original_filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_date": "2025-08-29T10:00:00Z",
  "processed": true,
  "user": 1,
  "extracted_text": "Document content here...",
  "breakdown": {
    "id": 1,
    "content": "Step-by-step breakdown...",
    "sections": [...]
  }
}
```

### Delete Document
```http
DELETE /api/documents/{id}/
```

**Response:**
```http
HTTP/1.1 204 No Content
```

## 📝 Annotations API

### List Annotations
```http
GET /api/documents/{document_id}/annotations/
```

**Query Parameters:**
- `annotation_type`: Filter by type (note, question, improvement, highlight)
- `start_offset`: Filter by start position
- `end_offset`: Filter by end position

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "document": 1,
      "annotation_type": "note",
      "start_offset": 100,
      "end_offset": 150,
      "content": "This section needs clarification",
      "color": "#ffff00",
      "user": 1,
      "created_at": "2025-08-29T10:00:00Z",
      "updated_at": "2025-08-29T10:00:00Z",
      "text_content": "selected text here",
      "context": "surrounding context...",
      "source_location": {
        "page": 1,
        "line": 5,
        "paragraph": 2
      }
    }
  ]
}
```

### Create Annotation
```http
POST /api/documents/{document_id}/annotations/
```

**Request:**
```json
{
  "annotation_type": "note",
  "start_offset": 100,
  "end_offset": 150,
  "content": "This section needs clarification",
  "color": "#ffff00"
}
```

**Response:**
```json
{
  "id": 1,
  "document": 1,
  "annotation_type": "note",
  "start_offset": 100,
  "end_offset": 150,
  "content": "This section needs clarification",
  "color": "#ffff00",
  "user": 1,
  "created_at": "2025-08-29T10:00:00Z",
  "updated_at": "2025-08-29T10:00:00Z"
}
```

### Update Annotation
```http
PUT /api/annotations/{id}/
```

**Request:**
```json
{
  "content": "Updated annotation content",
  "color": "#ff0000"
}
```

### Delete Annotation
```http
DELETE /api/annotations/{id}/
```

**Response:**
```http
HTTP/1.1 204 No Content
```

## 🔍 Advanced Endpoints

### Search Annotations
```http
GET /api/documents/{document_id}/annotations/search/?q=search_term
```

### Annotation Statistics
```http
GET /api/documents/{document_id}/annotations/stats/
```

**Response:**
```json
{
  "total_annotations": 25,
  "by_type": {
    "note": 10,
    "question": 8,
    "improvement": 5,
    "highlight": 2
  },
  "by_user": {
    "user1": 15,
    "user2": 10
  }
}
```

### Export Annotations
```http
GET /api/documents/{document_id}/annotations/export/?format=json
```

**Formats:** `json`, `csv`, `pdf`

## 🔄 Processing API

### Trigger Reprocessing
```http
POST /api/documents/{id}/reprocess/
```

**Request:**
```json
{
  "model": "openai/gpt-4",
  "options": {
    "include_sections": true,
    "generate_summary": true
  }
}
```

### Processing Status
```http
GET /api/documents/{id}/status/
```

**Response:**
```json
{
  "status": "processing",
  "progress": 75,
  "estimated_completion": "2025-08-29T10:05:00Z",
  "current_step": "Generating sections"
}
```

## 📊 Analytics API

### Document Analytics
```http
GET /api/analytics/documents/
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `user_id`: Filter by user

**Response:**
```json
{
  "total_documents": 100,
  "processed_documents": 95,
  "average_processing_time": 45.2,
  "popular_file_types": {
    "pdf": 60,
    "docx": 35,
    "txt": 5
  }
}
```

### User Activity
```http
GET /api/analytics/users/{user_id}/activity/
```

## 🌐 WebSocket API

### Connection
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/documents/1/annotations/');
```

### Message Types

#### Annotation Created
```json
{
  "type": "annotation_created",
  "annotation": {
    "id": 1,
    "content": "New annotation",
    "user": "username"
  }
}
```

#### Annotation Updated
```json
{
  "type": "annotation_updated",
  "annotation": {
    "id": 1,
    "content": "Updated content"
  }
}
```

#### Annotation Deleted
```json
{
  "type": "annotation_deleted",
  "annotation_id": 1
}
```

## ❌ Error Handling

### Error Response Format
```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "field_name": ["This field is required."]
  },
  "code": 400
}
```

### Common Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Internal server error |

## 🔒 Rate Limiting

### Default Limits
- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Upload**: 10 files/hour per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📝 SDK Examples

### Python SDK
```python
import requests

class AIReportWriterAPI:
    def __init__(self, token, base_url="http://localhost:8000"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    
    def upload_document(self, file_path, title=None):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'title': title} if title else {}
            response = requests.post(
                f"{self.base_url}/api/documents/",
                headers={"Authorization": f"Token {self.token}"},
                files=files,
                data=data
            )
        return response.json()
    
    def create_annotation(self, document_id, start, end, content, type="note"):
        data = {
            "start_offset": start,
            "end_offset": end,
            "content": content,
            "annotation_type": type
        }
        response = requests.post(
            f"{self.base_url}/api/documents/{document_id}/annotations/",
            headers=self.headers,
            json=data
        )
        return response.json()
```

### JavaScript SDK
```javascript
class AIReportWriterAPI {
    constructor(token, baseUrl = 'http://localhost:8000') {
        this.token = token;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async uploadDocument(file, title = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (title) formData.append('title', title);
        
        const response = await fetch(`${this.baseUrl}/api/documents/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${this.token}`
            },
            body: formData
        });
        
        return response.json();
    }
    
    async createAnnotation(documentId, start, end, content, type = 'note') {
        const response = await fetch(
            `${this.baseUrl}/api/documents/${documentId}/annotations/`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({
                    start_offset: start,
                    end_offset: end,
                    content: content,
                    annotation_type: type
                })
            }
        );
        
        return response.json();
    }
}
```

## 🧪 Testing

### API Testing with curl
```bash
# Set your token
TOKEN="your-api-token-here"
BASE_URL="http://localhost:8000"

# Upload document
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -F "file=@test.pdf" \
  -F "title=Test Document" \
  "$BASE_URL/api/documents/"

# Create annotation
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_offset": 100, "end_offset": 150, "content": "Test annotation", "annotation_type": "note"}' \
  "$BASE_URL/api/documents/1/annotations/"
```

### Postman Collection
Import our [Postman collection](../postman/AI_Report_Writer.json) for interactive API testing.

---

**📚 Need more help?** Check our [Getting Started Guide](GETTING_STARTED.md) or create an issue on GitHub.
