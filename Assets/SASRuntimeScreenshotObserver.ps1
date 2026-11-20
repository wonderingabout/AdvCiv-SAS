# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Runtime 14 observes confirmed screenshot-file creation externally because Civ4 exposes no reliable screenshot-completion callback to the supplied DLL/Python source.
# A Print Screen/key request is not evidence that an image was actually saved (KI#7 documents a window/monitor case where the key produces no file), while external capture tools can bypass game input entirely.
# FileSystemWatcher therefore records only future image files that actually appear/change in Civ4's user ScreenShots directory. Rows retain filename/time/file evidence plus a best-effort copy of the matching Runtime snapshot context; they do not claim which process wrote the image or that Runtime context was perfectly current at the capture instant.
# No image bytes are copied into diagnostic output, no screenshot request is injected, and the watcher performs no directory polling. (ChatGPT-5.6-Sol) -->
param(
    [Parameter(Mandatory=$true)][string]$StatusPath,
    [Parameter(Mandatory=$true)][int]$TargetProcessId,
    [Parameter(Mandatory=$true)][string]$ProcessStartUtc,
    [Parameter(Mandatory=$true)][int]$RecorderRevision,
    [string]$ScreenshotDirectory = ''
)

$ErrorActionPreference = 'Stop'
# <!-- custom: Reuse the shared external-observer host metadata so screenshot evidence identifies the PowerShell/CLR environment that performed file observation. (ChatGPT-5.6-Sol) -->
. (Join-Path $PSScriptRoot 'SASRuntimeObserverEnvironment.ps1')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$logDirectory = [System.IO.Path]::GetDirectoryName($StatusPath)
$runId = $ProcessStartUtc + '_' + $TargetProcessId
$statePath = Join-Path $logDirectory ('SASRuntimeScreenshotWatch_' + $runId + '.json')
$eventPath = Join-Path $logDirectory ('SASRuntimeScreenshots_' + $runId + '.jsonl')
$maxRows = 4096
$maxPendingPaths = 256
$maxFingerprintBytes = 64MB
$quietMilliseconds = 500
$drawingAvailable = $null
$eventPrefix = 'SASRuntimeScreenshotWatch.' + $PID + '.'

