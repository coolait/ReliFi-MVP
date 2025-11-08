# Backup .env File Script
# This script creates a timestamped backup of your .env file
# Run this periodically to protect against accidental deletion

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $projectRoot "client\.env"
$backupDir = Join-Path $env:USERPROFILE "Documents\ReliFi-Env-Backups"

# Create backup directory if it doesn't exist
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Write-Host "✅ Created backup directory: $backupDir" -ForegroundColor Green
}

# Check if .env file exists
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: .env file not found at $envFile" -ForegroundColor Red
    Write-Host "   Make sure you're running this from the project root." -ForegroundColor Yellow
    exit 1
}

# Create timestamped backup
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
$backupFile = Join-Path $backupDir ".env.backup-$timestamp"

try {
    Copy-Item $envFile $backupFile
    Write-Host "✅ .env file backed up successfully!" -ForegroundColor Green
    Write-Host "   Backup location: $backupFile" -ForegroundColor Cyan
    
    # List recent backups
    $recentBackups = Get-ChildItem $backupDir -Filter ".env.backup-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    Write-Host "`n📋 Recent backups:" -ForegroundColor Yellow
    foreach ($backup in $recentBackups) {
        Write-Host "   - $($backup.Name) ($($backup.LastWriteTime))" -ForegroundColor Gray
    }
    
    # Keep only last 10 backups
    $allBackups = Get-ChildItem $backupDir -Filter ".env.backup-*" | Sort-Object LastWriteTime -Descending
    if ($allBackups.Count -gt 10) {
        $oldBackups = $allBackups | Select-Object -Skip 10
        foreach ($oldBackup in $oldBackups) {
            Remove-Item $oldBackup.FullName -Force
            Write-Host "   🗑️  Removed old backup: $($oldBackup.Name)" -ForegroundColor DarkGray
        }
    }
} catch {
    Write-Host "❌ Error creating backup: $_" -ForegroundColor Red
    exit 1
}

