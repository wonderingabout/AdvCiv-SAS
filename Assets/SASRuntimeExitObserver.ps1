# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The game cannot publish reliably after an access violation, abort or forced termination.
# Added after live Python edits left RUNNING status behind despite a Windows-reported native crash; this is process-exit observation, not a Python/XML reload workaround.
# DLL/AI crashes are covered when they terminate the attached process too; a recognized fatal runtime dialog is now observed separately while the process remains alive, without pretending that the dialog identifies the faulty function.
# Launched only by enabled runtime diagnostics, this same-user observer acquires the exact process before waiting without polling.
# No elevation, game commands, Python imports or changes to live gameplay are involved. Launch success alone does not prove attachment; policy restrictions or an early exit can prevent observation. (GPT-6.1-Sol) -->
param(
    [Parameter(Mandatory=$true)][string]$StatusPath,
    [Parameter(Mandatory=$true)][int]$TargetProcessId,
    [Parameter(Mandatory=$true)][string]$ProcessStartUtc,
    [Parameter(Mandatory=$true)][int]$RecorderRevision,
    [int]$ScreenshotWatchOn = 0
)

$ErrorActionPreference = 'Stop'
# <!-- custom: The shared metadata definition records the actual PowerShell/CLR host once, independent of the native VC2003 DLL. (GPT-6.1-Sol) -->
. (Join-Path $PSScriptRoot 'SASRuntimeObserverEnvironment.ps1')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$evidencePath = Join-Path ([System.IO.Path]::GetDirectoryName($StatusPath)) ('SASRuntimeExit_' + $ProcessStartUtc + '_' + $TargetProcessId + '.json')
# <!-- custom: Only one observer may own a particular run/root's live receipt. Otherwise a later duplicate could overwrite a captured failure dialog with its empty startup state.
# Delete-on-close releases this transient lock even if the observer is killed; distinct CvAltRoot paths retain their independent observers. (GPT-6.1-Sol) -->
try {
    $observerOwnership = New-Object System.IO.FileStream(($evidencePath + '.lock'), [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None, 1, [System.IO.FileOptions]::DeleteOnClose)
} catch [System.IO.IOException] {
    exit 0
}

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
        environment = Get-SASRuntimeObserverEnvironment
        observerState = 'WAITING'
        attachedUtc = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss.fffZ')
    }
    Write-SASRuntimeExitEvidence $evidence
    # <!-- custom: Confirmed screenshot files need external filesystem observation too: a Print Screen request is not proof of a saved image, and external capture tools can bypass game input.
    # Launch the adjacent screenshot observer only after this exact process handle/start identity is confirmed. It writes its own bounded state/history files; this parent records launch/expected filenames but does not duplicate screenshot rows. (ChatGPT-5.6-Sol) -->
    $evidence.screenshotObserverState = 'DISABLED'
    $evidence.screenshotObserverProcessId = 0
    $evidence.screenshotObserverError = ''
    $evidence.screenshotObserverStateFilename = 'SASRuntimeScreenshotWatch_' + $ProcessStartUtc + '_' + $TargetProcessId + '.json'
    $evidence.screenshotObserverHistoryFilename = 'SASRuntimeScreenshots_' + $ProcessStartUtc + '_' + $TargetProcessId + '.jsonl'
    # <!-- custom: The native launcher passes its cached XML opt-in. Keep screenshot-off free of child launch/path checks and screenshot-file I/O; the ordinary exit observer remains independent. (GPT-6.1-Sol) -->
    if ($ScreenshotWatchOn -gt 0) {
        $evidence.screenshotObserverState = 'STARTING'
        try {
            $screenshotScript = Join-Path $PSScriptRoot 'SASRuntimeScreenshotObserver.ps1'
            if (-not [System.IO.File]::Exists($screenshotScript)) { throw 'SASRuntimeScreenshotObserver.ps1 is missing' }
            $powerShellPath = [System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
            $quotedScript = '"' + $screenshotScript + '"'
            $quotedStatus = '"' + $StatusPath + '"'
            $arguments = '-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ' + $quotedScript + ' -StatusPath ' + $quotedStatus + ' -TargetProcessId ' + $TargetProcessId + ' -ProcessStartUtc ' + $ProcessStartUtc + ' -RecorderRevision ' + $RecorderRevision
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = $powerShellPath
            $startInfo.Arguments = $arguments
            $startInfo.UseShellExecute = $false
            $startInfo.CreateNoWindow = $true
            $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
            $screenshotProcess = [System.Diagnostics.Process]::Start($startInfo)
            if ($null -eq $screenshotProcess) { throw 'Screenshot observer launch returned no process' }
            $evidence.screenshotObserverProcessId = $screenshotProcess.Id
            $evidence.screenshotObserverState = 'LAUNCHED'
            $screenshotProcess.Dispose()
        } catch {
            $evidence.screenshotObserverState = 'UNAVAILABLE'
            $evidence.screenshotObserverError = $_.Exception.Message
        }
    }
    Write-SASRuntimeExitEvidence $evidence
    # <!-- custom: A fatal runtime dialog can keep the process alive indefinitely, so process exit alone cannot explain a blocked game.
    # The companion uses a process-filtered WinEvent message loop and a blocking event queue, not periodic UI/game polling. Compilation or hook failure leaves the original process-exit wait available. (GPT-6.1-Sol) -->
    $evidence.dialogObserverState = 'STARTING'
    $evidence.dialogObserverErrorCode = 0
    $evidence.dialogObserverError = ''
    $evidence.dialogEventsDropped = 0
    $evidence.failureDialogCount = 0
    $evidence.failureDialog = $null
    $dialogObserver = $null
    # <!-- custom: Measure only Add-Type in this helper, not game startup; report failure too. Do not infer a C# compiler version from the CLR identifier. (GPT-6.1-Sol) -->
    $evidence.listenerCompilation = [ordered]@{ state = 'STARTING'; elapsedMilliseconds = $null }
    $compileTimer = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Add-Type -Path (Join-Path $PSScriptRoot 'SASRuntimeDialogObserver.cs')
        $compileTimer.Stop()
        $evidence.listenerCompilation.state = 'SUCCEEDED'
        $evidence.listenerCompilation.elapsedMilliseconds = $compileTimer.ElapsedMilliseconds
        $dialogObserver = New-Object SASRuntimeDialogObserver($target)
        while ($null -ne ($dialogEvent = $dialogObserver.TakeNext())) {
            if ($dialogEvent.MonitorReady) {
                $evidence.dialogObserverState = $(if ($dialogEvent.MonitorError -eq 0) { 'ACTIVE' } else { 'UNAVAILABLE' })
                $evidence.dialogObserverErrorCode = $dialogEvent.MonitorError
                $evidence.dialogObserverError = $(if ($dialogEvent.MonitorError -eq 0) { '' } else { 'WinEvent listener initialization failed' })
            } else {
                if ($dialogEvent.Visible) { $evidence.failureDialogCount++ }
                if (-not $evidence.Contains('firstFailureDialogObservedUtc')) {
                    $evidence.firstFailureDialogObservedUtc = $dialogEvent.FirstObservedUtc
                }
                $evidence.failureDialog = [ordered]@{
                    kind = $dialogEvent.Kind
                    visible = $dialogEvent.Visible
                    firstObservedUtc = $dialogEvent.FirstObservedUtc
                    observedUtc = $dialogEvent.ObservedUtc
                    windowHandle = $dialogEvent.WindowHandle
                    title = $dialogEvent.Title
                    text = $dialogEvent.Text
                }
            }
            $evidence.dialogEventsDropped = $dialogObserver.DroppedEvents
            Write-SASRuntimeExitEvidence $evidence
        }
        $evidence.dialogEventsDropped = $dialogObserver.DroppedEvents
        if ($evidence.dialogObserverState -eq 'STARTING') { $evidence.dialogObserverState = 'PROCESS_EXITED_BEFORE_READY' }
    } catch {
        if ($evidence.listenerCompilation.state -eq 'STARTING') {
            $compileTimer.Stop()
            $evidence.listenerCompilation.state = 'FAILED'
            $evidence.listenerCompilation.elapsedMilliseconds = $compileTimer.ElapsedMilliseconds
        }
        $evidence.dialogObserverState = 'UNAVAILABLE'
        $evidence.dialogObserverErrorCode = -1
        $evidence.dialogObserverError = $_.Exception.Message
        Write-SASRuntimeExitEvidence $evidence
    } finally {
        if ($null -ne $dialogObserver) { $dialogObserver.Dispose() }
    }
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
    if ($null -ne $evidence.failureDialog) {
        $observation.failureDialogKind = $evidence.failureDialog.kind
        $observation.firstFailureDialogObservedUtc = $evidence.firstFailureDialogObservedUtc
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
        # <!-- custom: Keep bounded first/latest dialog evidence live in the independent receipt, then attach its summary to the final history row after Civ4 exits.
        # This avoids concurrent writers in the game's JSONL file or changing native history counters while the game remains alive. (GPT-6.1-Sol) -->
        if ($null -ne $evidence.failureDialog) {
            $row.firstFailureDialogObservedUtc = $evidence.firstFailureDialogObservedUtc
            $row.failureDialogCount = $evidence.failureDialogCount
            $row.failureDialog = $evidence.failureDialog
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
    $observerOwnership.Dispose()
}
