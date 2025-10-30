# Quick Setup Guide

## Step 1: Install Frontend Dependencies

Open a NEW terminal (keep the backend running) and run:

```powershell
cd frontend
npm install
```

## Step 2: Start the Frontend

Once installation is complete, run:

```powershell
npm run dev
```

## Step 3: Access the Application

Open your browser and go to:
**http://localhost:3000**

## Step 4: Sign Up

1. Click "Sign up here"
2. Enter your details:
   - Full Name: Your name
   - Email: **must end with @reva.edu.in**
   - Password: At least 6 characters
3. Click "Sign Up"

## Step 5: Start Using!

You'll be automatically logged in and can start creating maintenance reports!

---

## Important Notes:

✅ Backend is running on port 8000
✅ Frontend will run on port 3000
✅ Only @reva.edu.in emails are allowed
✅ All API routes are protected with JWT authentication
✅ Your session persists across page refreshes

## Troubleshooting:

**If npm install fails:**
```powershell
# Clear npm cache and try again
npm cache clean --force
npm install
```

**If port 3000 is busy:**
Edit `frontend/vite.config.js` and change the port:
```javascript
server: {
  port: 3001,  // Change to any available port
  ...
}
```

**If you can't login:**
- Make sure you're using an @reva.edu.in email
- Check that the backend is running on port 8000
- Clear browser localStorage and try again
