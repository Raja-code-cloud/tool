$toolRoot = 'C:\Users\Administrator\Documents\Tool'
$termDir = 'C:\Users\Administrator\.cursor\projects\c-Users-Administrator-Documents-Tool\terminals'

# Collect terminal session PIDs and their state
$sessions = @{}
Get-ChildItem $termDir -Filter '*.txt' | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return }
    $shellPid = if ($content -match '(?m)^pid:\s*(\d+)') { [int]$matches[1] } else { $null }
    if (-not $shellPid) { return }
    $active = ($content -notmatch 'exit_code:')
    $command = if ($content -match '(?m)^command:\s*(.+)$') { $matches[1].Trim() } else { '' }
    $sessions[$shellPid] = [PSCustomObject]@{
        File = $_.Name
        Active = $active
        Command = $command
        ShellAlive = [bool](Get-Process -Id $shellPid -ErrorAction SilentlyContinue)
    }
}

Write-Host '=== STUCK ACTIVE SESSIONS (shell dead but marked active) ==='
$sessions.GetEnumerator() | Where-Object { $_.Value.Active -and -not $_.Value.ShellAlive } |
    ForEach-Object { Write-Host "$($_.Value.File) pid=$($_.Key) DEAD" }

Write-Host ''
Write-Host '=== ACTIVE SESSIONS WITH LIVE SHELL ==='
$sessions.GetEnumerator() | Where-Object { $_.Value.Active -and $_.Value.ShellAlive } |
    ForEach-Object {
        $s = $_.Value
        Write-Host "$($s.File) pid=$($_.Key)"
        Write-Host "  cmd: $($s.Command.Substring(0, [Math]::Min(120, $s.Command.Length)))"
    }

Write-Host ''
Write-Host '=== ORPHAN CANDIDATES (Tool-related, parent shell dead or not in sessions) ==='
$aliveSessionPids = @($sessions.Keys)
$candidates = Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -and (
            $_.CommandLine -like "*$toolRoot*" -or
            $_.Name -in @('node.exe', 'python.exe', 'pytest.exe', 'git.exe', 'git-remote-https.exe')
        )
    } |
    ForEach-Object {
        $parentAlive = [bool](Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue)
        $parentIsSession = $aliveSessionPids -contains $_.ParentProcessId
        $isOrphan = -not $parentAlive -or (-not $parentIsSession -and $_.ParentProcessId -ne 0)
        if ($isOrphan -or ($_.ProcessId -in $aliveSessionPids)) {
            [PSCustomObject]@{
                PID = $_.ProcessId
                PPID = $_.ParentProcessId
                Name = $_.Name
                ParentAlive = $parentAlive
                ParentIsSession = $parentIsSession
                Orphan = $isOrphan
                CMD = $_.CommandLine.Substring(0, [Math]::Min(150, $_.CommandLine.Length))
            }
        }
    }

$candidates | Sort-Object @{Expression='Orphan';Descending=$true}, Name |
    Format-Table -AutoSize PID, PPID, Name, Orphan, ParentAlive, CMD
