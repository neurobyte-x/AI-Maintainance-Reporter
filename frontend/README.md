# AI Maintenance Reporter - React Frontend

## Setup Instructions

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

The frontend will run on http://localhost:3000

Optional: set a custom backend API URL by creating `.env` in `frontend/`:

```
# must include /api suffix
VITE_API_URL=http://localhost:8000/api
```

### 3. Build for Production
```bash
npm run build
```

## Authentication

Only users with **@reva.edu.in** email addresses can sign up and login.

## Features

- 🔐 Secure login/signup with JWT authentication
- 📸 Photo upload for maintenance reports
- 🤖 AI-powered issue detection
- 📊 Real-time ticket dashboard
- ✅ Email validation (@reva.edu.in only)

## Tech Stack

- React 18
- Vite
- React Router
- Axios
- Modern CSS
