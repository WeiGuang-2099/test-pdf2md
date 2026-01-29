@echo off
chcp 65001 >nul
echo ====================================
echo OCR 依赖检查工具
echo ====================================
echo.

set "MISSING=0"

echo [1/2] 检查 Ghostscript...
where gs >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Ghostscript 已安装并在 PATH 中
    gs -version | findstr /C:"Ghostscript" 2>nul
) else (
    where gswin64c >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Ghostscript 已安装并在 PATH 中
        gswin64c -version | findstr /C:"Ghostscript" 2>nul
    ) else (
        echo ✗ 未找到 Ghostscript
        echo   下载地址: https://ghostscript.com/releases/gsdnld.html
        echo   安装 Windows 64-bit 版本
        set "MISSING=1"
    )
)
echo.

echo [2/2] 检查 Tesseract OCR...
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Tesseract 已安装并在 PATH 中
    tesseract --version | findstr /C:"tesseract" 2>nul
    echo.
    echo   检查中文语言包...
    tesseract --list-langs 2>nul | findstr /C:"chi_sim" >nul
    if %errorlevel% equ 0 (
        echo   ✓ 简体中文语言包已安装
    ) else (
        echo   ✗ 简体中文语言包未安装
        echo     请重新安装 Tesseract 并勾选 "Chinese - Simplified"
        set "MISSING=1"
    )
) else (
    echo ✗ 未找到 Tesseract OCR
    echo   下载地址: https://github.com/UB-Mannheim/tesseract/wiki
    echo   安装时请勾选 "Chinese - Simplified" 语言包
    set "MISSING=1"
)
echo.

echo ====================================
if %MISSING% equ 0 (
    echo ✓ 所有依赖都已正确安装！
    echo.
    echo 您可以正常使用 OCR 功能了。
    echo 运行 'python backend/main.py' 启动应用。
) else (
    echo ⚠ 缺少必要的依赖
    echo.
    echo 请按照提示安装缺少的程序。
    echo 详细安装指南: OCR_SETUP_GUIDE.md
    echo.
    echo 如果已安装但未检测到，请：
    echo 1. 确认安装路径正确
    echo 2. 重启所有命令行窗口
    echo 3. 必要时手动添加到系统 PATH
)
echo ====================================
echo.
pause
