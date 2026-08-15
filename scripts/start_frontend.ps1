# Start FlowMind AI Frontend (Next.js)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting FlowMind AI Web Frontend (Next.js 14)" -ForegroundColor Cyan
Write-Host "   URL: http://localhost:3000" -ForegroundColor Green
Write-Host "   Connecting to Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location "$PSScriptRoot\..\frontend"
npm run dev
