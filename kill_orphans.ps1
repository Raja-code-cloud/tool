# Kill stuck/orphan processes from dead agent terminal sessions.
# Preserves: user IDE terminals (89, 533), auto-sync (71296), active pytest with progress.

$toKill = @(
    18376   # stuck vitest shell (742466.txt) - hung 9+ min with no output
    11544   # orphan vitest node worker
    12524   # orphan pytest (release tests, parent session dead)
    16164   # orphan pytest from dead git status session
    20580   # orphan git-remote-https from completed session
    11564   # orphan chrome from completed Stop-Process session
    20056   # orphan AppVShNotify from completed npm update
    7112    # orphan smartscreen from completed pytest session
    18704   # orphan wermgr from completed Get-ChildItem session
    20792   # orphan sh from completed session
)

# Also kill child node processes of stuck vitest
$vitestChildren = Get-CimInstance Win32_Process |
    Where-Object { $_.ParentProcessId -eq 18376 -or ($_.CommandLine -like '*vitest*' -and $_.ParentProcessId -notin @(13152, 18832, 2264)) } |
    Select-Object -ExpandProperty ProcessId

$allKill = ($toKill + $vitestChildren) | Sort-Object -Unique

$killed = @()
$skipped = @()

foreach ($procId in $allKill) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $proc) {
        $skipped += "$procId (already dead)"
        continue
    }
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue).CommandLine
    # Safety: never kill Cursor IDE or user shell terminals
    if ($cmd -like '*cursor*resources*' -or $procId -in @(13152, 18832, 2264, 4184, 15376)) {
        $skipped += "$procId ($($proc.ProcessName)) - protected"
        continue
    }
    try {
        Stop-Process -Id $procId -Force -ErrorAction Stop
        $killed += "$procId ($($proc.ProcessName))"
    } catch {
        $skipped += "$procId - failed: $($_.Exception.Message)"
    }
}

Write-Host 'KILLED:'
$killed | ForEach-Object { Write-Host "  $_" }
Write-Host ''
Write-Host 'SKIPPED:'
$skipped | ForEach-Object { Write-Host "  $_" }

# Summary of remaining active agent shells
Write-Host ''
Write-Host 'REMAINING ACTIVE SHELLS:'
$termDir = 'C:\Users\Administrator\.cursor\projects\c-Users-Administrator-Documents-Tool\terminals'
Get-ChildItem $termDir -Filter '*.txt' | ForEach-Object {
    $c = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($c -and ($c -notmatch 'exit_code:')) {
        if ($c -match '(?m)^pid:\s*(\d+)') {
            $spid = [int]$matches[1]
            if (Get-Process -Id $spid -ErrorAction SilentlyContinue) {
                $cmd = if ($c -match '(?m)^command:\s*(.+)$') { $matches[1].Trim().Substring(0, [Math]::Min(80, $matches[1].Trim().Length)) } else { '(interactive)' }
                Write-Host "  $($_.Name) pid=$spid $cmd"
            }
        }
    }
}
