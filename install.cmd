@echo off
setlocal
set "taskSource=%~dp0skills"
set "taskProfile=%USERPROFILE%"
if not "%~1"=="" set "taskProfile=%~1"
if not exist "%taskSource%\" (
    echo Extract the ZIP first, then run install.cmd from the extracted folder.
    exit /b 1
)
rem /MIR replaces each skill folder; /XF keeps machine-local preferences out of the purge.
set "taskKeep=library-location.json unreal-location.json"
set /a taskCount=0 >nul
for /d %%S in ("%taskSource%\*") do (
    if exist "%%~fS\SKILL.md" (
        robocopy "%%~fS" "%taskProfile%\.claude\skills\%%~nxS" /MIR /XF %taskKeep% /R:1 /W:1 /NFL /NDL /NJH /NJS /NP >nul
        if errorlevel 8 goto failed
        robocopy "%%~fS" "%taskProfile%\.agents\skills\%%~nxS" /MIR /XF %taskKeep% /R:1 /W:1 /NFL /NDL /NJH /NJS /NP >nul
        if errorlevel 8 goto failed
        set /a taskCount+=1 >nul
    )
)
echo Installed %taskCount% skills for Claude Code and Codex.
echo Start a new agent session if the skills do not appear.
echo Documentation downloads require Python 3.11+ and Git.
if "%~1"=="" pause
exit /b 0
:failed
echo Installation failed while copying skill files.
if "%~1"=="" pause
exit /b 1
