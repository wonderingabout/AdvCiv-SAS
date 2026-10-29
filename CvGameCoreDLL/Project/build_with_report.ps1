# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Keep one current full log/JSON pair beside the DLL; automatic timestamped archives and a separate compact format added cleanup and duplicated evidence we rarely revisit.
# Git preserves deliberately shipped JSON reports; save a dated copy manually when a particular failed attempt matters. Failed builds must not label an older DLL as a successful new build. (GPT-6.1-Sol) -->
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Debug', 'Debug-opt', 'Release', 'Assert-fast', 'Profile-fast', 'Debug-fast', '_Release-fast', 'Final_Release-fast')]
    [string]$Configuration,
    [ValidateSet('BUILD', 'REBUILD', 'CLEAN')]
    [string]$Request = 'BUILD',
    [switch]$IdeBuild
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$target = $Configuration -replace '-fast$', '' -replace '^_', ''
$env:TARGET = $target
$env:SAS_BUILD_REQUEST = $Request
$started = [DateTime]::UtcNow
$timer = [Diagnostics.Stopwatch]::StartNew()
$outputDirectory = Join-Path $PSScriptRoot $target
[void][IO.Directory]::CreateDirectory($outputDirectory)
$logPath = Join-Path $outputDirectory 'AdvCiv.log'
$reportPath = Join-Path $outputDirectory 'CvGameCoreDLL.dll.build.json'
# <!-- custom: MSBuild already owns AdvCiv.log during an IDE build; writing it ourselves would compete with its live logger.
# Terminal builds own the same filename directly, so either entry point produces the current log without another duplicate. (GPT-6.1-Sol) -->
$writer = $null
if (-not $IdeBuild) {
    $writer = New-Object IO.StreamWriter($logPath, $false, (New-Object Text.UTF8Encoding($false)))
    $writer.AutoFlush = $true
}
$warnings = New-Object 'Collections.Generic.HashSet[string]'
$errors = New-Object 'Collections.Generic.HashSet[string]'

function Write-BuildLine([string]$Line) {
    if ($null -ne $writer) { $writer.WriteLine($Line) }
    Write-Output $Line
}

function Get-GitText([string[]]$Arguments) {
    $ErrorActionPreference = 'Continue'
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return 'UNAVAILABLE' }
    $result = & git @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) { return 'UNAVAILABLE' }
    return ($result -join "`n")
}

