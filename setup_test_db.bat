@echo off
rem ------------------------------------------------------------
rem  Setup script for MiVoto application (software de sambleas)
rem  - Activates virtual environment
rem  - Creates database tables (fallback to db.create_all())
rem  - Populates at least 30 rows of test data
rem ------------------------------------------------------------

rem Activate virtual environment
if exist "venv\\Scripts\\activate.bat" (
    call "venv\\Scripts\\activate.bat"
) else (
    echo Virtual environment not found. Please create it first (python -m venv venv).
    exit /b 1
)

rem Ensure Flask environment variables
set FLASK_APP=run.py
set FLASK_ENV=development

rem Reset database and populate all initial and test data
python reset_db.py

if %errorlevel% neq 0 (
    echo One or more steps failed. Check the output above for details.
) else (
    echo Database setup and test data insertion completed successfully.
)

pause
