# 🎉 AI Maintenance Reporter - Complete Setup

## ✅ What's Been Created

### Backend (FastAPI + LangGraph)
- ✅ JWT-based authentication system
- ✅ User registration/login with @reva.edu.in validation
- ✅ Protected API endpoints
- ✅ Image analysis using Gemini AI
- ✅ LangGraph workflow for issue classification
- ✅ SQLite database with users and tickets tables
- ✅ Secure password hashing with bcrypt

### Frontend (React + Vite)
- ✅ Modern React 18 application
- ✅ Login and Signup pages with validation
- ✅ Protected dashboard with ticket management
- ✅ Photo upload with preview
- ✅ Real-time ticket display
- ✅ Responsive design
- ✅ JWT token management

## 🚀 Quick Start

### 1. Install Backend Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_actual_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### 4. Start Everything (Easy Way)
```powershell
.\start.ps1
```

OR manually:

**Terminal 1 - Backend:**
```powershell
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 👤 How to Use

1. **Sign Up** at http://localhost:3000/signup
   - Use your @reva.edu.in email
   - Create a strong password

2. **Login** with your credentials

3. **Report Issues**
   - Click "New Report"
   - Enter your name and location
   - Upload a photo of the broken item
   - AI will automatically analyze and classify

4. **View Tickets**
   - See all reported issues
   - Check status and priority
   - View AI-generated descriptions

## 🔒 Security Features

- ✅ Email validation (only @reva.edu.in)
- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Protected API routes
- ✅ Secure session management

## 📋 Database Schema

### Users Table
- id (PRIMARY KEY)
- email (UNIQUE)
- password_hash
- full_name
- created_at

### Tickets Table
- id (PRIMARY KEY)
- user_id (FOREIGN KEY → users)
- student_name
- location
- issue_type
- description
- image_path
- status
- priority
- created_at

## 🎯 Features

### Authentication
- Sign up with REVA email only
- Secure login
- Auto-logout on token expiry
- Remember user session

### Issue Reporting
- Upload photos
- Auto-detect broken items
- Classify issue type (Fan, Light, Furniture, etc.)
- Assign priority (High, Medium, Low)
- Store detailed descriptions

### Dashboard
- View all tickets
- Real-time updates
- Filter by status
- Responsive design

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.115.0
- LangGraph 0.2.45
- Google Gemini AI
- JWT (PyJWT 2.9.0)
- Passlib with bcrypt
- SQLite

**Frontend:**
- React 18
- Vite 5
- React Router 6
- Axios
- Modern CSS

## 📝 Environment Variables

Create a `.env` file:
```env
GOOGLE_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_jwt_secret_key_min_32_chars
```

## 🔧 Troubleshooting

### Backend Issues
- Make sure port 8000 is free
- Check if .env file exists with valid API keys
- Verify Python dependencies are installed

### Frontend Issues
- Make sure port 3000 is free
- Run `npm install` in frontend directory
- Check if backend is running on port 8000

### Authentication Issues
- Only @reva.edu.in emails are allowed
- Password must be at least 6 characters
- Clear browser localStorage if having login issues

## 📦 Files Created

### Backend
- `main.py` - FastAPI application with auth and LangGraph
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (you need to add your keys)
- `.env.example` - Template

### Frontend
- `frontend/package.json` - Node dependencies
- `frontend/vite.config.js` - Vite configuration
- `frontend/src/App.jsx` - Main application
- `frontend/src/components/Login.jsx` - Login page
- `frontend/src/components/Signup.jsx` - Signup page
- `frontend/src/components/Dashboard.jsx` - Main dashboard
- `frontend/src/api.js` - API client
- `frontend/src/index.css` - Global styles

### Scripts
- `start.ps1` - PowerShell script to start both servers

## 🎨 UI Features

- Beautiful gradient backgrounds
- Card-based layout
- Priority badges (High/Medium/Low)
- Status indicators
- Responsive design
- Image preview
- Form validation
- Error/success messages

## 🚀 Production Deployment

1. Change SECRET_KEY in .env to a strong random string
2. Build frontend: `cd frontend && npm run build`
3. Use production ASGI server: `gunicorn main:app`
4. Set up HTTPS
5. Use production database (PostgreSQL)
6. Enable CORS only for your domain

## ✨ Next Steps

Your application is ready! Just:
1. Add your Google API key to `.env`
2. Run `.\start.ps1`
3. Sign up at http://localhost:3000/signup
4. Start reporting issues!

Happy coding! 🎉
