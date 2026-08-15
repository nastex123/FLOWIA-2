# Start FlowMind AI Backend Locally (No Docker Required)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting FlowMind AI Backend (100% Local Mode)" -ForegroundColor Cyan
Write-Host "   Database: Local SQLite (data/flowmind.db)" -ForegroundColor Green
Write-Host "   Storage:  Local Disk (data/storage/)" -ForegroundColor Green
Write-Host "   AI / ML:  Local Pure Libraries (scikit-learn, etc.)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Set Python path to include backend
$env:PYTHONPATH = "$PSScriptRoot\..\backend"

# Start Uvicorn dev server
python -m uvicorn app.main:app --app-dir "$PSScriptRoot\..\backend" --reload --host 127.0.0.1 --port 8000