# <!-- custom: Record branch ancestry and staged/unstaged runtime-code patches independently so a build made on a reproducer/PR branch cannot be mistaken for a later main practical merely from rev-list count.
# This is a local provenance snapshot only: no fetch is attempted, and defaultRefSource says whether the locally known default came from a local branch or origin's tracking ref.
# Anchor counts/ancestry/staged patches to the captured SHAs rather than refs that may move during capture. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
function Get-SourceDiffState([switch]$Cached, [string]$BaseCommit = 'HEAD') {
    # <!-- custom: Git failures should mark optional provenance unavailable, not abort DLL compilation under the wrapper's Stop policy. (GPT-6.1-Sol) -->
    $ErrorActionPreference = 'Continue'
    $repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
    # <!-- custom: Keep build provenance aligned with ModName/SGR/runtime source identity, including shipped PowerShell/C# companions directly under Assets. (ChatGPT-5.6-Sol) -->
    $scope = @('CvGameCoreDLL', 'Assets/Config', 'Assets/Python', 'Assets/XML', 'Assets/*.ps1', 'Assets/*.cs', 'PrivateMaps')
    # <!-- custom: PowerShell unwraps a one-element if result to a string; splatting that scalar passed d/i/f/f as separate Git arguments and broke unstaged capture.
    # Keep both branches typed as string arrays. (GPT-6.1-Sol) -->
    [string[]]$prefix = if ($Cached) { @('diff', '--cached', $BaseCommit) } else { @('diff') }
    $temp = [IO.Path]::GetTempFileName()
    try {
        # <!-- custom: Read UTF-8 NUL-delimited paths so non-ASCII filenames are not mistaken for quoted octal paths.
        # The old --literal-pathspecs also disabled the Assets/*.ps1 and Assets/*.cs scope wildcards, silently omitting shipped companions.
        # Expand these fixed scope pathspecs normally; retain literal handling below for each discovered bracket/Unicode filename. (GPT-6.1-Sol) -->
        & git -C $repoRoot @prefix '--name-only' '-z' '--no-renames' ('--output=' + $temp) '--' @scope 2>$null
        if ($LASTEXITCODE -ne 0) { return [ordered]@{ available = $false; reason = 'GIT_DIFF_UNAVAILABLE' } }
        $names = [IO.File]::ReadAllText($temp, [Text.Encoding]::UTF8).Split([char[]]@([char]0), [StringSplitOptions]::RemoveEmptyEntries)
        & git -C $repoRoot @prefix '--binary' '--full-index' '--no-ext-diff' '--no-textconv' '--no-renames' '--no-color' ('--output=' + $temp) '--' @scope 2>$null
        if ($LASTEXITCODE -ne 0) { return [ordered]@{ available = $false; reason = 'GIT_DIFF_UNAVAILABLE' } }
        $whole = Get-BuildFileState $temp
        $files = @()
        foreach ($path in $names) {
            if ([string]::IsNullOrEmpty($path)) { continue }
            [IO.File]::WriteAllBytes($temp, [byte[]]@())
            & git --literal-pathspecs -C $repoRoot @prefix '--binary' '--full-index' '--no-ext-diff' '--no-textconv' '--no-renames' '--no-color' ('--output=' + $temp) '--' $path 2>$null
            if ($LASTEXITCODE -ne 0) { return [ordered]@{ available = $false; reason = 'PER_FILE_GIT_DIFF_UNAVAILABLE' } }
            $state = Get-BuildFileState $temp
            # <!-- custom: A file changed between name enumeration and patch capture must not become an empty patch reported as verified evidence. (GPT-6.1-Sol) -->
            if ($state.sizeBytes -eq 0) { return [ordered]@{ available = $false; reason = 'SOURCE_DIFF_CHANGED_DURING_CAPTURE' } }
            $files += [ordered]@{ path = $path; diffBytes = $state.sizeBytes; sha256 = $state.sha256 }
        }
        return [ordered]@{ available = $true; scope = 'TRACKED_RUNTIME_CODE_RULES'; diffBytes = $whole.sizeBytes; sha256 = $whole.sha256; fileCount = $files.Count; files = $files }
    }
    catch { return [ordered]@{ available = $false; reason = 'SOURCE_DIFF_CAPTURE_FAILED'; detail = $_.Exception.Message } }
    finally { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }
}

function Get-SourceProvenance {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return [ordered]@{ available = $false; reason = 'GIT_UNAVAILABLE' } }
    $commit = Get-GitText -Arguments @('rev-parse', 'HEAD')
    if ($commit -eq 'UNAVAILABLE') { return [ordered]@{ available = $false; reason = 'HEAD_UNAVAILABLE' } }
    $branch = Get-GitText -Arguments @('symbolic-ref', '--quiet', '--short', 'HEAD')
    $version = Get-GitText -Arguments @('rev-list', '--count', $commit)
    $shallow = Get-GitText -Arguments @('rev-parse', '--is-shallow-repository')
    $result = [ordered]@{
        available = $true
        commit = $commit
        branch = $branch
        version = if ($shallow -eq 'false') { $version } else { 'UNAVAILABLE' }
        history = if ($shallow -eq 'true') { 'SHALLOW' } elseif ($shallow -eq 'false') { 'FULL' } else { 'UNKNOWN' }
        defaultBranch = 'UNAVAILABLE'
        defaultCommit = 'UNAVAILABLE'
        defaultVersion = 'UNAVAILABLE'
        defaultRefSource = 'UNAVAILABLE'
        mergeBaseCommit = 'UNAVAILABLE'
        mergeBaseVersion = 'UNAVAILABLE'
        branchRelation = 'UNAVAILABLE'
        currentOnlyCommits = -1
        defaultOnlyCommits = -1
        stagedCodeRulesDiff = Get-SourceDiffState -Cached -BaseCommit $commit
        unstagedCodeRulesDiff = Get-SourceDiffState
    }
    if ($shallow -ne 'false') { return $result }
    $originHead = Get-GitText -Arguments @('symbolic-ref', '--quiet', 'refs/remotes/origin/HEAD')
    if ($originHead -notmatch '^refs/remotes/origin/(.+)$') { return $result }
    $defaultBranch = $Matches[1]
    $localRef = 'refs/heads/' + $defaultBranch
    $remoteRef = $originHead
    $defaultCommit = Get-GitText -Arguments @('rev-parse', '--verify', $localRef)
    if ($defaultCommit -ne 'UNAVAILABLE') {
        $defaultRef = $localRef
        $result.defaultRefSource = 'LOCAL_BRANCH'
    }
    else {
        $defaultCommit = Get-GitText -Arguments @('rev-parse', '--verify', $remoteRef)
        if ($defaultCommit -eq 'UNAVAILABLE') { return $result }
        $defaultRef = $remoteRef
        $result.defaultRefSource = 'REMOTE_TRACKING'
    }
    $result.defaultBranch = $defaultBranch
    $result.defaultCommit = $defaultCommit
    $result.defaultVersion = Get-GitText -Arguments @('rev-list', '--count', $defaultCommit)
    $result.mergeBaseCommit = Get-GitText -Arguments @('merge-base', $commit, $defaultCommit)
    if ($result.mergeBaseCommit -ne 'UNAVAILABLE') { $result.mergeBaseVersion = Get-GitText -Arguments @('rev-list', '--count', $result.mergeBaseCommit) }
    $counts = Get-GitText -Arguments @('rev-list', '--left-right', '--count', ($commit + '...' + $defaultCommit))
    if ($counts -match '^([0-9]+)\s+([0-9]+)$') {
        $result.currentOnlyCommits = [int]$Matches[1]
        $result.defaultOnlyCommits = [int]$Matches[2]
        if ($result.currentOnlyCommits -eq 0 -and $result.defaultOnlyCommits -eq 0) { $result.branchRelation = 'AT_DEFAULT' }
        elseif ($result.currentOnlyCommits -gt 0 -and $result.defaultOnlyCommits -eq 0) { $result.branchRelation = 'AHEAD_OF_DEFAULT' }
        elseif ($result.currentOnlyCommits -eq 0 -and $result.defaultOnlyCommits -gt 0) { $result.branchRelation = 'BEHIND_DEFAULT' }
        else { $result.branchRelation = 'DIVERGED' }
    }
    return $result
}

