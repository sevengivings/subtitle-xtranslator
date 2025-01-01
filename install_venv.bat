@echo off

set current_dir=%homedrive%%homepath%

echo This script will create a Python virtual environment and install required packages.
echo Python venv environment needs 7 ~ 8 Gigabytes.   
echo Default installation directory is %current_dir%, %current_dir%\venv will be created. 

set /p installation_dir=Enter new directory or press Enter key: 

if "%installation_dir%" == "" (
    set installation_dir=%current_dir%
)

echo %installation_dir%\venv will be used. 
pause

if not exist "%installation_dir%\venv\Scripts" (
    echo Creating venv...
    python -m venv %installation_dir%\venv
)

call %installation_dir%\venv\Scripts\activate.bat

echo Python packages will be installed. 
pause Ctrl-C to cancel.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Requirements installation failed. please remove venv folder and run install_venv.bat again.
) else (
    echo.
    echo Requirements are installed successfully.
)
pause