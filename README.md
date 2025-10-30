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

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root with at least:

```
# Required
GOOGLE_API_KEY=your_actual_google_api_key_here
SECRET_KEY=change_me

# Optional: set this to use Neon (PostgreSQL). If not set, the app uses local SQLite.
# Example (Neon):
# DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
DATABASE_URL=
```

### 3. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 4. Run the Backend

```bash
python main.py
```

The backend will start at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Setup and Run the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at:
- **React App**: http://localhost:3000

## Usage

1. **Sign Up**: Create an account with your @reva.edu.in email
2. **Login**: Access your dashboard
3. **Report Issue**: Click "New Report", fill in details, and upload a photo
4. **AI Analysis**: The system automatically analyzes the image and classifies the issue
5. **View Tickets**: See all reported issues in the dashboard

## API Endpoints

### Authentication

#### Sign Up
```
POST /api/auth/signup
Content-Type: application/json

Body:
{
  "email": "student@reva.edu.in",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

Body:
{
  "email": "student@reva.edu.in",
  "password": "password123"
}
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>
```

### Tickets (All require authentication)

#### Create Ticket
```
POST /api/tickets
Authorization: Bearer <token>
Content-Type: multipart/form-data

Parameters:
- student_name: string
- location: string
- image: file
```

#### Get All Tickets
```
GET /api/tickets
Authorization: Bearer <token>
```

#### Get Single Ticket
```
GET /api/tickets/{ticket_id}
Authorization: Bearer <token>
```

#### Update Ticket Status
```
PUT /api/tickets/{ticket_id}/status?ticket_status=resolved
Authorization: Bearer <token>
```

Valid statuses: `pending`, `in_progress`, `resolved`, `closed`

## Project Structure

```
AAD/
├── main.py                 # FastAPI app with LangGraph workflow
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Environment template
├── .gitignore             # Git ignore file
├── maintenance_tickets.db # SQLite database (auto-created)
├── uploads/               # Uploaded images (auto-created)
└── frontend/              # React frontend
  ├── package.json       # Node dependencies
    ├── vite.config.js     # Vite configuration
    ├── index.html         # HTML entry point
    └── src/
        ├── main.jsx       # React entry point
        ├── App.jsx        # Main App component
        ├── index.css      # Global styles
        ├── api.js         # API client
        └── components/
            ├── Login.jsx      # Login page
            ├── Signup.jsx     # Signup page
            └── Dashboard.jsx  # Main dashboard
├── NEON_SCHEMA.sql        # SQL DDL for Neon (PostgreSQL)
```

## How It Works

### LangGraph Workflow

1. **Analyze Image Node**: Uses Gemini AI to analyze the uploaded image
2. **Classify Issue Node**: Determines issue type (fan, light, furniture, etc.) and priority
3. **Create Ticket Node**: Stores the ticket in the database

```
[Upload Image] → [AI Analysis] → [Classification] → [Create Ticket] → [End]
```

### Priority Levels

- **High**: Critical issues (broken, damaged, dangerous)
- **Medium**: Not working, malfunctioning
- **Low**: Minor issues

### Issue Types

- Fan
- Light
- Furniture
- Electronics
- Electrical
- Other

## Usage Example

1. Open http://localhost:8000/static/index.html
2. Enter your name and location
3. Upload a photo of broken equipment
4. Click "Submit Report"
5. AI analyzes the image and creates a ticket
6. View the ticket in the dashboard

## Troubleshooting

### API Key Issues
- Make sure your `.env` file exists and contains a valid `GOOGLE_API_KEY`
- Check that you have API quota remaining

### Module Not Found
- Run `pip install -r requirements.txt` again
- Make sure you're in the correct directory

### Port Already in Use
- Change the port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

### Database connection errors (Neon)
- Ensure `psycopg2-binary` is installed (`pip install -r requirements.txt`)
- Verify `DATABASE_URL` is correct and includes `sslmode=require`
- Make sure the Neon database has the tables created (run contents of `NEON_SCHEMA.sql`)

## Deploying

### Frontend (Firebase Hosting)
1. Build the React app:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. Deploy with Firebase Hosting (requires `firebase-tools` and project setup). Serve `frontend/dist`.

### Backend (Render/Railway/Fly.io)
- Deploy the FastAPI server on a Python service platform (Render/Railway). Set env vars:
  - `DATABASE_URL` (Neon connection string)
  - `GOOGLE_API_KEY`
  - `SECRET_KEY`
- Expose port 8000 and use the start command `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8000`.

### Database (Neon)
1. Create a Neon project and database
2. Open the SQL editor and paste `NEON_SCHEMA.sql`
3. Copy the connection string and set it as `DATABASE_URL` in your backend environment

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## License

MIT License - Feel free to use and modify!

## Contributing

Pull requests are welcome! Please ensure your code follows the existing style.