function Get-TempState {
    $directory = Join-Path $PSScriptRoot ('temp_files/' + $target)
    $files = @(Get-ChildItem -LiteralPath $directory -Recurse -File -ErrorAction SilentlyContinue)
    return [ordered]@{
        directoryPresent = (Test-Path -LiteralPath $directory)
        objectCount = @($files | Where-Object { $_.Extension -eq '.obj' }).Count
        incompleteMarkerCount = @($files | Where-Object { $_.Extension -eq '.@' }).Count
        pchPresent = (Test-Path -LiteralPath (Join-Path $directory 'CvGameCoreDLL.pch'))
        pdbPresent = (Test-Path -LiteralPath (Join-Path $directory 'CvGameCoreDLL.pdb'))
    }
}

# <!-- custom: Reuse the former DLL-only size/time/hash reader for source snapshots too, keeping byte-identity reporting consistent. (GPT-6.1-Sol) -->
function Get-BuildFileState([string]$Path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $file = Get-Item -LiteralPath $path
    # <!-- custom: The local legacy PowerShell has no Get-FileHash; use .NET SHA-256 so the VC2010 workflow needs no PowerShell upgrade. (GPT-6.1-Sol) -->
    $algorithm = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($path)
    try { $hash = [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '') }
    finally { $stream.Dispose(); $algorithm.Dispose() }
    return [ordered]@{
        sizeBytes = $file.Length
        modifiedUtc = $file.LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        sha256 = $hash
    }
}

function Get-DllState {
    return Get-BuildFileState (Join-Path $PSScriptRoot ($target + '/CvGameCoreDLL.dll'))
}

