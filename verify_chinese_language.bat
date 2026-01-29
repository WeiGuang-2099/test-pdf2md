@echo off
chcp 65001 >nul
echo ====================================
echo Tesseract 中文语言包检查
echo ====================================
echo.

echo [1] 检查 Tesseract 版本...
tesseract --version 2>nul
if %errorlevel% neq 0 (
    echo ✗ Tesseract 未找到
    pause
    exit /b 1
)
echo.

echo [2] 检查已安装的语言包...
tesseract --list-langs 2>nul
echo.

echo [3] 检查中文语言包文件...
set "TESSDATA=C:\Program Files\Tesseract-OCR\tessdata"

if exist "%TESSDATA%\chi_sim.traineddata" (
    echo ✓ 找到简体中文语言包: chi_sim.traineddata
    dir "%TESSDATA%\chi_sim.traineddata" | findstr /C:"chi_sim"
) else (
    echo ✗ 未找到简体中文语言包
    echo   文件应该在: %TESSDATA%\chi_sim.traineddata
)
echo.

if exist "%TESSDATA%\chi_tra.traineddata" (
    echo ✓ 找到繁体中文语言包: chi_tra.traineddata
) else (
    echo ○ 未安装繁体中文语言包（可选）
)
echo.

echo ====================================
echo 如果未找到中文语言包，请：
echo 1. 重新运行 Tesseract 安装程序
echo 2. 选择 "Modify" 修改安装
echo 3. 勾选 "Chinese - Simplified"
echo 或者使用手动安装方法（见文档）
echo ====================================
pause
