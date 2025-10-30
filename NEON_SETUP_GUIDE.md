# Neon Database Setup Guide

Follow these steps **exactly** to set up your Neon PostgreSQL database for the AI Maintenance Reporter app.

---

## Step 1: Create Neon Account & Project

1. Go to **https://neon.tech**
2. Click **"Sign Up"** (or "Get Started") and create a free account
3. After login, click **"Create Project"** or **"New Project"**
4. Fill in:
   - **Project Name**: `maintenance-reporter` (or any name you like)
   - **Region**: Choose closest to you (e.g., US East, Europe, Asia)
   - **Postgres Version**: Leave default (16 is fine)
5. Click **"Create Project"**

---

## Step 2: Get Your Database Connection String

1. After the project is created, you'll see a **Connection Details** page
2. Look for the **Connection String** section
3. Select **"Pooled connection"** (recommended for serverless/FastAPI)
4. Copy the connection string that looks like:
   ```
   postgresql://username:password@ep-xyz-abc123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
5. **Save this string** - you'll paste it into your `.env` file

---

## Step 3: Open the SQL Editor

1. In your Neon project dashboard, click on **"SQL Editor"** in the left sidebar
   - Or click **"Tables"** then **"Run a query"**
2. You should see a text editor where you can paste SQL commands

---

## Step 4: Create Database Tables

1. Open the file **`NEON_SCHEMA.sql`** in this project folder
2. **Copy the entire contents** of that file
3. **Paste** it into the Neon SQL Editor
4. Click **"Run"** (or press Ctrl+Enter)
5. You should see success messages like:
   ```
   Users table created    | 0
   Tickets table created  | 0
   ```

---

## Step 5: Verify Tables Were Created

1. In the left sidebar, click **"Tables"**
2. You should see:
   - ✅ **users** (with columns: id, email, password_hash, full_name, role, created_at)
   - ✅ **tickets** (with columns: id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority)
3. If you see both tables, you're good to go!

---

## Step 6: Configure Your `.env` File

1. Open the **`.env`** file in your project root (if it doesn't exist, copy `.env.example` to `.env`)
2. Paste your connection string from Step 2:

```env
# Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# JWT Secret Key
SECRET_KEY=your-secret-key-change-this-in-production

# Neon Database URL (paste your connection string here)
DATABASE_URL=postgresql://username:password@ep-xyz-abc123.us-east-2.aws.neon.tech/neondb?sslmode=require

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

3. **Make sure the connection string includes `?sslmode=require` at the end**
4. Save the file

---

## Step 7: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This will install `psycopg2-binary` which is required for PostgreSQL connections.

---

## Step 8: Test the Connection

Run the backend:

```powershell
python main.py
```

You should see:
```
🚀 Starting AI Maintenance Reporter API...
📍 API Docs: http://localhost:8000/docs
🌐 Frontend: http://localhost:8000/static/index.html
```

If you see errors about database connection, double-check:
- ✅ `DATABASE_URL` is correctly pasted in `.env`
- ✅ Connection string includes `?sslmode=require`
- ✅ `psycopg2-binary` is installed

---

## Step 9: Test with Frontend

1. Open a **new terminal**
2. Navigate to frontend:
   ```powershell
   cd frontend
   ```
3. Install dependencies (first time only):
   ```powershell
   npm install
   ```
4. Start the dev server:
   ```powershell
   npm run dev
   ```
5. Open **http://localhost:3000** in your browser
6. Try signing up with an `@reva.edu.in` email
7. Upload a maintenance photo and create a ticket

---

## Troubleshooting

### Error: "psycopg2 is required"
**Solution**: Run `pip install psycopg2-binary`

### Error: "could not connect to server"
**Solution**: 
- Check your `DATABASE_URL` is correct
- Ensure you have internet connection (Neon is cloud-hosted)
- Verify the connection string includes `?sslmode=require`

### Error: "relation 'users' does not exist"
**Solution**: You didn't run the SQL schema. Go back to **Step 4** and run `NEON_SCHEMA.sql` in the Neon SQL Editor.

### Error: "password authentication failed"
**Solution**: The password in your connection string might have special characters. Neon should URL-encode them automatically, but if issues persist, regenerate the password in Neon settings.

---

## Environment Variables Summary

Your `.env` file should have these 3 essential variables:

```env
GOOGLE_API_KEY=AIza...your_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

---

## What's Next?

Once everything works locally:
- **Backend Deployment**: Deploy to Render/Railway/Fly.io and set the same env vars
- **Frontend Deployment**: Build with `npm run build` and deploy to Firebase/Vercel/Netlify
- **Frontend Config**: Set `VITE_API_URL` in frontend `.env` to your deployed backend URL

---

## Quick Reference: Neon Dashboard URLs

- **Dashboard**: https://console.neon.tech
- **SQL Editor**: https://console.neon.tech/app/projects/[your-project-id]/branches/main/sql-editor
- **Connection Details**: https://console.neon.tech/app/projects/[your-project-id]/connection-details

---

✅ **You're all set!** If you run into any issues, check the troubleshooting section or verify each step carefully.