# <!-- custom: Exact source hashes remain provenance, but a comment added after a successful build must not imply that its DLL lacks a Python method.
# Capture the same literal .def names/targets inspected by the integration guard; strings/comments are tokenized first, and nested target expressions retain their complete token sequence.
# This describes registrations only, not arbitrary C++ implementation compatibility, and requires no Python installation on the build machine. (GPT-6.1-Sol) -->
function Get-PythonBindingRegistrations([string]$Text) {
    $pattern = '//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|''(?:\\.|[^''\\])*''|[A-Za-z_]\w*|[^\s]'
    $tokens = @([regex]::Matches($Text, $pattern, [Text.RegularExpressions.RegexOptions]::Singleline) |
        ForEach-Object { $_.Value } | Where-Object { -not ($_.StartsWith('//') -or $_.StartsWith('/*')) })
    $seen = New-Object 'Collections.Generic.HashSet[string]'
    for ($i = 0; $i -lt $tokens.Count - 5; $i++) {
        # <!-- custom: Global python::def registrations are DLL contracts too; mirror the integration guard so the UTC logging bridge enters build fingerprints alongside class methods. (GPT-6.1-Sol) -->
        $isMethod = $tokens[$i] -ceq '.'
        $isFunction = $i -ge 2 -and $tokens[$i - 2] -ceq 'python' -and $tokens[$i - 1] -ceq ':' -and $tokens[$i] -ceq ':'
        if (-not ($isMethod -or $isFunction) -or $tokens[$i + 1] -cne 'def' -or $tokens[$i + 2] -cne '(' -or
            -not $tokens[$i + 3].StartsWith('"') -or $tokens[$i + 4] -cne ',') { continue }
        $targetTokens = New-Object 'Collections.Generic.List[string]'
        $depth = 0
        for ($j = $i + 5; $j -lt $tokens.Count; $j++) {
            $token = $tokens[$j]
            if ($depth -eq 0 -and $token -in @(',', ')')) { break }
            $targetTokens.Add($token)
            if ($token -in @('(', '[', '<')) { $depth++ }
            elseif ($token -in @(')', ']', '>')) { $depth-- }
        }
        if ($targetTokens.Count -gt 0) {
            $name = $tokens[$i + 3].Substring(1, $tokens[$i + 3].Length - 2)
            $bindingTarget = $targetTokens -join ''
            if ($seen.Add($name + "`0" + $bindingTarget)) {
                [ordered]@{ name = $name; target = $bindingTarget }
            }
        }
    }
}

# <!-- custom: Store one compact fingerprint per interface file rather than duplicating hundreds of registrations in every report.
# Sort hex-encoded UTF-8 name/NUL/target records ordinally before hashing; this gives PowerShell and Python the same case-sensitive, locale-independent representation, including non-ASCII names. (GPT-6.1-Sol) -->
function Get-PythonBindingFingerprint([string]$Text) {
    [string[]]$records = @(Get-PythonBindingRegistrations $Text | ForEach-Object {
        [BitConverter]::ToString([Text.Encoding]::UTF8.GetBytes($_.name + "`0" + $_.target)).Replace('-', '')
    })
    [Array]::Sort($records, [StringComparer]::Ordinal)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($algorithm.ComputeHash([Text.Encoding]::ASCII.GetBytes(($records -join "`n")))).Replace('-', '')
    }
    finally { $algorithm.Dispose() }
}

