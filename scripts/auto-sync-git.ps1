param(
    [int]$IntervalMinutes = 5,
    [string]$Branch = "main"
)

$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LogFile = Join-Path $RepoRoot "scripts\auto-sync-git.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

Set-Location $RepoRoot
$env:HUSKY = "0"

Write-Log "Auto-sync started (every $IntervalMinutes min, branch: $Branch)"

while ($true) {
    try {
        $status = git status --porcelain 2>&1 | Where-Object { $_ -notmatch 'cloud-content-hub-infra' }

        if ($LASTEXITCODE -ne 0) {
            Write-Log "ERROR: git status failed"
        }
        elseif ($status) {
            Write-Log "Changes detected - committing..."

            git add -A -- . ":(exclude)cloud-content-hub-infra" 2>&1 | Out-Null
            $commitMessage = "Auto-sync: update workspace $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            git commit -m $commitMessage 2>&1 | ForEach-Object { Write-Log $_ }

            if ($LASTEXITCODE -eq 0) {
                Write-Log "Pushing to origin/$Branch..."
                git push origin $Branch 2>&1 | ForEach-Object { Write-Log $_ }

                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Push successful."
                }
                else {
                    Write-Log "ERROR: Push failed."
                }
            }
            else {
                Write-Log "ERROR: Commit failed."
            }
        }
        else {
            Write-Log "No changes detected."
        }
    }
    catch {
        Write-Log ("ERROR: " + $_.Exception.Message)
    }

    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
