# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Optional Runtime 12 source observation records live mod-source/configuration disk edits without tree polling or claiming that Civ4 reloaded them.
# The observer is a separate same-user PowerShell process because Python/XML can be edited while the game is blocked or crashing; FileSystemWatcher covers Python/XML, PrivateMaps scripts/scenarios, Resource themes, mod Settings and the root mod INI. Notifications describe disk edits, not which files the engine actually uses.
# Bursts for one path are coalesced after a short quiet period, then the final on-disk size/SHA-256 is sampled once. Paths are mod-relative, output rows/pending paths have explicit limits, and no file contents are copied.
# C++ edits are deliberately outside this live watcher because changing source does not replace the loaded DLL. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
param(
    [Parameter(Mandatory=$true)][string]$StatusPath,
    [Parameter(Mandatory=$true)][int]$TargetProcessId,
    [Parameter(Mandatory=$true)][string]$ProcessStartUtc,
    [Parameter(Mandatory=$true)][int]$RecorderRevision,
    [string]$WatchRoot = ''
)

$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
if ([string]::IsNullOrEmpty($WatchRoot)) { $WatchRoot = $PSScriptRoot }
$WatchRoot = [System.IO.Path]::GetFullPath($WatchRoot).TrimEnd('\', '/')
# <!-- custom: Share startup-only host metadata with the exit observer; dot-sourcing defines the function without starting either observer. (GPT-6.1-Sol) -->
. (Join-Path $PSScriptRoot 'SASRuntimeObserverEnvironment.ps1')
$modRoot = [System.IO.Path]::GetDirectoryName($WatchRoot)
$logDirectory = [System.IO.Path]::GetDirectoryName($StatusPath)
$runId = $ProcessStartUtc + '_' + $TargetProcessId
$statePath = Join-Path $logDirectory ('SASRuntimeSourceWatch_' + $runId + '.json')
$eventPath = Join-Path $logDirectory ('SASRuntimeSourceChanges_' + $runId + '.jsonl')
$maxRows = 4096
$maxPendingPaths = 1024
$maxFingerprintBytes = 16MB
$quietMilliseconds = 750
$eventPrefix = 'SASRuntimeSourceWatch.' + $PID + '.'

# <!-- custom: Duplicate source observers for one run/root would double-count save bursts. A delete-on-close lock gives exactly one owner while allowing root migrations to have independent observers. (ChatGPT-5.6-Sol) -->
try {
    $ownership = New-Object System.IO.FileStream(($statePath + '.lock'), [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None, 1, [System.IO.FileOptions]::DeleteOnClose)
} catch [System.IO.IOException] {
    exit 0
}

function Write-SASSourceWatchState($data) {
    $temporary = $statePath + '.' + $PID + '.tmp'
    try {
        [System.IO.File]::WriteAllText($temporary, ($data | ConvertTo-Json -Depth 6) + "`r`n", $utf8)
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

function Get-SASUtcNow() { return [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss.fffZ') }

# <!-- custom: Paths were Assets-relative in the Python/XML-only draft; use the mod root so themes, maps and the root INI share one unambiguous journal namespace. (GPT-6.1-Sol) -->
function Get-SASRelativeSourcePath([string]$fullPath) {
    if ([string]::IsNullOrEmpty($fullPath)) { return $null }
    try { $full = [System.IO.Path]::GetFullPath($fullPath) } catch { return $null }
    $prefix = $modRoot + [System.IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { return $null }
    return $full.Substring($prefix.Length).Replace('\', '/')
}

function Test-SASWatchedSourcePath([string]$relativePath) {
    if ([string]::IsNullOrEmpty($relativePath)) { return $false }
    return $relativePath -imatch '^(Assets/Python/.*\.py|Assets/(XML|Config)/.*\.xml|PrivateMaps/.*\.(py|CivBeyondSwordWBSave|CivWarlordsWBSave|Civ4WorldBuilderSave)|Resource/.*\.thm|Settings/.*\.(ini|xml|txt)|[^/]+\.ini)$'
}

function Get-SASFileEvidence([string]$relativePath) {
    $local = $relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $path = Join-Path $modRoot $local
    if (-not [System.IO.File]::Exists($path)) {
        return [ordered]@{ finalState = 'ABSENT'; sizeBytes = -1; lastWriteUtc = '-'; fingerprintAlgorithm = 'SHA256'; fingerprint = '-'; fingerprintStatus = 'NOT_PRESENT' }
    }
    try {
        $file = New-Object System.IO.FileInfo($path)
        $size = [Int64]$file.Length
        $lastWrite = $file.LastWriteTimeUtc.ToString('yyyyMMddTHHmmss.fffZ')
        if ($size -gt $maxFingerprintBytes) {
            return [ordered]@{ finalState = 'PRESENT'; sizeBytes = $size; lastWriteUtc = $lastWrite; fingerprintAlgorithm = 'SHA256'; fingerprint = '-'; fingerprintStatus = 'SKIPPED_TOO_LARGE' }
        }
        $stream = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
        try {
            $sha = [System.Security.Cryptography.SHA256]::Create()
            try { $hash = $sha.ComputeHash($stream) } finally { $sha.Dispose() }
        } finally { $stream.Dispose() }
        $fingerprint = ([BitConverter]::ToString($hash)).Replace('-', '')
        return [ordered]@{ finalState = 'PRESENT'; sizeBytes = $size; lastWriteUtc = $lastWrite; fingerprintAlgorithm = 'SHA256'; fingerprint = $fingerprint; fingerprintStatus = 'AVAILABLE' }
    } catch {
        return [ordered]@{ finalState = 'PRESENT'; sizeBytes = -1; lastWriteUtc = '-'; fingerprintAlgorithm = 'SHA256'; fingerprint = '-'; fingerprintStatus = 'UNREADABLE' }
    }
}

$state = [ordered]@{
    revision = $RecorderRevision
    processId = $TargetProcessId
    processStartUtc = $ProcessStartUtc
    observerProcessId = $PID
    observerState = 'STARTING'
    startedUtc = Get-SASUtcNow
    environment = Get-SASRuntimeObserverEnvironment
    watchedScopes = @('Assets/Python/**/*.py', 'Assets/XML/**/*.xml', 'Assets/Config/**/*.xml', 'PrivateMaps/*.py and scenarios (recursive)', 'Resource/**/*.thm', 'Settings/**/*.{ini,xml,txt}', '*.ini (mod root only)')
    eventFilename = [System.IO.Path]::GetFileName($eventPath)
    rawEventsObserved = 0
    burstsWritten = 0
    rawEventsCoalesced = 0
    rowsDropped = 0
    writeFailures = 0
    watcherErrors = 0
    pendingPaths = 0
    lastRecordedUtc = '-'
}
Write-SASSourceWatchState $state

$target = $null
$writer = $null
$watchers = @()
$registrations = @()
$pending = @{}
$processExited = $false
$stateDirty = $false

function Add-SASPendingEvent([string]$relativePath, [string]$action, [string]$oldRelativePath, [string]$observedUtc) {
    if (-not (Test-SASWatchedSourcePath $relativePath)) { return }
    $state.rawEventsObserved++
    $script:stateDirty = $true
    if (-not $pending.ContainsKey($relativePath)) {
        if ($pending.Count -ge $maxPendingPaths) { $state.rowsDropped++; return }
        $pending[$relativePath] = [ordered]@{
            path = $relativePath
            firstObservedUtc = $observedUtc
            lastObservedUtc = $observedUtc
            eventCount = 0
            actions = New-Object System.Collections.ArrayList
            oldPaths = New-Object System.Collections.ArrayList
        }
    }
    $item = $pending[$relativePath]
    $item.lastObservedUtc = $observedUtc
    $item.eventCount++
    if (-not $item.actions.Contains($action)) { [void]$item.actions.Add($action) }
    if (-not [string]::IsNullOrEmpty($oldRelativePath) -and $oldRelativePath -ne $relativePath -and -not $item.oldPaths.Contains($oldRelativePath)) { [void]$item.oldPaths.Add($oldRelativePath) }
}

function Write-SASPendingRow($item) {
    if ($state.burstsWritten -ge $maxRows) { $state.rowsDropped++; return }
    $file = Get-SASFileEvidence $item.path
    $row = [ordered]@{
        record = 'source_file_change'
        revision = $RecorderRevision
        run = $runId
        recordedUtc = Get-SASUtcNow
        firstObservedUtc = $item.firstObservedUtc
        lastObservedUtc = $item.lastObservedUtc
        path = $item.path
        eventCount = $item.eventCount
        actionsObserved = @($item.actions)
        oldPathsObserved = @($item.oldPaths)
        finalState = $file.finalState
        sizeBytes = $file.sizeBytes
        lastWriteUtc = $file.lastWriteUtc
        fingerprintAlgorithm = $file.fingerprintAlgorithm
        fingerprint = $file.fingerprint
        fingerprintStatus = $file.fingerprintStatus
        engineReloadState = 'NOT_OBSERVED'
    }
    try {
        $writer.WriteLine(($row | ConvertTo-Json -Depth 5 -Compress))
        $writer.Flush()
        $state.burstsWritten++
        if ($item.eventCount -gt 1) { $state.rawEventsCoalesced += ($item.eventCount - 1) }
        $state.lastRecordedUtc = $row.recordedUtc
        $script:stateDirty = $true
    } catch {
        $state.writeFailures++
        $script:stateDirty = $true
    }
}

function Flush-SASPending([bool]$force) {
    $now = [DateTime]::UtcNow
    foreach ($key in @($pending.Keys)) {
        $item = $pending[$key]
        $last = [DateTime]::ParseExact($item.lastObservedUtc, 'yyyyMMddTHHmmss.fffZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal)
        if ($force -or ($now - $last).TotalMilliseconds -ge $quietMilliseconds) {
            Write-SASPendingRow $item
            $pending.Remove($key)
            $script:stateDirty = $true
        }
    }
    if ($state.pendingPaths -ne $pending.Count) { $state.pendingPaths = $pending.Count; $script:stateDirty = $true }
}

try {
    $target = [System.Diagnostics.Process]::GetProcessById($TargetProcessId)
    $null = $target.Handle
    if ($target.StartTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ') -ne $ProcessStartUtc) { exit 2 }
    $target.EnableRaisingEvents = $true
    $registrations += Register-ObjectEvent -InputObject $target -EventName Exited -SourceIdentifier ($eventPrefix + 'ProcessExit')
    # <!-- custom: Exit can occur after EnableRaisingEvents but before the subscriber is attached; one post-subscription state check closes that lost-event window without periodic process polling. (GPT-6.1-Sol) -->
    if ($target.HasExited) { $processExited = $true }

    # <!-- custom: Use narrow watched directories instead of subscribing to the whole repository (Git/generated files can be noisy).
    # Root INI observation is nonrecursive; new subdirectories inside existing watched roots are included. User Logs are excluded to avoid observing our own continuous output. (GPT-6.1-Sol) -->
    $definitions = @(
        @((Join-Path $WatchRoot 'Python'), '*.py', 'Python', $true),
        @((Join-Path $WatchRoot 'XML'), '*.xml', 'XML', $true),
        @((Join-Path $WatchRoot 'Config'), '*.xml', 'Config', $true),
        @((Join-Path $modRoot 'PrivateMaps'), '*', 'PrivateMaps', $true),
        @((Join-Path $modRoot 'Resource'), '*.thm', 'Resource', $true),
        @((Join-Path $modRoot 'Settings'), '*', 'Settings', $true),
        @($modRoot, '*.ini', 'ModIni', $false)
    )
    foreach ($definition in $definitions) {
        if (-not [System.IO.Directory]::Exists($definition[0])) { continue }
        $watcher = New-Object System.IO.FileSystemWatcher
        $watcher.Path = $definition[0]
        $watcher.Filter = $definition[1]
        $watcher.IncludeSubdirectories = $definition[3]
        $watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::Size -bor [System.IO.NotifyFilters]::CreationTime
        $watcher.InternalBufferSize = 32768
        $watchers += $watcher
        foreach ($name in @('Changed', 'Created', 'Deleted', 'Renamed', 'Error')) {
            $registrations += Register-ObjectEvent -InputObject $watcher -EventName $name -SourceIdentifier ($eventPrefix + $definition[2] + '.' + $name)
        }
        $watcher.EnableRaisingEvents = $true
    }
    if ($watchers.Count -eq 0) { throw 'No mod watch roots are available' }

    $stream = [System.IO.File]::Open($eventPath, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
    $writer = New-Object System.IO.StreamWriter($stream, $utf8)
    $writer.AutoFlush = $true
    $state.observerState = 'WATCHING'
    $state.attachedUtc = Get-SASUtcNow
    Write-SASSourceWatchState $state
    $stateDirty = $false

    # <!-- custom: Wait-Event wakes for Windows notifications; its timeout only services pending-save debounce. It never scans the source tree, and idle cycles do not rewrite state. (GPT-6.1-Sol) -->
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
                    $relative = Get-SASRelativeSourcePath $args.FullPath
                    $oldRelative = $null
                    if ($args -is [System.IO.RenamedEventArgs]) { $oldRelative = Get-SASRelativeSourcePath $args.OldFullPath }
                    if (-not (Test-SASWatchedSourcePath $relative) -and (Test-SASWatchedSourcePath $oldRelative)) { $relative = $oldRelative }
                    Add-SASPendingEvent $relative ([string]$args.ChangeType).ToUpperInvariant() $oldRelative (Get-SASUtcNow)
                }
                Remove-Event -EventIdentifier $event.EventIdentifier -ErrorAction SilentlyContinue
                $event = Get-Event | Where-Object { $_.SourceIdentifier.StartsWith($eventPrefix, [StringComparison]::OrdinalIgnoreCase) } | Select-Object -First 1
            } while ($null -ne $event)
        }
        Flush-SASPending $false
        if ($stateDirty) { Write-SASSourceWatchState $state; $stateDirty = $false }
    }
    Flush-SASPending $true
    $target.WaitForExit()
    $state.observerState = 'EXITED'
    $state.processExitedUtc = $target.ExitTime.ToUniversalTime().ToString('yyyyMMddTHHmmss.fffZ')
    $state.endedUtc = Get-SASUtcNow
    Write-SASSourceWatchState $state
} catch {
    $state.observerState = 'UNAVAILABLE'
    $state.error = $_.Exception.GetType().Name
    $state.endedUtc = Get-SASUtcNow
    Write-SASSourceWatchState $state
    exit 3
} finally {
    foreach ($registration in $registrations) { Unregister-Event -SubscriptionId $registration.Id -ErrorAction SilentlyContinue }
    Get-Event | Where-Object { $_.SourceIdentifier.StartsWith($eventPrefix, [StringComparison]::OrdinalIgnoreCase) } | Remove-Event -ErrorAction SilentlyContinue
    foreach ($watcher in $watchers) { $watcher.Dispose() }
    if ($null -ne $writer) { $writer.Dispose() }
    if ($null -ne $target) { $target.Dispose() }
    if ($null -ne $ownership) { $ownership.Dispose() }
}