# <!-- custom: Git status names changed paths but does not identify their bytes; sample local DLL sources and project/build configuration before and after each attempt.
# Exclude output trees and external toolchains/SDKs; this is a scoped filesystem snapshot, not proof of exactly which inputs each compiler invocation read. (GPT-6.1-Sol) -->
function Get-BuildInputSnapshot {
    $sourceRoot = Split-Path -Parent $PSScriptRoot
    $files = New-Object 'Collections.Generic.List[IO.FileInfo]'
    $directories = New-Object 'Collections.Generic.Queue[string]'
    $directories.Enqueue($sourceRoot)
    while ($directories.Count -gt 0) {
        $directory = $directories.Dequeue()
        foreach ($item in Get-ChildItem -LiteralPath $directory) {
            if ($item.PSIsContainer) {
                if ($item.FullName -ne $PSScriptRoot) { $directories.Enqueue($item.FullName) }
            }
            elseif ($item.Extension -in @('.cpp', '.h', '.inl')) { $files.Add($item) }
        }
    }
    foreach ($item in Get-ChildItem -LiteralPath $PSScriptRoot -File) {
        if ($item.Name -like 'Makefile*' -or $item.Extension -in @('.ps1', '.sln', '.vcxproj', '.props', '.targets', '.rc', '.def', '.h')) {
            $files.Add($item)
        }
    }
    $snapshot = @{}
    foreach ($file in $files) {
        $relativePath = 'CvGameCoreDLL/' + $file.FullName.Substring($sourceRoot.Length + 1).Replace('\', '/')
        $snapshot[$relativePath] = Get-BuildFileState $file.FullName
        if ($file.Name -clike '*Interface*.cpp') {
            $snapshot[$relativePath]['pythonBindingsSha256'] = Get-PythonBindingFingerprint ([IO.File]::ReadAllText($file.FullName))
        }
    }
    return $snapshot
}

# <!-- custom: A changed timestamp alone does not mean changed content; SHA-256 identifies exact bytes, including whitespace/line-ending edits.
# Timestamp-only entries retain the path and both observed UTC values; repeating identical sizes/hashes inflated reports after checkouts touched many files.
# Keep full before/after states for byte changes, including LF/CRLF differences; the initial manifest retains exact input hashes. (GPT-6.1-Sol) -->
function Get-BuildInputReport($Before, $After, [switch]$IncludeBefore) {
    $paths = @(@($Before.Keys) + @($After.Keys) | Sort-Object -Unique)
    foreach ($path in $paths) {
        $old = $Before[$path]
        $new = $After[$path]
        $change = 'UNCHANGED'
        if ($null -eq $old) { $change = 'ADDED' }
        elseif ($null -eq $new) { $change = 'REMOVED' }
        elseif ($old.sha256 -ne $new.sha256) { $change = 'CONTENT_CHANGED' }
        elseif ($old.modifiedUtc -ne $new.modifiedUtc) { $change = 'TIMESTAMP_ONLY' }
        if ($change -eq 'TIMESTAMP_ONLY') {
            [ordered]@{ path = $path; change = $change; beforeModifiedUtc = $old.modifiedUtc; afterModifiedUtc = $new.modifiedUtc }
        }
        elseif ($change -ne 'UNCHANGED') {
            $entry = [ordered]@{ path = $path; change = $change; after = $new }
            if ($IncludeBefore) { $entry['before'] = $old }
            $entry
        }
    }
}

# <!-- custom: Read the preceding report before replacing it; comparing its final source snapshot with this attempt's start exposes edits between builds even when HEAD did not change.
# Use only a completed Build/Rebuild with final measurements; an interrupted/Clean/older report without a manifest is explicitly unavailable, never an empty baseline that makes every file look added. (GPT-6.1-Sol) -->
function Get-PreviousBuildInputs([string]$Path) {
    $result = @{ available = $false; reason = 'NO_PREVIOUS_REPORT' }
    if (-not (Test-Path -LiteralPath $Path)) { return $result }
    try {
        # <!-- custom: JSON is UTF-8 even without a BOM; Windows PowerShell's default ANSI decoding otherwise corrupts non-ASCII paths/tool names during reconstruction. (GPT-6.1-Sol) -->
        $previous = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($previous.request -eq 'CLEAN' -or $previous.status -notin @('SUCCEEDED', 'FAILED') -or
            $null -eq $previous.buildInputsBefore -or $null -eq $previous.buildInputSummary -or $previous.buildInputsAfterError) {
            $result.reason = 'NO_COMPLETED_BUILD_SOURCE_SNAPSHOT'
            return $result
        }
        $snapshot = @{}
        foreach ($entry in $previous.buildInputsBefore) {
            $snapshot[$entry.path] = [ordered]@{ sizeBytes = $entry.sizeBytes; modifiedUtc = $entry.modifiedUtc; sha256 = $entry.sha256 }
        }
        foreach ($entry in $previous.buildInputChanges) {
            if ($entry.change -eq 'REMOVED') { $snapshot.Remove($entry.path) }
            # <!-- custom: Compact timestamp entries update the existing manifest state instead of replacing it with a missing `after` object.
            # Verify the prior timestamp so malformed evidence cannot silently invent a state; legacy reports retain their full `after` records and follow the original branch. (GPT-6.1-Sol) -->
            elseif ($entry.change -eq 'TIMESTAMP_ONLY' -and $null -ne $entry.afterModifiedUtc) {
                if (-not $snapshot.ContainsKey($entry.path) -or $snapshot[$entry.path].modifiedUtc -ne $entry.beforeModifiedUtc -or
                    [string]::IsNullOrEmpty([string]$entry.afterModifiedUtc)) { throw 'Invalid compact timestamp-only build input.' }
                $snapshot[$entry.path].modifiedUtc = $entry.afterModifiedUtc
            }
            else { $snapshot[$entry.path] = $entry.after }
        }
        if ($snapshot.Count -ne $previous.buildInputSummary.afterCount) { throw 'Previous source snapshot count mismatch.' }
        return @{ available = $true; snapshot = $snapshot; startedUtc = $previous.startedUtc; endedUtc = $previous.endedUtc;
            configuration = $previous.configuration; request = $previous.request; status = $previous.status; commit = $previous.commitAfter }
    }
    catch { $result.reason = 'UNREADABLE_PREVIOUS_REPORT'; return $result }
}

# <!-- custom: A VS2010 IDE can drive VC2003, and Makefile.user may select another toolchain; record expanded build commands rather than guessing from the IDE, folder name or first cl.exe on PATH.
# This optional build-time capture invokes only the no-build Makefile target. Executable resource versions describe the selected binaries, not C++ language-standard support or proof that a particular invocation consumed every input. (GPT-6.1-Sol) -->
function Get-BuildToolchain([string]$NMakePath = 'nmake') {
    $ErrorActionPreference = 'Continue'
    try {
        $lines = & $NMakePath /NOLOGO sas_toolchain_info 2>$null
        if ($LASTEXITCODE -ne 0) { return [ordered]@{ available = $false; reason = 'MAKEFILE_QUERY_FAILED' } }
        $values = @{}
        foreach ($line in $lines) {
            if ([string]$line -match '^SAS_BUILD_([A-Z]+)=(.*)$') { $values[$matches[1]] = $matches[2].Trim() }
        }
        foreach ($key in @('CC', 'CPP', 'LD', 'RC', 'TOOLKIT', 'PSDK')) {
            if (-not $values.ContainsKey($key)) { return [ordered]@{ available = $false; reason = 'INCOMPLETE_MAKEFILE_QUERY' } }
        }
        $tools = [ordered]@{}
        foreach ($pair in @(@('cCompiler', 'CC'), @('cppCompiler', 'CPP'), @('linker', 'LD'), @('resourceCompiler', 'RC'))) {
            $command = $values[$pair[1]]
            $tool = [ordered]@{ command = $command; available = $false }
            $executable = $command
            if ($command -match '^"([^\"]+)"(?:\s.*)?$') { $executable = $matches[1] }
            try {
                $resolved = Get-Command -Name $executable -CommandType Application -ErrorAction Stop
                $info = [Diagnostics.FileVersionInfo]::GetVersionInfo($resolved.Source)
                $tool.available = $true
                $tool.path = $resolved.Source
                $tool.fileVersion = $info.FileVersion
                $tool.productVersion = $info.ProductVersion
                $tool.productName = $info.ProductName
            } catch { $tool.reason = 'EXECUTABLE_UNAVAILABLE' }
            $tools[$pair[0]] = $tool
        }
        return [ordered]@{ available = $true; selection = 'MAKEFILE_EXPANSION'; toolkit = $values.TOOLKIT; platformSdk = $values.PSDK; tools = $tools }
    } catch { return [ordered]@{ available = $false; reason = 'TOOLCHAIN_CAPTURE_FAILED' } }
}

# <!-- custom: The explicit IDE switch identifies the wrapper entry path; ancestor executable evidence can further identify VCExpress/devenv/MSBuild or another caller without assuming a particular IDE version.
# Capture only a bounded parent chain and executable versions, not command lines. Environment hints can be stale, so they are not treated as proof of the launching application. Failure of optional provenance must not block a build. (GPT-6.1-Sol) -->
function Get-BuildInvocation([bool]$IdeRequested) {
    $context = [ordered]@{
        entryMode = $(if ($IdeRequested) { 'IDE_SWITCH' } else { 'DIRECT_WRAPPER' })
        powershellVersion = $PSVersionTable.PSVersion.ToString()
        powershellEdition = [string]$PSVersionTable.PSEdition
        clrVersion = [Environment]::Version.ToString()
        processBits = [IntPtr]::Size * 8
        ancestorState = 'UNAVAILABLE'
        ancestors = @()
    }
    try {
        $child = Get-CimInstance -ClassName Win32_Process -Filter ('ProcessId=' + $PID) -ErrorAction Stop
        $seen = @{}
        for ($depth = 0; $depth -lt 8 -and $null -ne $child -and $child.ParentProcessId -ne 0; $depth++) {
            $parentId = [int]$child.ParentProcessId
            if ($seen.ContainsKey($parentId)) { break }
            $seen[$parentId] = $true
            $parent = Get-CimInstance -ClassName Win32_Process -Filter ('ProcessId=' + $parentId) -ErrorAction Stop
            if ($null -eq $parent -or $parent.CreationDate -gt $child.CreationDate) { break }
            $entry = [ordered]@{ processId = $parentId; name = $parent.Name; path = $parent.ExecutablePath; fileVersion = $null; productVersion = $null }
            if (-not [string]::IsNullOrEmpty($parent.ExecutablePath)) {
                try {
                    $info = [Diagnostics.FileVersionInfo]::GetVersionInfo($parent.ExecutablePath)
                    $entry.fileVersion = $info.FileVersion
                    $entry.productVersion = $info.ProductVersion
                } catch { }
            }
            $context.ancestors += $entry
            $child = $parent
        }
        $context.ancestorState = 'OBSERVED'
    } catch {
        if ($context.ancestors.Count -gt 0) { $context.ancestorState = 'PARTIAL' }
    }
    return $context
}

# <!-- custom: JSON has no comment syntax; retain introductory copyright/purpose as ordinary metadata so reports remain valid JSON for CI. (GPT-6.1-Sol) -->
$report = [ordered]@{
    copyright = 'AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy); (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS root README.md)'
    purpose = 'Informational build report only: not read or required by Civilization IV or normal gameplay. Supports CI checks for committed DLL updates and investigation of build, runtime or AI issues alongside game logs.'
    configuration = $Configuration
    target = $target
    request = $Request
    startedUtc = $started.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    branch = Get-GitText -Arguments @('symbolic-ref', '--quiet', '--short', 'HEAD')
    commit = Get-GitText -Arguments @('rev-parse', 'HEAD')
    workingTreeStatus = Get-GitText -Arguments @('status', '--porcelain=v1', '--untracked-files=normal')
    invocation = Get-BuildInvocation -IdeRequested $IdeBuild.IsPresent
    toolchain = Get-BuildToolchain
    sourceProvenance = Get-SourceProvenance
    tempBefore = Get-TempState
    dllBefore = Get-DllState
    status = 'RUNNING'
    logFile = [IO.Path]::GetFileName($logPath)
    steps = @()
}
$previousBuild = Get-PreviousBuildInputs $reportPath
$inputsBefore = @{}
$exitCode = 1
try {
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
    $inputsBefore = Get-BuildInputSnapshot
    $report['buildInputsBefore'] = @($inputsBefore.Keys | Sort-Object | ForEach-Object {
        $state = $inputsBefore[$_]
        $entry = [ordered]@{ path = $_; sizeBytes = $state.sizeBytes; modifiedUtc = $state.modifiedUtc; sha256 = $state.sha256 }
        if ($state.Contains('pythonBindingsSha256')) { $entry['pythonBindingsSha256'] = $state.pythonBindingsSha256 }
        $entry
    })
    if ($previousBuild.available) {
        $sincePrevious = @(Get-BuildInputReport $previousBuild.snapshot $inputsBefore -IncludeBefore)
        $report['sincePreviousBuild'] = [ordered]@{
            available = $true; scope = 'PREVIOUS_BUILD_END_TO_CURRENT_BUILD_START'; previousStartedUtc = $previousBuild.startedUtc;
            previousEndedUtc = $previousBuild.endedUtc; previousConfiguration = $previousBuild.configuration;
            previousRequest = $previousBuild.request; previousStatus = $previousBuild.status; previousCommit = $previousBuild.commit;
            previousFileCount = $previousBuild.snapshot.Count; currentFileCount = $inputsBefore.Count; changedCount = $sincePrevious.Count; changes = $sincePrevious
        }
        Write-BuildLine ('Since previous completed build attempt ({0}, {1}): {2} source/project file changes (including timestamp-only changes).' -f $previousBuild.endedUtc, $previousBuild.status, $sincePrevious.Count)
    }
    else {
        $report['sincePreviousBuild'] = [ordered]@{ available = $false; reason = $previousBuild.reason }
        Write-BuildLine ('Since previous completed build attempt: unavailable ({0}).' -f $previousBuild.reason)
    }
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-BuildLine ('Build input snapshot: {0} local source/project files; external toolchain/SDK inputs excluded.' -f $inputsBefore.Count)
    Write-BuildLine ('Build report: ' + $reportPath)
    Write-BuildLine ('Started UTC: ' + $report.startedUtc)
    Write-BuildLine ('Configuration: {0}; request: {1}; branch: {2}; commit: {3}' -f $Configuration, $Request, $report.branch, $report.commit)
    Write-BuildLine ('Build invocation: ' + ($report.invocation | ConvertTo-Json -Depth 5 -Compress))
    Write-BuildLine ('Selected build toolchain: ' + ($report.toolchain | ConvertTo-Json -Depth 5 -Compress))
    Write-BuildLine ('Temporary artifacts before request: ' + ($report.tempBefore | ConvertTo-Json -Compress))
    Write-BuildLine ('Working-tree status relative to HEAD (staged + unstaged + untracked): ' + $report.workingTreeStatus)
    if ($Request -eq 'BUILD' -and ($report.tempBefore.objectCount -gt 0 -or $report.tempBefore.pchPresent -or $report.tempBefore.incompleteMarkerCount -gt 0)) {
        Write-BuildLine 'Existing intermediates detected; this wrapper does not clean them. Follow the compilation guide clean-target rule for accepted full builds.'
    }
    $commands = @()
    if ($Request -eq 'REBUILD' -or $Request -eq 'CLEAN') { $commands += 'nmake clean /NOLOGO' }
    if ($Request -ne 'CLEAN') {
        $commands += 'nmake source_list /NOLOGO', 'nmake fastdep /NOLOGO'
        if ($Configuration.EndsWith('-fast')) {
            $commands += 'nmake precompile /NOLOGO', 'bin\jom build /NOLOGO'
        }
        else { $commands += 'nmake dll /NOLOGO' }
    }
    $exitCode = 0
    foreach ($command in $commands) {
        Write-BuildLine ('Command: ' + $command)
        # <!-- custom: Merge native stderr inside cmd so Windows PowerShell does not turn compiler diagnostics into terminating ErrorRecords.
        # Preserve each native exit code and stop at the first failing step; later commands must not hide a failed dependency/compile step. (GPT-6.1-Sol) -->
        & $env:ComSpec /d /s /c ($command + ' 2>&1') | ForEach-Object {
            $line = [string]$_
            Write-BuildLine $line
            if ($line -match '\bwarning\s+[A-Z]+[0-9]+\s*:') { [void]$warnings.Add($line) }
            if ($line -match '\b(?:fatal\s+)?error\s+[A-Z]+[0-9]+\s*:') { [void]$errors.Add($line) }
        }
        $exitCode = $LASTEXITCODE
        $report.steps += [ordered]@{ command = $command; exitCode = $exitCode }
        if ($exitCode -ne 0) { break }
    }
    if ($exitCode -eq 0 -and $Request -ne 'CLEAN' -and -not (Get-DllState)) {
        Write-BuildLine 'Build driver returned success but the target DLL is missing.'
        $exitCode = 1
    }
}
catch {
    Write-BuildLine ('Build reporting/driver failure: ' + $_.Exception.Message)
    $exitCode = 1
}
finally {
    $timer.Stop()
    $report['endedUtc'] = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    $report['durationMilliseconds'] = $timer.ElapsedMilliseconds
    $report['exitCode'] = $exitCode
    $report.status = if ($exitCode -eq 0) { 'SUCCEEDED' } else { 'FAILED' }
    $report['warningCount'] = $warnings.Count
    $report['errorCount'] = $errors.Count
    $report['recognizedWarningLines'] = @($warnings | Sort-Object)
    $report['recognizedErrorLines'] = @($errors | Sort-Object)
    $report['commitAfter'] = Get-GitText -Arguments @('rev-parse', 'HEAD')
    $report['workingTreeStatusAfter'] = Get-GitText -Arguments @('status', '--porcelain=v1', '--untracked-files=normal')
    $report['sourceProvenanceAfter'] = Get-SourceProvenance
    $report['tempAfter'] = Get-TempState
    $report['dllAfter'] = Get-DllState
    try {
        $inputsAfter = Get-BuildInputSnapshot
        $changedInputs = @(Get-BuildInputReport $inputsBefore $inputsAfter)
        $report['buildInputChanges'] = $changedInputs
        $unchangedCount = $inputsBefore.Count - @($changedInputs | Where-Object { $_.change -ne 'ADDED' }).Count
        $report['buildInputSummary'] = [ordered]@{ scope = 'CURRENT_BUILD_START_TO_END'; beforeCount = $inputsBefore.Count; afterCount = $inputsAfter.Count; unchangedCount = $unchangedCount; changedCount = $changedInputs.Count }
        Write-BuildLine ('During this build attempt: {0} files before, {1} after; {2} unchanged; {3} changes (including timestamp-only changes).' -f $inputsBefore.Count, $inputsAfter.Count, $unchangedCount, $changedInputs.Count)
    }
    catch {
        # <!-- custom: A failed final snapshot must not suppress the compiler result/report; mark it explicitly rather than presenting the initial snapshot as final evidence. (GPT-6.1-Sol) -->
        $report['buildInputsAfterError'] = $_.Exception.Message
    }
    Write-BuildLine ('Ended UTC: {0}; result: {1}; exit code: {2}; duration milliseconds: {3}' -f $report.endedUtc, $report.status, $exitCode, $report.durationMilliseconds)
    Write-BuildLine ('Distinct coded diagnostic lines: warnings={0}; errors={1}' -f $warnings.Count, $errors.Count)
    Write-BuildLine ('Build output log: ' + $logPath)
    Write-BuildLine ('Build details (JSON): ' + $reportPath)
    if ($null -ne $writer) { $writer.Dispose() }
    [IO.File]::WriteAllText($reportPath, (($report | ConvertTo-Json -Depth 6) + "`n"), (New-Object Text.UTF8Encoding($false)))
}
exit $exitCode
