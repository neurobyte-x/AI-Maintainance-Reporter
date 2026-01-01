# AI Maintenance Reporter - Backend Documentation

## Overview

The AI Maintenance Reporter backend is a FastAPI-based REST API that leverages Google Gemini AI and LangGraph for intelligent maintenance ticket management. The system automatically analyzes uploaded images of broken equipment, classifies issues, and creates detailed maintenance tickets with priority levels.

## Architecture

### Core Technologies

- **FastAPI 0.115.4**: Modern, high-performance web framework for building APIs
- **LangGraph 0.2.45**: Agent workflow orchestration and state management
- **Google Gemini 2.5 Flash**: Multi-modal AI for image analysis and reasoning
- **PostgreSQL (Neon)**: Cloud-native production database
- **JWT Authentication**: Secure token-based authentication with PyJWT 2.9.0
- **Uvicorn**: ASGI server for production deployment

### Key Features

- ✅ **AI-Powered Image Analysis**: Automatic detection of equipment issues using Google Gemini
- ✅ **Multi-Agent Workflow**: LangGraph orchestrates image analysis, classification, and ticketing
- ✅ **Secure Authentication**: JWT-based auth with role-based access control (RBAC)
- ✅ **RESTful API**: Comprehensive endpoints for tickets, users, and admin operations
- ✅ **Real-time Processing**: Synchronous workflow execution for immediate results
- ✅ **Database Abstraction**: Supports PostgreSQL with query adaptation layer

## Project Structure

```
backend/
├── __init__.py           # Python package marker
└── main.py               # Main FastAPI application (893 lines)
    ├── Database Layer
    ├── Authentication System
    ├── LangGraph Workflow
    ├── API Endpoints
    └── Static File Serving
```

## Environment Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database (Neon recommended)
- Google AI API Key

### Environment Variables

Create a `.env` file in the project root:

```env
# Google AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key

# Security
SECRET_KEY=your_secure_random_secret_key_change_in_production

# Database
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# Server (Optional)
PORT=8000
```

### Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Initialize Database**:
```bash
# Run the SQL schema in your Neon dashboard
# File: NEON_SCHEMA.sql
```

3. **Run the Server**:
```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

## Database Schema

### Tables

#### `users` Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_users_email` on `email`

#### `tickets` Table
```sql
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    student_name VARCHAR(255),
    location VARCHAR(255),
    issue_type VARCHAR(100),
    description TEXT,
    image_path TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority VARCHAR(50) DEFAULT 'medium',
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Indexes**:
- `idx_tickets_user_id` on `user_id`
- `idx_tickets_created_at` on `created_at DESC`
- `idx_tickets_status` on `status`

## Authentication System

### Password Hashing

Uses SHA-256 hashing with a secret key salt:
```python
hash = sha256(password + SECRET_KEY)
```

### JWT Tokens

- **Algorithm**: HS256
- **Expiration**: 24 hours (1440 minutes)
- **Payload**: `{ sub: email, user_id: int, exp: timestamp }`

### Roles

- `student`: Can create and view own tickets
- `admin`: Full access to all tickets and user management

## LangGraph Workflow

The AI analysis workflow consists of three sequential nodes:

### 1. Image Analysis Node
**Function**: `analyze_image_node(state)`
- Analyzes uploaded images using Google Gemini 2.5 Flash
- Detects broken/damaged equipment (fans, lights, furniture, electronics)
- Returns 2-3 sentence summary of maintenance issues
- Updates state with issue description

### 2. Issue Classification Node
**Function**: `classify_issue_node(state)`
- Classifies issue type based on keywords
- Determines priority level (low/medium/high)

**Issue Types**:
- Fan
- Light
- Furniture
- Electronics
- Electrical
- Other

**Priority Keywords**:
- **High**: "severely", "broken", "damaged", "fire", "sparking", "dangerous"
- **Medium**: "not working", "malfunctioning", "cracked", "bent"
- **Low**: "no maintenance issues", "minor", "slight"

### 3. Ticket Creation Node
**Function**: `create_ticket_node(state)`
- Marks ticket as ready for database insertion
- Finalizes workflow state

### Workflow State

```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]    # Conversation history
    image_path: str                    # Path to uploaded image
    issue_detected: str                # AI-generated description
    issue_type: str                    # Classified category
    priority: str                      # low/medium/high
    ticket_created: bool               # Workflow completion flag
