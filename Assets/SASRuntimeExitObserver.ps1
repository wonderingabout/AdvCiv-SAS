# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The game cannot publish reliably after an access violation, abort or forced termination.
# Added after live Python edits left RUNNING status behind despite a Windows-reported native crash; this is process-exit observation, not a Python/XML reload workaround.
# DLL/AI crashes are covered when they terminate the attached process too; errors that leave it alive are not process exits, and the exit code does not name the faulty function.
# Launched only by enabled runtime diagnostics, this same-user observer acquires the exact process before waiting without polling.
# No elevation, game commands, Python imports or changes to live gameplay are involved. Launch success alone does not prove attachment; policy restrictions or an early exit can prevent observation. (GPT-6.1-Sol) -->
param(
    [Parameter(Mandatory=$true)][string]$StatusPath,
    [Parameter(Mandatory=$true)][int]$TargetProcessId,
    [Parameter(Mandatory=$true)][string]$ProcessStartUtc,
    [Parameter(Mandatory=$true)][int]$RecorderRevision
)

$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$evidencePath = Join-Path ([System.IO.Path]::GetDirectoryName($StatusPath)) ('SASRuntimeExit_' + $ProcessStartUtc + '_' + $TargetProcessId + '.json')

# <!-- custom: Publish a small independent receipt/final record atomically, even if Civ4 died while rewriting its current JSON.
# WAITING proves handle acquisition; EXITED carries the authoritative process result. A blocked snapshot or a newer game must not erase this run's separate exit evidence. (GPT-6.1-Sol) -->
function Write-SASRuntimeExitEvidence($data) {
    $temporary = $evidencePath + '.' + $PID + '.tmp'
    try {
        [System.IO.File]::WriteAllText($temporary, ($data | ConvertTo-Json -Depth 8) + "`r`n", $utf8)
        for ($attempt = 0; $attempt -lt 10; $attempt++) {
            try {
                if ([System.IO.File]::Exists($evidencePath)) {
                    [System.IO.File]::Replace($temporary, $evidencePath, [System.Management.Automation.Language.NullString]::Value)
                } else {
                    [System.IO.File]::Move($temporary, $evidencePath)
                }
                return
            } catch {
                # <!-- custom: A concurrent observer can create the same receipt between Exists and Move, and a reader can briefly deny replacement. Retry the atomic operation, not the process observation. (GPT-6.1-Sol) -->
                if ($attempt -eq 9) { throw }
                Start-Sleep -Milliseconds 100
            }
        }
    } catch {
        [Console]::Error.WriteLine($_.Exception.Message)
    } finally {
        if ([System.IO.File]::Exists($temporary)) { [System.IO.File]::Delete($temporary) }
    }
}

try {
    $target = [System.Diagnostics.Process]::GetProcessById($TargetProcessId)
    $null = $target.Handle
    if ($target.StartTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ') -ne $ProcessStartUtc) {
        exit 2
    }
    # <!-- custom: Force acquisition now so ExitCode remains available after the target disappears; PID reuse cannot redirect an already-open process handle. (GPT-6.1-Sol) -->
    $evidence = [ordered]@{
        revision = $RecorderRevision
        processId = $TargetProcessId
        processStartUtc = $ProcessStartUtc
        observerProcessId = $PID
        observerState = 'WAITING'
        attachedUtc = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss.fffZ')
    }
    Write-SASRuntimeExitEvidence $evidence
    $target.WaitForExit()
    $exitCode = $target.ExitCode
    $exitedUtc = $target.ExitTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ')
} catch {
    # <!-- custom: Without an attached handle, neither an exit code nor a crash can be established. Leave the snapshot alone rather than inventing a successful observation. (GPT-6.1-Sol) -->
    exit 3
} finally {
    if ($null -ne $target) { $target.Dispose() }
}

