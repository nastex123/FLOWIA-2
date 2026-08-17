# FlowMind AI — Windows PowerShell Unified Startup Script
$ErrorActionPreference = "Stop"

# Navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check Python availability
if (Get-Command python -ErrorAction SilentlyContinue) {
    python start.py $args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py start.py $args
} else {
    Write-Error "[ERROR] Python was not found on your system PATH."
}
