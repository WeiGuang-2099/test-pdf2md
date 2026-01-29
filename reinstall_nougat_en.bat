@echo off
echo ====================================
echo Reinstall Nougat-OCR (Fixed Versions)
echo ====================================
echo.

REM Remove old environment
if exist venv_nougat (
    echo [1/5] Removing old virtual environment...
    rmdir /s /q venv_nougat
    echo Done.
) else (
    echo [1/5] No old environment found, skipping.
)

REM Create new environment
echo.
echo [2/5] Creating new virtual environment...
python -m venv venv_nougat
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)
echo Done.

REM Activate environment
call venv_nougat\Scripts\activate.bat

REM Upgrade pip
echo.
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel -q
echo Done.

REM Install core dependencies with compatible versions
echo.
echo [4/5] Installing core dependencies (compatible versions)...
echo    - pydantic 1.10.13
echo    - transformers 4.30.2
echo    - albumentations 1.3.1
pip install "pydantic==1.10.13" "transformers==4.30.2" "albumentations==1.3.1" -q

REM Install nougat-ocr
echo.
echo [5/5] Installing nougat-ocr (this may take several minutes)...
pip install nougat-ocr --no-deps
pip install nougat-ocr

if %errorlevel% neq 0 (
    echo.
    echo Installation failed
    pause
    exit /b 1
)

REM Verify
echo.
echo ====================================
echo Verifying installation...
echo ====================================
echo.
python -c "import nougat; print('Nougat import successful')"

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Installation Complete!
    echo ====================================
    echo.
    echo Usage:
    echo 1. Activate: venv_nougat\Scripts\activate
    echo 2. Run: nougat your_file.pdf -o output_dir
    echo 3. Or: python backend/nougat_converter.py your_file.pdf
    echo.
) else (
    echo.
    echo Verification failed
    echo.
    echo If problems persist, check Python version.
    echo nougat-ocr works best with Python 3.9 or 3.10
    echo.
)

pause
