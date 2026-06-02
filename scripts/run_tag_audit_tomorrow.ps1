# run_tag_audit_tomorrow.ps1
# Scheduled execution of youtube_tag_audit_bulk.py --execute
# Target: 2026-06-04 09:15 local time

$ROOT    = "C:\Users\petar\OneDrive\Desktop\izlet_sustav"
$SCRIPT  = "$ROOT\scripts\youtube_tag_audit_bulk.py"
$LOG_DIR = "$ROOT\logs"
$LOG     = "$LOG_DIR\youtube_tag_audit_20260604.log"

# Ensure logs/ exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
}

# Wait until 2026-06-04 09:15 local time
$target = [datetime]"2026-06-04 09:15:00"
$now    = Get-Date
if ($now -lt $target) {
    $wait = ($target - $now).TotalSeconds
    Write-Host "Waiting $([math]::Round($wait/60, 1)) minutes until $target..."
    Start-Sleep -Seconds ([int]$wait)
}

Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') — Starting youtube_tag_audit_bulk.py --execute"

# Run script, capture output to log and console
Set-Location $ROOT
$output = python scripts/youtube_tag_audit_bulk.py --execute 2>&1
$output | Out-File -FilePath $LOG -Encoding UTF8
$output | ForEach-Object { Write-Host $_ }

# Summary
$updated = ($output | Select-String "✓ Updated").Count
$errors  = ($output | Select-String "✗ Error").Count

Write-Host ""
Write-Host "──────────────────────────────────"
Write-Host "Log saved to: $LOG"
Write-Host "✓ Updated:    $updated"
Write-Host "✗ Errors:     $errors"
Write-Host "Done: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