```

## API Endpoints

### Authentication

#### POST `/api/auth/signup`
Register a new user.

**Request Body**:
```json
{
  "email": "student@reva.edu.in",
  "password": "password123",
  "full_name": "John Doe",
  "role": "student"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@reva.edu.in",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

**Validation**:
- Email must be valid format
- Password minimum 6 characters
- Role must be `student` or `admin`

**Error Codes**:
- `400`: Email already registered
- `500`: Database error

---

#### POST `/api/auth/login`
Authenticate user and get access token.

**Request Body**:
```json
{
  "email": "student@reva.edu.in",
  "password": "password123"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@reva.edu.in",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

**Error Codes**:
- `401`: Invalid credentials
- `500`: Server error

---

#### GET `/api/auth/me`
Get current user information.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "id": 1,
  "email": "student@reva.edu.in",
  "full_name": "John Doe",
  "role": "student"
}
```

**Error Codes**:
- `401`: Invalid/expired token
- `404`: User not found

---

### Ticket Management

#### POST `/api/tickets/`
Create a new maintenance ticket with AI analysis.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data**:
- `student_name` (string): Name of student reporting
- `location` (string): Equipment location
- `image` (file): Image of broken equipment

**Process Flow**:
1. Save uploaded image to `uploads/` directory
2. Initialize LangGraph workflow with image path
3. Execute AI analysis pipeline:
   - Analyze image with Gemini
   - Classify issue type
   - Determine priority
4. Store ticket in database
5. Return created ticket

**Response** (200):
```json
{
  "id": 1,
  "student_name": "John Doe",
  "location": "Room 301",
  "issue_type": "Fan",
  "description": "Ceiling fan blade is severely bent and broken. Potential safety hazard.",
  "status": "pending",
  "created_at": "2025-12-17T10:30:00",
  "priority": "high"
}
```

**Error Codes**:
- `400`: No image file provided
- `401`: Authentication required
- `500`: Processing error (check server logs)

---

#### GET `/api/tickets/`
Get all tickets (filtered by role).

**Headers**:
```
Authorization: Bearer <token>
```

**Authorization**:
- **Students**: See only their own tickets
- **Admins**: See all tickets

**Response** (200):
```json
[
  {
    "id": 1,
    "student_name": "John Doe",
    "location": "Room 301",
    "issue_type": "Fan",
    "description": "Ceiling fan blade is severely bent...",
    "status": "pending",
    "created_at": "2025-12-17T10:30:00",
    "priority": "high"
  },
  {
    "id": 2,
    "student_name": "Jane Smith",
    "location": "Lab 2",
    "issue_type": "Light",
    "description": "Fluorescent light not working...",
    "status": "in_progress",
    "created_at": "2025-12-17T09:15:00",
    "priority": "medium"
  }
]
```

---

#### GET `/api/tickets/{ticket_id}`
Get specific ticket details.

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `ticket_id` (integer): Ticket ID

**Authorization**:
- Must be ticket owner or admin

**Response** (200):
```json
{
  "id": 1,
  "student_name": "John Doe",
  "location": "Room 301",
  "issue_type": "Fan",
  "description": "Ceiling fan blade is severely bent and broken.",
  "status": "pending",
  "created_at": "2025-12-17T10:30:00",
  "priority": "high"
}
```

**Error Codes**:
- `401`: Authentication required
- `404`: Ticket not found or access denied

---

#### PUT `/api/tickets/{ticket_id}/status`
Update ticket status (admin only).

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `ticket_status` (string): New status

**Valid Statuses**:
- `pending`
- `in_progress`
- `resolved`
- `closed`

**Example**:
```
PUT /api/tickets/1/status?ticket_status=in_progress
```

**Response** (200):
```json
{
  "message": "Ticket status updated successfully",
  "ticket_id": 1,
  "status": "in_progress"
}
```

**Error Codes**:
- `400`: Invalid status
- `403`: Admin access required
- `404`: Ticket not found

---

#### PATCH `/api/tickets/{ticket_id}`
Update ticket fields (owner or admin).

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "student_name": "John Doe Updated",
  "location": "Room 302",
  "issue_type": "Electrical",
  "description": "Updated description",
  "priority": "high",
  "status": "in_progress"
}
```

**Authorization**:
- Students: Can update own tickets (except status)
- Admins: Can update all fields including status

**Response** (200):
```json
{
  "id": 1,
  "student_name": "John Doe Updated",
  "location": "Room 302",
  "issue_type": "Electrical",
  "description": "Updated description",
  "status": "in_progress",
  "created_at": "2025-12-17T10:30:00",
  "priority": "high"
}
```

**Validation**:
- Priority: `low`, `medium`, `high`
- Status: `pending`, `in_progress`, `resolved`, `closed`

**Error Codes**:
- `400`: Invalid field values
- `403`: Not authorized
- `404`: Ticket not found

---

#### DELETE `/api/tickets/{ticket_id}`
Delete ticket and associated image (admin only).

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "message": "Ticket deleted successfully",
  "ticket_id": 1
}
```

