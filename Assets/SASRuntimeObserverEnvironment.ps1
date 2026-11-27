# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Capture the actual external observer host once, rather than maintaining a machine-specific version table in documentation.
# Both PowerShell companions dot-source this definition; it performs no observation, compilation or file writes by itself. CLR and Framework release identify different layers, not the C# compiler/language version. (GPT-6.1-Sol) -->
function Get-SASRuntimeObserverEnvironment {
    $frameworkRelease = $null
    try {
        $frameworkRelease = (Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' -Name Release -ErrorAction Stop).Release
    } catch { }
    return [ordered]@{
        powershellVersion = $PSVersionTable.PSVersion.ToString()
        powershellEdition = [string]$PSVersionTable.PSEdition
        clrVersion = [Environment]::Version.ToString()
        frameworkRelease = $frameworkRelease
        processBits = [IntPtr]::Size * 8
        executablePath = [System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
    }
}
