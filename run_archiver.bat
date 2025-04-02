@echo off
echo News Magazine Archiver
echo ========================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python 3.6 or higher.
    pause
    exit /b
)

:main_menu
cls
echo Main Menu
echo =========
echo 1. The Atlantic
echo 2. The Economist
echo 3. Set your Readwise API token
echo 4. Exit
echo.

set /p main_choice="Enter your choice (1-4): "

if "%main_choice%"=="1" (
    call :atlantic_menu
) else if "%main_choice%"=="2" (
    call :economist_menu
) else if "%main_choice%"=="3" (
    set /p token="Enter your Readwise API token: "
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--token', '%token%']); main()"
    echo Token set successfully.
    pause
    goto main_menu
) else if "%main_choice%"=="4" (
    echo Goodbye!
    exit /b
) else (
    echo Invalid choice.
    pause
    goto main_menu
)

exit /b

:atlantic_menu
cls
echo The Atlantic Menu
echo ================
echo 1. List available issues
echo 2. Archive a specific issue
echo 3. Interactive issue selection
echo 4. Back to main menu
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'atlantic']); main()"
    pause
    goto atlantic_menu
) else if "%choice%"=="2" (
    set /p issue="Enter the exact issue name (e.g., 'April 2025'): "
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', '%issue%', '--source', 'atlantic']); main()"
    pause
    goto atlantic_menu
) else if "%choice%"=="3" (
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'atlantic']); main()"
    pause
    goto atlantic_menu
) else if "%choice%"=="4" (
    goto main_menu
) else (
    echo Invalid choice.
    pause
    goto atlantic_menu
)

:economist_menu
cls
echo The Economist Menu
echo =================
echo 1. List available issues
echo 2. Archive a specific issue
echo 3. Interactive issue selection
echo 4. Back to main menu
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'economist']); main()"
    pause
    goto economist_menu
) else if "%choice%"=="2" (
    set /p issue="Enter the exact issue name (e.g., 'Mar 29th 2025'): "
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', '%issue%', '--source', 'economist']); main()"
    pause
    goto economist_menu
) else if "%choice%"=="3" (
    python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'economist']); main()"
    pause
    goto economist_menu
) else if "%choice%"=="4" (
    goto main_menu
) else (
    echo Invalid choice.
    pause
    goto economist_menu
) 