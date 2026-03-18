# ProdMaster AI -- SessionStart hook runner (PowerShell)
# Called by run-hook.cmd. Reads memory files and writes context to stdout.
param([string]$Event = "session-start")

$ErrorActionPreference = "SilentlyContinue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pluginRoot = Split-Path -Parent $scriptDir
$memDir = Join-Path $pluginRoot "memory"
$templatePath = Join-Path $scriptDir "session-start.md"

if (-not (Test-Path $templatePath)) {
    Write-Output "## ProdMaster AI`n*Memory not yet initialized.*"
    exit 0
}

function Get-Section {
    param([string]$FilePath, [string]$Section)
    if (-not (Test-Path $FilePath)) { return "(none yet)" }
    $lines = Get-Content $FilePath -ErrorAction SilentlyContinue
    if (-not $lines) { return "(none yet)" }
    $capture = $false
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $lines) {
        if ($line -match "^## $Section\s*$") { $capture = $true; continue }
        if ($capture -and $line -match "^## ") { break }
        if ($capture -and $line.Trim() -and $line -notmatch "^<!--") { $out.Add($line) }
    }
    $recent = if ($out.Count -le 5) { $out } else { $out | Select-Object -Last 5 }
    if ($recent.Count -eq 0) { return "(none yet)" }
    return ($recent -join "`n")
}

function Get-LastField {
    param([string]$FilePath, [string]$Field, [int]$Count)
    if (-not (Test-Path $FilePath)) { return "(none yet)" }
    $matches = Select-String -Path $FilePath -Pattern "^$Field" -ErrorAction SilentlyContinue
    if (-not $matches) { return "(none yet)" }
    $last = $matches | Select-Object -Last $Count
    return ($last | ForEach-Object { "- " + ($_.Line -replace "^$Field", "") }) -join "`n"
}

function Get-OpenGaps {
    param([string]$FilePath)
    if (-not (Test-Path $FilePath)) { return "(none yet)" }
    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return "(none yet)" }
    $out = [System.Collections.Generic.List[string]]::new()
    $lines = $content -split "`n"
    $foundOpen = $false
    foreach ($line in $lines) {
        if ($line -match "^status: open") { $foundOpen = $true; continue }
        if ($foundOpen -and $line -match "^pattern:") {
            $out.Add("- " + ($line -replace "^pattern:\s*", ""))
            $foundOpen = $false
        }
        if ($line -match "^---") { $foundOpen = $false }
    }
    if ($out.Count -eq 0) { return "(none yet)" }
    return ($out | Select-Object -First 5) -join "`n"
}

$af = Get-Section (Join-Path $memDir "project-context.md") "Active Features"
$tp = Get-LastField (Join-Path $memDir "patterns.md") "pattern: " 5
$og = Get-OpenGaps (Join-Path $memDir "skill-gaps.md")
$re = Get-LastField (Join-Path $memDir "evolution-log.md") "change_summary: " 3

$tpl = Get-Content $templatePath -Raw
$result = $tpl `
    -replace '\{\{active_features\}\}', $af `
    -replace '\{\{top_patterns\}\}', $tp `
    -replace '\{\{open_gaps\}\}', $og `
    -replace '\{\{recent_evolutions\}\}', $re

Write-Output $result
exit 0
