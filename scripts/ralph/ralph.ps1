# Ralph (PowerShell) - Long-running AI agent loop
# Usage: .\scripts\ralph\ralph.ps1 [-Tool <amp|claude>] [-MaxIterations <number>]

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("amp", "claude")]
    [string]$Tool = "amp",

    [Parameter(Mandatory=$false)]
    [int]$MaxIterations = 10
)

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Get-Location }

$PrdFile = Join-Path $ScriptDir "prd.json"
$ProgressFile = Join-Path $ScriptDir "progress.txt"
$ArchiveDir = Join-Path $ScriptDir "archive"
$LastBranchFile = Join-Path $ScriptDir ".last-branch"

# Helper for archiving
function Archive-PreviousRun {
    if ((Test-Path $PrdFile) -and (Test-Path $LastBranchFile)) {
        try {
            $PrdContent = Get-Content $PrdFile | ConvertFrom-Json
            $CurrentBranch = $PrdContent.branchName
        } catch {
            $CurrentBranch = ""
        }
        $LastBranch = Get-Content $LastBranchFile -ErrorAction SilentlyContinue
        
        if ($CurrentBranch -and $LastBranch -and ($CurrentBranch -ne $LastBranch)) {
            $Date = Get-Date -Format "yyyy-MM-dd"
            $FolderName = $LastBranch -replace "^ralph/", ""
            $ArchiveFolder = Join-Path $ArchiveDir "$Date-$FolderName"
            
            Write-Host "Archiving previous run: $LastBranch"
            if (-not (Test-Path $ArchiveFolder)) { New-Item -ItemType Directory -Path $ArchiveFolder -Force | Out-Null }
            
            if (Test-Path $PrdFile) { Copy-Item $PrdFile $ArchiveFolder -Force }
            if (Test-Path $ProgressFile) { Copy-Item $ProgressFile $ArchiveFolder -Force }
            Write-Host "   Archived to: $ArchiveFolder"
            
            # Reset progress file
            $Header = "# Ralph Progress Log`nStarted: $(Get-Date)`n---`n"
            Set-Content -Path $ProgressFile -Value $Header
        }
    }
}

# Archive if needed
Archive-PreviousRun

# Track current branch
if (Test-Path $PrdFile) {
    try {
        $PrdContent = Get-Content $PrdFile | ConvertFrom-Json
        $CurrentBranch = $PrdContent.branchName
        if ($CurrentBranch) {
            Set-Content -Path $LastBranchFile -Value $CurrentBranch
        }
    } catch {}
}

# Initialize progress if missing
if (-not (Test-Path $ProgressFile)) {
    $Header = "# Ralph Progress Log`nStarted: $(Get-Date)`n---`n"
    Set-Content -Path $ProgressFile -Value $Header
}

Write-Host "Starting Ralph - Tool: $Tool - Max iterations: $MaxIterations"

for ($i = 1; $i -le $MaxIterations; $i++) {
    Write-Host "`n==============================================================="
    Write-Host "  Ralph Iteration $i of $MaxIterations ($Tool)"
    Write-Host "==============================================================="

    if ($Tool -eq "amp") {
        # Note: Amp might need redirection or specific handling on Windows
        $Prompt = Get-Content (Join-Path $ScriptDir "prompt.md") -Raw
        $Output = $Prompt | amp --dangerously-allow-all 2>&1
        Write-Host $Output
    } else {
        # Claude Code
        $Prompt = Get-Content (Join-Path $ScriptDir "CLAUDE.md") -Raw
        # Passing input via stdin. In PS this might be tricky if claude expects an interactive TTY.
        # But we use --dangerously-skip-permissions --print as in the original script.
        $Output = $Prompt | claude --dangerously-skip-permissions --print 2>&1
        Write-Host $Output
    }

    if ($Output -match "<promise>COMPLETE</promise>") {
        Write-Host "`nRalph completed all tasks!"
        Write-Host "Completed at iteration $i of $MaxIterations"
        exit 0
    }

    Write-Host "Iteration $i complete. Continuing..."
    Start-Sleep -Seconds 2
}

Write-Host "`nRalph reached max iterations ($MaxIterations) without completing all tasks."
Write-Host "Check $ProgressFile for status."
exit 1
