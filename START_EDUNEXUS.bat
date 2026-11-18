@echo off
setlocal
cd /d "%~dp0"
title EduNexus
echo ============================================
echo   EduNexus - setup and launcher
echo ============================================
echo.

where winget >nul 2>&1
if errorlevel 1 set NOWINGET=1

rem ---- 1. find Python 3.11 / 3.12 / 3.13 ----
set PYV=
for %%V in (3.12 3.11 3.13) do (
  if not defined PYV (
    py -%%V -c "import sys" >nul 2>&1 && set PYV=%%V
  )
)
set NEEDRESTART=
if defined PYV goto havepython
if defined NOWINGET goto nowinget_python
echo Python 3.12 not found. Installing it now (one time)...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
set NEEDRESTART=1
goto checkollama
:nowinget_python
echo.
echo Python 3.12 is needed. Install it from https://www.python.org/downloads/release/python-3120/
echo (tick "Add python.exe to PATH"), then double-click this file again.
pause
exit /b 1
:havepython

rem ---- 2. Ollama (the local AI engine) ----
:checkollama
where ollama >nul 2>&1
if not errorlevel 1 goto haveollama
if defined NOWINGET goto haveollama
echo Ollama not found. Installing it now (one time)...
winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements
set NEEDRESTART=1
:haveollama

if not defined NEEDRESTART goto continue
echo.
echo ------------------------------------------------------------
echo  Required programs were just installed.
echo  Please CLOSE this window and double-click START_EDUNEXUS.bat again.
echo ------------------------------------------------------------
pause
exit /b 0
:continue

rem ---- 3. private Python environment (recreated if it uses a wrong Python version) ----
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys;sys.exit(0 if sys.version_info[:2] in ((3,11),(3,12),(3,13)) else 1)" >nul 2>&1
  if errorlevel 1 rmdir /s /q .venv
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating environment with Python %PYV% ...
  py -%PYV% -m venv .venv
  if errorlevel 1 goto fail
)

rem ---- 4. install packages (only the first time) ----
if exist ".venv\installed.flag" goto pkgsdone
echo Installing packages (first time only, 1-3 minutes)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto fail
echo ok> ".venv\installed.flag"
:pkgsdone

rem ---- 5. settings file with a private random secret key ----
if exist ".env" goto envdone
copy ".env.example" ".env" >nul
for /f %%K in ('".venv\Scripts\python.exe" -c "import secrets;print(secrets.token_urlsafe(48))"') do set KEY=%%K
powershell -NoProfile -Command "(Get-Content .env) -replace 'SECRET_KEY=.*','SECRET_KEY=%KEY%' | Set-Content .env"
:envdone

rem ---- 6. AI model (about 2 GB, first time only) ----
where ollama >nul 2>&1
if errorlevel 1 goto skipmodel
ollama list 2>nul | findstr /i "llama3.2" >nul
if not errorlevel 1 goto skipmodel
echo Downloading the AI model llama3.2 (about 2 GB, first time only)...
ollama pull llama3.2
if errorlevel 1 echo WARNING: model download failed. Make sure the Ollama app is running, then run this file again.
:skipmodel

rem ---- 7. start the app ----
echo.
echo Starting EduNexus... your browser will open at http://localhost:8000
echo Keep this window open while using the app. Close it to stop EduNexus.
echo.
".venv\Scripts\python.exe" app.py
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong (see the messages above). Send a screenshot of this window for help.
pause
exit /b 1
