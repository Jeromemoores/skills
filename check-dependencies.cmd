@echo off
setlocal
set "taskProject=%~1"
if not defined taskProject set "taskProject=%CD%"
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0skills\dependency-docs\scripts\dependency_docs.py" check --project "%taskProject%" --format table
) else (
    python "%~dp0skills\dependency-docs\scripts\dependency_docs.py" check --project "%taskProject%" --format table
)
exit /b %errorlevel%
