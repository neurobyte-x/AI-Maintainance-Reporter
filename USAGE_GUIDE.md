# AI Maintenance Reporter - Complete Setup Guide

## 🎉 New Features
- **Beautiful Landing Page** with modern design
- **Separate Login** for Students and Admins
- **Admin Dashboard** to manage and resolve tickets
- **Role-based Access Control**

## 🚀 How to Run

### 1. Start the Backend (FastAPI)
```powershell
python main.py
```
The backend will run on: http://localhost:8000

### 2. Start the Frontend (React)
Open a new terminal:
```powershell
cd frontend
npm run dev
```
The frontend will run on: http://localhost:5173

## 📱 Using the Application

### Landing Page
- Visit http://localhost:5173
- Choose between **Student Login** or **Admin Login**

### For Students:
1. **Sign Up**: Use your @reva.edu.in email
   - Select "Student Login" → "Sign up here"
   - Fill in your details (role will be 'student' automatically)

2. **Login**: Enter your credentials
   - Select "Student Login"
   - Enter @reva.edu.in email and password

3. **Create Tickets**:
   - Click "Create New Ticket"
   - Enter your name and location
   - Upload an image of the maintenance issue
   - AI will analyze and create a ticket automatically

4. **View Your Tickets**: See all submitted tickets with status

### For Admins:
1. **Sign Up/Login**: Use @reva.edu.in email with admin role
   - Select "Admin Login"
   - Create account or login

2. **Admin Dashboard Features**:
   - **Statistics Overview**: See total, pending, in-progress, and resolved tickets
   - **Filter Tickets**: View by status (All, Pending, In Progress, Resolved)
   - **Manage Tickets**:
     - **Pending** → Click "Start Working" → moves to In Progress
     - **In Progress** → Click "Mark Resolved" → moves to Resolved
     - **Resolved** → Click "Close Ticket" → closes the ticket

3. **View Ticket Details**:
   - Student name and location
   - Issue type (Fan, Light, Furniture, Electronics, etc.)
   - AI-generated description
   - Priority level (High, Medium, Low)
   - Creation timestamp

## 🎨 Features

### Student Features:
- ✅ Upload images of maintenance issues
- ✅ AI-powered issue detection and classification
- ✅ Automatic priority assignment
- ✅ Track ticket status in real-time
- ✅ View all submitted tickets

### Admin Features:
- ✅ Comprehensive dashboard with statistics
- ✅ View all tickets from all students
- ✅ Filter tickets by status
- ✅ Update ticket status (Pending → In Progress → Resolved → Closed)
- ✅ View detailed ticket information
- ✅ Priority-based ticket management

### AI Capabilities:
- 🤖 Automatic issue detection from images
- 🎯 Smart classification (Fan, Light, Furniture, Electronics, Electrical, Other)
- ⚡ Priority assessment (High, Medium, Low)
- 📝 Detailed description generation

## 🔐 Security
- JWT-based authentication
- Role-based access control
- Protected API endpoints
- Secure password hashing with bcrypt

## 📊 Tech Stack
- **Frontend**: React + Vite
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 2.5 Pro
- **Workflow**: LangGraph
- **Database**: SQLite
- **Authentication**: JWT + Passlib

## 🎯 User Roles

### Student (role: "student")
- Can create tickets
- Can view their own tickets
- Cannot access admin dashboard

### Admin (role: "admin")
- Can view all tickets
- Can update ticket status
- Access to admin dashboard
- Cannot create tickets (admin-only management)

## 📝 Database Schema

### Users Table:
- id (Primary Key)
- email (Unique, @reva.edu.in)
- password_hash
- full_name
- **role** (student/admin) ⭐ NEW
- created_at

### Tickets Table:
- id (Primary Key)
- user_id (Foreign Key)
- student_name
- location
- issue_type
- description
- image_path
- status (pending/in_progress/resolved/closed)
- priority (high/medium/low)
- created_at

## 🚨 Creating Admin Users

To create an admin user:
1. Go to http://localhost:5173
2. Click "Admin Login"
3. Click "Sign up here"
4. Register with @reva.edu.in email
5. The role will automatically be set to 'admin'

## 📸 Screenshots Guide

### Landing Page:
- Modern hero section
- Features showcase
- How it works section
- About section

### Student Dashboard:
- Create ticket form
- Ticket list with status badges
- Image upload with preview

### Admin Dashboard:
- Statistics cards (Total, Pending, In Progress, Resolved)
- Filter buttons
- Ticket management cards
- Action buttons for status updates

## 🔧 Troubleshooting

1. **Port already in use**:
   - Backend: Change port in main.py
   - Frontend: Change port in vite.config.js

2. **Database errors**:
   - Run: `python add_role_column.py` to migrate

3. **Login issues**:
   - Ensure email ends with @reva.edu.in
   - Check if user role matches login type

## 🎊 Enjoy your AI-powered maintenance system!
