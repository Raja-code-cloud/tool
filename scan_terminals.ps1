$dir = 'C:\Users\Administrator\.cursor\projects\c-Users-Administrator-Documents-Tool\terminals'
$results = @()

Get-ChildItem $dir -Filter '*.txt' | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return }

    $meta = @{
        file = $_.Name
        active = ($content -notmatch 'exit_code:')
        pid = $null
        cwd = $null
        command = $null
        started = $null
        running_ms = $null
        proc_alive = $false
        proc_name = $null
        cpu = $null
        mem_mb = $null
    }

    foreach ($line in ($content -split "`n" | Select-Object -First 20)) {
        if ($line -match '^pid:\s*(.+)$') { $meta.pid = $matches[1].Trim() }
        if ($line -match '^cwd:\s*(.+)$') { $meta.cwd = $matches[1].Trim() }
        if ($line -match '^command:\s*(.+)$') { $meta.command = $matches[1].Trim() }
        if ($line -match '^started_at:\s*(.+)$') { $meta.started = $matches[1].Trim() }
        if ($line -match '^running_for_ms:\s*(.+)$') { $meta.running_ms = [int]$matches[1].Trim() }
    }

    if ($meta.pid -match '^\d+$') {
        $proc = Get-Process -Id ([int]$meta.pid) -ErrorAction SilentlyContinue
        if ($proc) {
            $meta.proc_alive = $true
            $meta.proc_name = $proc.ProcessName
            $meta.cpu = [math]::Round($proc.CPU, 2)
            $meta.mem_mb = [math]::Round($proc.WorkingSet64 / 1MB, 1)
        }
    }

    if ($meta.active -or $meta.proc_alive) {
        $results += [PSCustomObject]$meta
    }
}

Write-Host "=== ACTIVE / ALIVE TERMINAL SESSIONS ==="
$results | Sort-Object @{Expression='active';Descending=$true}, @{Expression='running_ms';Descending=$true} |
    Format-Table -AutoSize file, active, proc_alive, pid, proc_name, cpu, mem_mb, running_ms, command

Write-Host ""
Write-Host "Active (no exit_code): $(($results | Where-Object { $_.active }).Count)"
Write-Host "Alive PIDs: $(($results | Where-Object { $_.proc_alive }).Count)"
Write-Host "Zombie metadata (active but dead PID): $(($results | Where-Object { $_.active -and -not $_.proc_alive }).Count)"

# Export for killing
$results | Where-Object { $_.proc_alive } | Export-Csv -Path 'C:\Users\Administrator\Documents\Tool\alive_terminals.csv' -NoTypeInformation
