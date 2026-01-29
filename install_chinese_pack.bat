@echo off
chcp 65001 >nul
echo ====================================
echo Tesseract 中文语言包安装工具
echo ====================================
echo.

set "TESSDATA=C:\Program Files\Tesseract-OCR\tessdata"

REM 检查 Tesseract 是否安装
if not exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo ✗ 错误: 未找到 Tesseract 安装
    echo   请先安装 Tesseract OCR
    pause
    exit /b 1
)

echo ✓ 找到 Tesseract 安装
echo   tessdata 路径: %TESSDATA%
echo.

REM 检查是否已经有中文语言包
if exist "%TESSDATA%\chi_sim.traineddata" (
    echo ✓ 简体中文语言包已存在，无需下载
    echo.
    goto :verify
)

echo [1/2] 下载简体中文语言包 (chi_sim.traineddata)...
echo       文件大小约 50MB，请耐心等待...
echo.

REM 使用 PowerShell 下载文件
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata' -OutFile '%TESSDATA%\chi_sim.traineddata'}" 2>nul

if exist "%TESSDATA%\chi_sim.traineddata" (
    echo ✓ 简体中文语言包下载成功！
) else (
    echo ✗ 下载失败
    echo.
    echo 请手动下载:
    echo 1. 访问: https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
    echo 2. 将下载的文件保存到: %TESSDATA%
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] 下载繁体中文语言包 (chi_tra.traineddata) [可选]...

if exist "%TESSDATA%\chi_tra.traineddata" (
    echo ✓ 繁体中文语言包已存在，跳过
) else (
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/chi_tra.traineddata' -OutFile '%TESSDATA%\chi_tra.traineddata'}" 2>nul
    
    if exist "%TESSDATA%\chi_tra.traineddata" (
        echo ✓ 繁体中文语言包下载成功！
    ) else (
        echo ○ 繁体中文语言包下载失败（可选项，不影响使用）
    )
)

:verify
echo.
echo ====================================
echo 验证安装...
echo ====================================
echo.

tesseract --list-langs 2>nul

echo.
echo ====================================
if exist "%TESSDATA%\chi_sim.traineddata" (
    echo ✓ 安装成功！
    echo.
    echo 中文语言包已安装，现在可以使用中文 OCR 了。
    echo.
    echo 重启应用:
    echo   python backend/main.py
) else (
    echo ✗ 安装失败
    echo.
    echo 请尝试手动安装方法（见 添加中文语言包.md）
)
echo ====================================
echo.
pause
