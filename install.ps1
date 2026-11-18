[CmdletBinding()]
param(
    [ValidateSet('Both', 'Claude', 'Codex')]
    [string]$Target = 'Both',
    [ValidateSet('All', 'Web', 'Unreal')]
    [string]$SkillSet = 'All',
    [string]$UserRoot = [Environment]::GetFolderPath('UserProfile')
)

$ErrorActionPreference = 'Stop'
$taskVersion = '1.0.0'
$taskRelease = "https://github.com/Jeromemoores/skills/releases/download/v$taskVersion"
$taskSourceRoot = $null
if ($PSScriptRoot -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'skills'))) {
    $taskSourceRoot = $PSScriptRoot
}

if (-not $taskSourceRoot) {
    # Windows PowerShell 5.1 can default to older TLS protocols.
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $taskTemp = Join-Path ([IO.Path]::GetTempPath()) ('jeromemoores-skills-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $taskTemp | Out-Null
    $taskBundle = switch ($SkillSet) { 'Web' { 'web-skills' }; 'Unreal' { 'unreal-skills' }; default { 'skills' } }
    $taskPackage = "$taskBundle-v$taskVersion"
    $taskArchiveName = "$taskPackage.zip"
    $taskArchive = Join-Path $taskTemp $taskArchiveName
    $taskSums = Join-Path $taskTemp 'SHA256SUMS'
    Invoke-WebRequest -UseBasicParsing -Uri "$taskRelease/$taskArchiveName" -OutFile $taskArchive
    Invoke-WebRequest -UseBasicParsing -Uri "$taskRelease/SHA256SUMS" -OutFile $taskSums
    $taskPattern = '^([a-fA-F0-9]{64})  ' + [regex]::Escape($taskArchiveName) + '$'
    $taskMatches = @(Get-Content -LiteralPath $taskSums | Where-Object { $_ -match $taskPattern })
    if ($taskMatches.Count -ne 1) { throw 'Release checksum entry is missing or ambiguous.' }
    $taskExpected = [regex]::Match($taskMatches[0], $taskPattern).Groups[1].Value
    if ((Get-FileHash -LiteralPath $taskArchive -Algorithm SHA256).Hash -ne $taskExpected) {
        throw 'Release checksum verification failed.'
    }
    Expand-Archive -LiteralPath $taskArchive -DestinationPath $taskTemp
    $taskSourceRoot = Join-Path $taskTemp $taskPackage
}

$taskSetFiles = @('shared')
if ($SkillSet -in @('All', 'Web')) { $taskSetFiles += 'web' }
if ($SkillSet -in @('All', 'Unreal')) { $taskSetFiles += 'unreal' }
$taskNames = @($taskSetFiles | ForEach-Object {
    Get-Content -LiteralPath (Join-Path $taskSourceRoot "skill-sets\$_.txt")
} | Where-Object { $_.Trim() } | Select-Object -Unique)
$taskProfile = [IO.Path]::GetFullPath($UserRoot)
$taskDestinations = @()
if ($Target -in @('Both', 'Claude')) { $taskDestinations += Join-Path $taskProfile '.claude\skills' }
if ($Target -in @('Both', 'Codex')) { $taskDestinations += Join-Path $taskProfile '.agents\skills' }
foreach ($taskName in $taskNames) {
    if ($taskName -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') { throw "Invalid skill name: $taskName" }
    $taskSource = Join-Path $taskSourceRoot "skills\$taskName"
    if (-not (Test-Path -LiteralPath (Join-Path $taskSource 'SKILL.md'))) { throw "Missing skill: $taskName" }
    foreach ($taskRoot in $taskDestinations) {
        $taskDestination = Join-Path $taskRoot $taskName
        foreach ($taskFile in Get-ChildItem -LiteralPath $taskSource -File -Recurse) {
            if ($taskFile.FullName -match '[\\/]__pycache__[\\/]' -or $taskFile.Extension -in @('.pyc', '.pyo')) { continue }
            $taskRelative = $taskFile.FullName.Substring($taskSource.Length + 1)
            $taskOutput = Join-Path $taskDestination $taskRelative
            New-Item -ItemType Directory -Path (Split-Path -Parent $taskOutput) -Force | Out-Null
            Copy-Item -LiteralPath $taskFile.FullName -Destination $taskOutput -Force
        }
    }
}
Write-Output "Installed $($taskNames.Count) skills for $Target ($SkillSet), version $taskVersion."
Write-Output 'Start a new agent session if the skills do not appear. Documentation downloads require Python 3.11+ and Git.'
if ($taskTemp) { Write-Output "Downloaded release retained at: $taskTemp" }