$observedUtc = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss.fffZ')
$codeHex = '0x' + ([BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$exitCode), 0)).ToString('X8')
$evidence.observerState = 'EXITED'
$evidence.recordedUtc = $observedUtc
$evidence.processExitedUtc = $exitedUtc
$evidence.exitCode = $exitCode
$evidence.exitCodeHex = $codeHex
$evidence.outcome = $(if ($exitCode -eq 0) { 'ZERO_EXIT_CODE' } else { 'NONZERO_EXIT_CODE' })
Write-SASRuntimeExitEvidence $evidence
$stream = $null
try {
    # <!-- custom: Deny writers/deletion while checking identity and replacing the snapshot through the same handle.
    # A newly launched game either published first (identity mismatch below), or its write fails/retries while this brief lock is held; it cannot have its newer snapshot silently overwritten. (GPT-6.1-Sol) -->
    for ($attempt = 0; $attempt -lt 10; $attempt++) {
        try {
            $stream = [System.IO.File]::Open($StatusPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::Read)
            break
        } catch [System.IO.IOException] {
            if (-not [System.IO.File]::Exists($StatusPath)) { exit 0 }
            if ($attempt -eq 9) { throw }
            Start-Sleep -Milliseconds 100
        }
    }
    $reader = New-Object System.IO.StreamReader($stream, $utf8, $true, 4096, $true)
    try { $status = $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
    if ($status.processId -ne $TargetProcessId -or $status.processStartUtc -ne $ProcessStartUtc) { exit 0 }
    if ($status.PSObject.Properties['exitObservation']) { exit 0 }

    $observation = [ordered]@{
        observer = 'WINDOWS_PROCESS_HANDLE'
        recordedUtc = $observedUtc
        processExitedUtc = $exitedUtc
        exitCode = $exitCode
        exitCodeHex = $codeHex
        outcome = $(if ($exitCode -eq 0) { 'ZERO_EXIT_CODE' } else { 'NONZERO_EXIT_CODE' })
    }
    # <!-- custom: A nonzero exit is evidence, not a diagnosis: access violations, aborts and external termination can all end a process.
    # Preserve the game's last observed turn/activity and source identity instead of claiming that a Python error or the latest user action caused the exit. (GPT-6.1-Sol) -->
    $historyState = 'ROOT_UNAVAILABLE'
    $unterminatedHistoryTail = $false
    if ($status.historyAtCurrentRoot -eq 1 -and [System.IO.Path]::GetFileName([string]$status.historyFilename) -eq $status.historyFilename -and $status.historyFilename -match '^SASRuntimeHistory_.*\.jsonl$') {
        $historyPath = Join-Path ([System.IO.Path]::GetDirectoryName($StatusPath)) $status.historyFilename
        $row = [ordered]@{
            record = 'process_exit'
            revision = $status.revision
            run = $ProcessStartUtc + '_' + $TargetProcessId
            processId = $TargetProcessId
            recordedUtc = $observedUtc
            processExitedUtc = $exitedUtc
            exitCode = $exitCode
            exitCodeHex = $codeHex
            outcome = $observation.outcome
            lastInProcessUpdatedUtc = $status.updatedUtc
            lastActivity = $status.activity
            sessionSerial = $status.sessionSerial
            gameTurn = $status.gameTurn
        }
        $history = $null
        try {
            $history = [System.IO.File]::Open($historyPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::Read)
            $originalLength = $history.Length
            $null = $history.Seek(0, [System.IO.SeekOrigin]::End)
            # <!-- custom: Keep a crash-interrupted JSONL fragment separate from the final valid row; preserve its bytes as evidence rather than silently deleting them. (GPT-6.1-Sol) -->
            if ($originalLength -gt 0) {
                $null = $history.Seek(-1, [System.IO.SeekOrigin]::End)
                $lastByte = $history.ReadByte()
                if ($lastByte -ne 10) {
                    $unterminatedHistoryTail = $true
                    $history.WriteByte(10)
                }
            }
            $bytes = $utf8.GetBytes(($row | ConvertTo-Json -Compress -Depth 8) + "`r`n")
            $history.Write($bytes, 0, $bytes.Length)
            $history.Flush($true)
            $historyState = 'WRITTEN'
            $status.historyRowsWritten++
        } catch {
            # <!-- custom: A failed final append must not prevent the fixed snapshot from reporting process exit; expose the gap and roll back our own partial bytes when possible. (GPT-6.1-Sol) -->
            $historyState = 'WRITE_FAILED'
            $status.historyWriteFailures++
            if ($null -ne $history) {
                try { $history.SetLength($originalLength) } catch { }
            }
        } finally {
            if ($null -ne $history) { $history.Dispose() }
        }
    }
    $observation.historyAppend = $historyState
    $observation.unterminatedHistoryTail = $unterminatedHistoryTail
    if ($exitCode -ne 0 -or $status.processState -ne 'EXITED_CLEANLY') { $status.processState = 'EXITED' }
    $status | Add-Member -NotePropertyName lastInProcessUpdatedUtc -NotePropertyValue $status.updatedUtc
    $status | Add-Member -NotePropertyName exitObservation -NotePropertyValue $observation
    $status.updatedUtc = $observedUtc
    $status.updateReason = 'PROCESS_EXIT_OBSERVED'
    $status.statusSerial++
    $bytes = $utf8.GetBytes(($status | ConvertTo-Json -Depth 16) + "`r`n")
    $stream.Position = 0
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.SetLength($bytes.Length)
    $stream.Flush($true)
} catch {
    [Console]::Error.WriteLine($_.Exception.ToString())
    exit 4
} finally {
    if ($null -ne $stream) { $stream.Dispose() }
}
