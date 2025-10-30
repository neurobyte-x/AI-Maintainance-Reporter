# Start Backend and Frontend

Write-Host "🚀 Starting AI Maintenance Reporter..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Please create one from .env.example" -ForegroundColor Yellow
    Write-Host "   Copy .env.example to .env and add your GOOGLE_API_KEY" -ForegroundColor Yellow
    exit 1
}

# Start backend in background
Write-Host "📡 Starting FastAPI backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "⚛️  Starting React frontend on port 3000..." -ForegroundColor Cyan
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

npm run dev

Set-Location ..