**Side Effects**:
- Deletes ticket from database
- Removes uploaded image file from `uploads/` directory

**Error Codes**:
- `403`: Admin access required
- `404`: Ticket not found

---

### Health Check

#### GET `/api/health`
Check system health and database connectivity.

**Response** (200):
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

**Status Values**:
- `healthy`: All systems operational
- `unhealthy`: Database connection failed

**Database Values**:
- `connected`: Database accessible
- `error: <message>`: Connection error details

---

## Static File Serving

### Endpoints

- **`/static/*`**: Serves files from `static/` directory
- **`/uploads/*`**: Serves uploaded images (requires authentication in production)
- **`/assets/*`**: Serves React build assets (Vite output)
- **`/*`**: Catch-all for React SPA routing

### Frontend Integration

When React app is built (`npm run build`):
1. Vite creates `frontend/dist/` directory
2. Backend serves `index.html` for all non-API routes
3. Assets loaded from `/assets/*` path

## Error Handling

### HTTP Exception Format

All errors return consistent JSON structure:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input, validation failed |
| 401 | Unauthorized | Missing/invalid/expired token |
| 403 | Forbidden | Insufficient permissions (not admin) |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Database error, AI processing error |

### Logging

Server logs include:
- Request details (student name, location, image filename)
- Workflow execution steps
- Database operations
- Error tracebacks for debugging

**Example Log Output**:
```
Received request - Student: John Doe, Location: Room 301, Image: broken_fan.jpg
Saving image to: uploads/20251217_103000_broken_fan.jpg
Image saved successfully
Running LangGraph workflow...
Workflow complete - Issue: Fan, Priority: high
Storing ticket in database...
Ticket #1 created successfully!
```

## Security Considerations

### Authentication

- **Password Storage**: SHA-256 with secret key salt (consider bcrypt for enhanced security)
- **Token Expiration**: 24-hour validity
- **HTTPS**: Required in production for token transmission
- **CORS**: Currently allows all origins (`*`) - restrict in production

### File Upload Security

- **Image Validation**: Uses PIL to verify valid image files
- **File Storage**: Timestamped filenames prevent overwrites
- **Path Traversal**: Uses Path objects to prevent directory traversal

### Database Security

- **SQL Injection**: Parameterized queries throughout
- **Connection String**: Loaded from environment variables
- **SSL Mode**: Required for PostgreSQL connections

### Recommendations for Production

