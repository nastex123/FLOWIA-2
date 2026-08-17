# FlowMind AI — Unified Startup Script (scripts/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."
& "$ScriptDir\..\start.ps1" @args
