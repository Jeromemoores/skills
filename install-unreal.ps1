[CmdletBinding()]
param(
    [ValidateSet('Both', 'Claude', 'Codex')]
    [string]$Target = 'Both',
    [string]$UserRoot = [Environment]::GetFolderPath('UserProfile')
)
$ErrorActionPreference = 'Stop'
$installer = Invoke-RestMethod 'https://raw.githubusercontent.com/Jeromemoores/skills/v1.2.0/install.ps1'
& ([scriptblock]::Create($installer)) -SkillSet Unreal -Target $Target -UserRoot $UserRoot
