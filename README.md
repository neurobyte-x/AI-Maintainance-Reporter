# AI Maintenance Reporter 🔧

An intelligent maintenance ticket system that uses Google Gemini AI and LangGraph to automatically detect and classify broken equipment from photos.

## Features

- � **Secure Authentication**: Only @reva.edu.in email addresses can sign up/login
- �📸 **Photo Upload**: Students can upload photos of broken equipment
- 🤖 **AI Detection**: Google Gemini 2.5 Pro analyzes images to detect issues
- 🎯 **Smart Classification**: LangGraph workflow classifies issue types and priorities
- 🎫 **Automatic Ticketing**: Creates maintenance tickets with detailed descriptions
- 📊 **Real-time Dashboard**: View all tickets with their status and priorities
- � **JWT Authentication**: Secure token-based authentication

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **LangGraph**: Agent workflow orchestration
- **Google Gemini AI**: Image analysis and reasoning
- **SQLite / Neon (PostgreSQL)**: Local dev uses SQLite by default; production can use Neon via DATABASE_URL
- **JWT**: Secure token-based authentication
- **Passlib**: Password hashing with bcrypt

### Frontend
- **React 18**: Modern UI library
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests
- **Modern CSS**: Responsive design with gradients and shadows

## Setup Instructions

### Local Development

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment** - Create `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   ```

3. **Setup Neon Database**:
   - Create account at [neon.tech](https://neon.tech)
   - Create new project
   - Run `NEON_SCHEMA.sql` in SQL Editor
   - Copy connection string to `DATABASE_URL`

4. **Run backend**:
   ```bash
   cd backend
   python main.py
   ```
   API: http://localhost:8000 | Docs: http://localhost:8000/docs

5. **Run frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   App: http://localhost:3000





## Project Structure

```
AAD/
├── backend/
│   ├── __init__.py            # Python package marker
│   └── main.py                # FastAPI app with LangGraph workflow
├── frontend/
│   ├── src/                   # React source files
│   ├── dist/                  # Build output (npm run build)
│   ├── package.json
│   └── vite.config.js
├── static/                     # Static files
├── uploads/                    # User uploaded images
├── .env                        # Environment variables (not committed)
├── .env.example               # Env template
├── requirements.txt            # Python dependencies
├── NEON_SCHEMA.sql            # Database schema for Neon
└── README.md                  # This file
```

## Usage Example

1. Open http://localhost:8000/static/index.html
2. Enter your name and location
3. Upload a photo of broken equipment
4. Click "Submit Report"
5. AI analyzes the image and creates a ticket
6. View the ticket in the dashboard



## Deploy on Render (Free Tier)

1. **Build frontend**:
   ```bash
   cd frontend && npm install && npm run build && cd ..
   ```

2. **Push to GitHub**:
   ```bash
   git add . && git commit -m "Ready for deployment" && git push
   ```

3. **Create Render Web Service**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - New → Web Service → Connect GitHub repo
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
     ```
   - **Start Command**: 
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **Add Environment Variables** in Render:
   ```
   GOOGLE_API_KEY=your_key
   SECRET_KEY=generate_with_python_secrets
   DATABASE_URL=your_neon_connection_string
   ```

5. Deploy! Your app will be live at `https://your-app.onrender.com`

---

**API Documentation**: Visit `/docs` when server is running for interactive Swagger UI