try {
    $ownership = New-Object System.IO.FileStream(($statePath + '.lock'), [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None, 1, [System.IO.FileOptions]::DeleteOnClose)
} catch [System.IO.IOException] {
    exit 0
}

function Get-SASScreenshotUtcNow() { return [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss.fffZ') }

function Write-SASScreenshotState($data) {
    $temporary = $statePath + '.' + $PID + '.tmp'
    try {
        [System.IO.File]::WriteAllText($temporary, ($data | ConvertTo-Json -Depth 8) + "`r`n", $utf8)
        for ($attempt = 0; $attempt -lt 10; $attempt++) {
            try {
                if ([System.IO.File]::Exists($statePath)) {
                    [System.IO.File]::Replace($temporary, $statePath, [System.Management.Automation.Language.NullString]::Value)
                } else {
                    [System.IO.File]::Move($temporary, $statePath)
                }
                return
            } catch {
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

function Get-SASScreenshotDirectory($target) {
    if (-not [string]::IsNullOrEmpty($ScreenshotDirectory)) {
        try { return [System.IO.Path]::GetFullPath($ScreenshotDirectory) } catch { return $null }
    }
    try {
        $exePath = $target.MainModule.FileName
        $exeDirectory = [System.IO.Path]::GetDirectoryName($exePath)
        $gameFolder = [System.IO.Path]::GetFileName($exeDirectory)
        $documents = [Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)
        if ([string]::IsNullOrEmpty($documents) -or [string]::IsNullOrEmpty($gameFolder)) { return $null }
        return Join-Path (Join-Path (Join-Path $documents 'My Games') $gameFolder) 'ScreenShots'
    } catch {
        return $null
    }
}

function Test-SASScreenshotFilename([string]$name) {
    if ([string]::IsNullOrEmpty($name)) { return $false }
    $extension = [System.IO.Path]::GetExtension($name)
    return @('.jpg', '.jpeg', '.png', '.bmp') -contains $extension.ToLowerInvariant()
}

function Get-SASRuntimeScreenshotContext([string]$observedUtc) {
    $context = [ordered]@{
        associationState = 'STATUS_MISSING'
        associationUncertainty = 'FILESYSTEM_CAPTURE_CONFIRMED_WRITER_AND_EXACT_SCREEN_NOT_OBSERVED'
        runtimeStatusUpdatedUtc = '-'
        runtimeStatusAgeMilliseconds = -1
        statusSerial = -1
        sessionSerial = -1
        sessionKind = '-'
        gameState = '-'
        activity = '-'
        gameTurn = -1
        elapsedGameTurns = -1
        activePlayer = -1
        autoplayActive = -1
        playerTurnPlayer = -1
        playerTurnTeam = -1
        playerTurnCivilization = -1
        playerTurnCivilizationType = '-'
        playerTurnControl = '-'
        playerTurnPhase = '-'
        playerTurnElapsedMilliseconds = -1
        worldBuilderMode = -1
        worldBuilderScreenVisible = -1
        civilopediaVisible = -1
        civilopediaContext = '-'
        buttonPopupAwaitingInteraction = -1
        buttonPopupType = '-'
        buttonPopupActivePlayer = -1
    }
    if (-not [System.IO.File]::Exists($StatusPath)) { return $context }
    try {
        $status = [System.IO.File]::ReadAllText($StatusPath, $utf8) | ConvertFrom-Json
    } catch {
        $context.associationState = 'STATUS_UNREADABLE'
        return $context
    }
    if ($status.processId -ne $TargetProcessId -or $status.processStartUtc -ne $ProcessStartUtc) {
        $context.associationState = 'STATUS_IDENTITY_MISMATCH'
        return $context
    }
    $context.associationState = 'MATCHED_PROCESS_STATUS_CONTEXT_MAY_BE_STALE'
    if ($status.PSObject.Properties['updatedUtc']) { $context.runtimeStatusUpdatedUtc = [string]$status.updatedUtc }
    if ($context.runtimeStatusUpdatedUtc -ne '-') {
        try {
            $observed = [DateTime]::ParseExact($observedUtc, 'yyyyMMddTHHmmss.fffZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal)
            $updated = [DateTime]::ParseExact($context.runtimeStatusUpdatedUtc, 'yyyyMMddTHHmmss.fffZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal)
            $context.runtimeStatusAgeMilliseconds = [Int64]([Math]::Abs(($observed - $updated).TotalMilliseconds))
        } catch { }
    }
    $copyFields = @(
        'statusSerial', 'sessionSerial', 'sessionKind', 'gameState', 'activity', 'gameTurn', 'elapsedGameTurns', 'activePlayer', 'autoplayActive',
        'playerTurnPlayer', 'playerTurnTeam', 'playerTurnCivilization', 'playerTurnCivilizationType', 'playerTurnControl', 'playerTurnPhase', 'playerTurnElapsedMilliseconds',
        'worldBuilderMode', 'worldBuilderScreenVisible', 'civilopediaVisible', 'civilopediaContext', 'buttonPopupAwaitingInteraction', 'buttonPopupType', 'buttonPopupActivePlayer'
    )
    foreach ($field in $copyFields) {
        if ($status.PSObject.Properties[$field]) { $context[$field] = $status.$field }
    }
    return $context
}

# <!-- custom: A quiet notification burst is not proof that a screenshot writer finished. Open without write/delete sharing before reading metadata or hashing, so they describe one stable file; a busy writer gets bounded retries and explicit UNREADABLE evidence instead of a misleading hash/size pair. (GPT-6.1-Sol) -->
function Get-SASScreenshotFileEvidence([string]$path) {
    for ($attempt = 0; $attempt -lt 8; $attempt++) {
        if (-not [System.IO.File]::Exists($path)) { return $null }
        try {
            $stream = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
            try {
                $file = New-Object System.IO.FileInfo($path)
                $size = [Int64]$file.Length
                $creationUtc = $file.CreationTimeUtc.ToString('yyyyMMddTHHmmss.fffZ')
                $lastWriteUtc = $file.LastWriteTimeUtc.ToString('yyyyMMddTHHmmss.fffZ')
                $fingerprint = '-'
                $fingerprintStatus = 'SKIPPED_TOO_LARGE'
                if ($size -le $maxFingerprintBytes) {
                    $sha = [System.Security.Cryptography.SHA256]::Create()
                    try { $hash = $sha.ComputeHash($stream) } finally { $sha.Dispose() }
                    $fingerprint = ([BitConverter]::ToString($hash)).Replace('-', '')
                    $fingerprintStatus = 'AVAILABLE'
                }
                # <!-- custom: Read image dimensions for UI-scale comparisons without logging image contents. Load System.Drawing only on the first bounded image read; unavailable/invalid formats remain explicit instead of preventing metadata capture. (GPT-6.1-Sol) -->
                $width = -1
                $height = -1
                $dimensionsStatus = 'SKIPPED_TOO_LARGE'
                if ($size -le $maxFingerprintBytes) {
                    if ($null -eq $script:drawingAvailable) {
                        try { Add-Type -AssemblyName System.Drawing; $script:drawingAvailable = $true } catch { $script:drawingAvailable = $false }
                    }
                    $dimensionsStatus = 'READER_UNAVAILABLE'
                    if ($script:drawingAvailable) {
                        $image = $null
                        try {
                            $stream.Position = 0
                            $image = [System.Drawing.Image]::FromStream($stream, $false, $false)
                            $width = $image.Width
                            $height = $image.Height
                            $dimensionsStatus = 'AVAILABLE'
                        } catch {
                            $dimensionsStatus = 'UNREADABLE_IMAGE'
                        } finally {
                            if ($null -ne $image) { $image.Dispose() }
                        }
                    }
                }
                return [ordered]@{
                    imageWidth = $width
                    imageHeight = $height
                    dimensionsStatus = $dimensionsStatus
                    sizeBytes = $size
                    creationUtc = $creationUtc
                    lastWriteUtc = $lastWriteUtc
                    fingerprintAlgorithm = 'SHA256'
                    fingerprint = $fingerprint
                    fingerprintStatus = $fingerprintStatus
                }
            } finally { $stream.Dispose() }
        } catch {
            if ($attempt -eq 7) { return [ordered]@{ imageWidth = -1; imageHeight = -1; dimensionsStatus = 'FILE_UNREADABLE'; sizeBytes = -1; creationUtc = '-'; lastWriteUtc = '-'; fingerprintAlgorithm = 'SHA256'; fingerprint = '-'; fingerprintStatus = 'UNREADABLE' } }
            Start-Sleep -Milliseconds 100
        }
    }
    return $null
}

$state = [ordered]@{
    revision = $RecorderRevision
    processId = $TargetProcessId
    processStartUtc = $ProcessStartUtc
    observerProcessId = $PID
    observerState = 'STARTING'
    startedUtc = Get-SASScreenshotUtcNow
    environment = Get-SASRuntimeObserverEnvironment
    screenshotDirectoryKind = 'CIV4_USER_SCREENSHOTS'
    nativeFilenamePattern = 'Civ4ScreenShot<sequence>.JPG'
    eventFilename = [System.IO.Path]::GetFileName($eventPath)
    filesRecorded = 0
    rawEventsObserved = 0
    rawEventsCoalesced = 0
    ignoredEvents = 0
    rowsDropped = 0
    writeFailures = 0
    watcherErrors = 0
    pendingFiles = 0
    lastScreenshotFilename = '-'
    lastScreenshotObservedUtc = '-'
}
Write-SASScreenshotState $state

$target = $null
$watcher = $null
$registrations = @()
$writer = $null
$pending = @{}
$processExited = $false
$stateDirty = $false

function Add-SASScreenshotPending([string]$path, [string]$action, [string]$observedUtc) {
    $name = [System.IO.Path]::GetFileName($path)
    if (-not (Test-SASScreenshotFilename $name)) { $state.ignoredEvents++; $script:stateDirty = $true; return }
    $state.rawEventsObserved++
    $script:stateDirty = $true
    if (-not $pending.ContainsKey($path)) {
        if ($pending.Count -ge $maxPendingPaths) { $state.rowsDropped++; return }
        $pending[$path] = [ordered]@{
            path = $path
            filename = $name
            firstObservedUtc = $observedUtc
            lastObservedUtc = $observedUtc
            eventCount = 0
            actions = New-Object System.Collections.ArrayList
            context = Get-SASRuntimeScreenshotContext $observedUtc
        }
    }
    $item = $pending[$path]
    $item.lastObservedUtc = $observedUtc
    $item.eventCount++
    if (-not $item.actions.Contains($action)) { [void]$item.actions.Add($action) }
}

function Write-SASScreenshotPendingRow($item) {
    if ($state.filesRecorded -ge $maxRows) { $state.rowsDropped++; return }
    $file = Get-SASScreenshotFileEvidence $item.path
    if ($null -eq $file) { $state.ignoredEvents++; return }
    $nativePattern = [regex]::IsMatch($item.filename, '^Civ4ScreenShot[0-9]+\.jpg$', [Text.RegularExpressions.RegexOptions]::IgnoreCase)
    $row = [ordered]@{
        record = 'screenshot_file_observed'
        revision = $RecorderRevision
        run = $runId
        recordedUtc = Get-SASScreenshotUtcNow
        firstObservedUtc = $item.firstObservedUtc
        lastObservedUtc = $item.lastObservedUtc
        filename = $item.filename
        nativeCiv4FilenamePattern = $(if ($nativePattern) { 1 } else { 0 })
        writerIdentity = 'NOT_OBSERVED'
        captureRequestObserved = 0
        eventCount = $item.eventCount
        actionsObserved = @($item.actions)
        imageWidth = $file.imageWidth
        imageHeight = $file.imageHeight
        dimensionsStatus = $file.dimensionsStatus
        sizeBytes = $file.sizeBytes
        fileCreationUtc = $file.creationUtc
        fileLastWriteUtc = $file.lastWriteUtc
        fingerprintAlgorithm = $file.fingerprintAlgorithm
        fingerprint = $file.fingerprint
        fingerprintStatus = $file.fingerprintStatus
        associationState = $item.context.associationState
        associationUncertainty = $item.context.associationUncertainty
        runtimeStatusUpdatedUtc = $item.context.runtimeStatusUpdatedUtc
        runtimeStatusAgeMilliseconds = $item.context.runtimeStatusAgeMilliseconds
        statusSerial = $item.context.statusSerial
        sessionSerial = $item.context.sessionSerial
        sessionKind = $item.context.sessionKind
        gameState = $item.context.gameState
        activity = $item.context.activity
        gameTurn = $item.context.gameTurn
        elapsedGameTurns = $item.context.elapsedGameTurns
        activePlayer = $item.context.activePlayer
        autoplayActive = $item.context.autoplayActive
        playerTurnPlayer = $item.context.playerTurnPlayer
        playerTurnTeam = $item.context.playerTurnTeam
        playerTurnCivilization = $item.context.playerTurnCivilization
        playerTurnCivilizationType = $item.context.playerTurnCivilizationType
        playerTurnControl = $item.context.playerTurnControl
        playerTurnPhase = $item.context.playerTurnPhase
        playerTurnElapsedMilliseconds = $item.context.playerTurnElapsedMilliseconds
        worldBuilderMode = $item.context.worldBuilderMode
        worldBuilderScreenVisible = $item.context.worldBuilderScreenVisible
        civilopediaVisible = $item.context.civilopediaVisible
        civilopediaContext = $item.context.civilopediaContext
        buttonPopupAwaitingInteraction = $item.context.buttonPopupAwaitingInteraction
        buttonPopupType = $item.context.buttonPopupType
        buttonPopupActivePlayer = $item.context.buttonPopupActivePlayer
    }
    try {
        $writer.WriteLine(($row | ConvertTo-Json -Depth 6 -Compress))
        $writer.Flush()
        $state.filesRecorded++
        if ($item.eventCount -gt 1) { $state.rawEventsCoalesced += ($item.eventCount - 1) }
        $state.lastScreenshotFilename = $item.filename
        $state.lastScreenshotObservedUtc = $row.recordedUtc
        $script:stateDirty = $true
    } catch {
        $state.writeFailures++
        $script:stateDirty = $true
    }
}

function Flush-SASScreenshotPending([bool]$force) {
    $now = [DateTime]::UtcNow
    foreach ($key in @($pending.Keys)) {
        $item = $pending[$key]
        $last = [DateTime]::ParseExact($item.lastObservedUtc, 'yyyyMMddTHHmmss.fffZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal)
        if ($force -or ($now - $last).TotalMilliseconds -ge $quietMilliseconds) {
            Write-SASScreenshotPendingRow $item
            $pending.Remove($key)
            $script:stateDirty = $true
        }
    }
    if ($state.pendingFiles -ne $pending.Count) { $state.pendingFiles = $pending.Count; $script:stateDirty = $true }
}

try {
    $target = [System.Diagnostics.Process]::GetProcessById($TargetProcessId)
    $null = $target.Handle
    if ($target.StartTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ') -ne $ProcessStartUtc) { exit 2 }
    $screenshotDirectory = Get-SASScreenshotDirectory $target
    if ([string]::IsNullOrEmpty($screenshotDirectory) -or -not [System.IO.Directory]::Exists($screenshotDirectory)) {
        $state.observerState = 'UNAVAILABLE'
        $state.error = 'SCREENSHOT_DIRECTORY_MISSING'
        $state.endedUtc = Get-SASScreenshotUtcNow
        Write-SASScreenshotState $state
        exit 3
    }

    $target.EnableRaisingEvents = $true
    $registrations += Register-ObjectEvent -InputObject $target -EventName Exited -SourceIdentifier ($eventPrefix + 'ProcessExit')
    if ($target.HasExited) { $processExited = $true }

    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $screenshotDirectory
    $watcher.Filter = '*'
    $watcher.IncludeSubdirectories = $false
    $watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::Size -bor [System.IO.NotifyFilters]::CreationTime
    $watcher.InternalBufferSize = 16384
    foreach ($name in @('Changed', 'Created', 'Renamed', 'Error')) {
        $registrations += Register-ObjectEvent -InputObject $watcher -EventName $name -SourceIdentifier ($eventPrefix + $name)
    }
    $watcher.EnableRaisingEvents = $true

    $stream = [System.IO.File]::Open($eventPath, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
    $writer = New-Object System.IO.StreamWriter($stream, $utf8)
    $writer.AutoFlush = $true
    $state.observerState = 'WATCHING'
    $state.attachedUtc = Get-SASScreenshotUtcNow
    Write-SASScreenshotState $state
    $stateDirty = $false

    while (-not $processExited) {
        $event = Wait-Event -Timeout 1
        if ($null -ne $event) {
            do {
                $identifier = $event.SourceIdentifier
                if ($identifier -eq ($eventPrefix + 'ProcessExit')) {
                    $processExited = $true
                } elseif ($identifier.EndsWith('.Error')) {
                    $state.watcherErrors++
                    $stateDirty = $true
                } else {
                    $args = $event.SourceEventArgs
                    $path = $args.FullPath
                    if ($args -is [System.IO.RenamedEventArgs]) { $path = $args.FullPath }
                    Add-SASScreenshotPending $path ([string]$args.ChangeType).ToUpperInvariant() (Get-SASScreenshotUtcNow)
                }
                Remove-Event -EventIdentifier $event.EventIdentifier -ErrorAction SilentlyContinue
                $event = Get-Event | Where-Object { $_.SourceIdentifier.StartsWith($eventPrefix, [StringComparison]::OrdinalIgnoreCase) } | Select-Object -First 1
            } while ($null -ne $event)
        }
        Flush-SASScreenshotPending $false
        if ($stateDirty) { Write-SASScreenshotState $state; $stateDirty = $false }
    }
    Flush-SASScreenshotPending $true
    $target.WaitForExit()
    $state.observerState = 'EXITED'
    $state.processExitedUtc = $target.ExitTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ')
    $state.endedUtc = Get-SASScreenshotUtcNow
    Write-SASScreenshotState $state
} catch {
    $state.observerState = 'UNAVAILABLE'
    $state.error = $_.Exception.GetType().Name
    $state.endedUtc = Get-SASScreenshotUtcNow
    Write-SASScreenshotState $state
    exit 4
} finally {
    foreach ($registration in $registrations) { Unregister-Event -SubscriptionId $registration.Id -ErrorAction SilentlyContinue }
    Get-Event | Where-Object { $_.SourceIdentifier.StartsWith($eventPrefix, [StringComparison]::OrdinalIgnoreCase) } | Remove-Event -ErrorAction SilentlyContinue
    if ($null -ne $watcher) { $watcher.Dispose() }
    if ($null -ne $writer) { $writer.Dispose() }
    if ($null -ne $target) { $target.Dispose() }
    if ($null -ne $ownership) { $ownership.Dispose() }
}
