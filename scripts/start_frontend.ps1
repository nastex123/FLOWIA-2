# Script PowerShell para iniciar el Frontend en Next.js
Write-Host "Iniciando FlowMind AI Frontend (Next.js)..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\frontend"
npm run dev
