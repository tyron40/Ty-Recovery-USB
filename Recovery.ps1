# Windows PowerShell 5.1 or later. No disk writes or reset commands.
[CmdletBinding()]
param([switch]$DetectOnly)
$ErrorActionPreference = 'Stop'
try {
    $computer = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $catalog = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'catalog.json') -Raw | ConvertFrom-Json
    if ($catalog.schemaVersion -ne 1) { throw 'Unsupported catalog version.' }
    $id = 'windows'
    if ($computer.Manufacturer -match 'Microsoft' -and $computer.Model -match '^Surface') { $id = 'surface' }
    $route = @($catalog.routes | Where-Object { $_.id -eq $id })
    if ($route.Count -ne 1) { throw 'No unique recovery route. Stop and consult the manufacturer.' }
    $report = [ordered]@{
        manufacturer = $computer.Manufacturer
        model = $computer.Model
        operatingSystem = $os.Caption
        architecture = $os.OSArchitecture
        processorArchitectureCode = $cpu.Architecture
        route = $id
    }
    $report | ConvertTo-Json
    Write-Host "`n$($route[0].instructions)"
    Write-Host 'Detection describes the running Windows system. It does not certify installation compatibility.'
    if ($DetectOnly) { exit 0 }
    Write-Host "`n1. Open Windows Recovery settings (does not start a reset)"
    Write-Host '2. Open official recovery instructions'
    Write-Host 'Anything else: exit'
    $choice = Read-Host 'Choose'
    if ($choice -eq '1') {
        Start-Process 'ms-settings:recovery'
    } elseif ($choice -eq '2') {
        $url = [uri]$route[0].url
        if ($url.Scheme -ne 'https' -or $url.Host -notin @('support.microsoft.com','learn.microsoft.com')) {
            throw 'Catalog URL is not an allowed official Microsoft destination.'
        }
        Start-Process $url.AbsoluteUri
    }
} catch {
    Write-Error "Recovery stopped: $_"
    exit 1
}