1. **Enable HTTPS**: Use reverse proxy (nginx) or platform SSL
2. **Restrict CORS**: Whitelist frontend domain only
3. **Rate Limiting**: Add middleware to prevent abuse
4. **File Size Limits**: Implement max upload size (currently unlimited)
5. **Switch to bcrypt**: Replace SHA-256 with bcrypt for password hashing
6. **Add Logging**: Implement structured logging (e.g., structlog)
7. **Environment Validation**: Fail fast if required env vars missing

## Deployment

### Render.com Configuration

**`render.yaml`** (should exist in project root):
```yaml
services:
  - type: web
    name: ai-maintenance-reporter
    env: python
    buildCommand: "pip install -r requirements.txt && cd frontend && npm install && npm run build"
    startCommand: "cd backend && python main.py"
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: maintenance-db
          property: connectionString
```

### Manual Deployment Steps

1. **Create Neon Database**:
   - Sign up at [neon.tech](https://neon.tech)
   - Create new project
   - Run `NEON_SCHEMA.sql` in SQL Editor
   - Copy connection string

2. **Deploy to Render**:
   - Connect GitHub repository
   - Create new Web Service
   - Set environment variables:
     - `GOOGLE_API_KEY`
     - `SECRET_KEY`
     - `DATABASE_URL`
   - Deploy

3. **Verify Deployment**:
   ```bash
   curl https://your-app.onrender.com/api/health
   ```

## API Testing

### Using cURL

**Health Check**:
```bash
curl http://localhost:8000/api/health
```

**Signup**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@reva.edu.in",
    "password": "password123",
    "full_name": "Test User",
    "role": "student"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@reva.edu.in",
    "password": "password123"
  }'
```

**Create Ticket**:
```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "student_name=John Doe" \
  -F "location=Room 301" \
  -F "image=@/path/to/image.jpg"
```

**Get Tickets**:
```bash
curl http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using FastAPI Interactive Docs

Navigate to `http://localhost:8000/docs` for Swagger UI with:
- Interactive API testing
- Request/response schemas
- Authentication support

## Performance Considerations

### Database

- **Connection Pooling**: Not implemented (uses single connections)
- **Indexes**: Optimized for common queries (user_id, created_at, status)
- **Query Optimization**: Direct SQL with minimal joins

### AI Processing

- **Synchronous Execution**: Blocks request until workflow completes
- **Image Processing**: PIL loads entire image into memory
- **Gemini API**: Network latency varies (typically 2-5 seconds)

### Optimization Opportunities

1. **Async Database**: Switch to `asyncpg` for non-blocking queries
2. **Background Tasks**: Use FastAPI BackgroundTasks for AI processing
3. **Caching**: Cache common issue classifications
4. **Image Optimization**: Resize images before sending to Gemini
5. **Connection Pooling**: Implement database connection pool

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
```
Error: Database connection failed: could not connect to server
```
**Solution**: Verify `DATABASE_URL` in `.env` and network access to Neon

**2. Google API Error**
```
Error occurred: API key not valid
```
**Solution**: Check `GOOGLE_API_KEY` in `.env` and verify key is active

**3. Token Expired**
```
401 Unauthorized: Token has expired
```
**Solution**: Re-login to get new access token

**4. Image Upload Failed**
```
500 Internal Server Error: Error processing request
```
**Solution**: Check image file format (must be valid image) and server logs

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

```
fastapi==0.115.4              # Web framework
uvicorn[standard]==0.32.0     # ASGI server
python-multipart==0.0.12      # Form data parsing
pillow==11.0.0                # Image processing
python-dotenv==1.0.1          # Environment variables
google-generativeai==0.8.3    # Google Gemini AI
langgraph==0.2.45             # Agent workflows
langchain-core==0.3.15        # LangChain base
pydantic==2.9.2               # Data validation
pyjwt==2.9.0                  # JWT tokens
psycopg2-binary>=2.9.9        # PostgreSQL driver
```

## License

[Specify your license here]

## Support

For issues and questions:
- GitHub Issues: [Your repository URL]
- Email: [Your support email]
- Documentation: [Your docs URL]

---

**Last Updated**: December 17, 2025  
**Version**: 1.0.0  
**Maintained By**: [Your name/team]
