@echo off
chcp 65001 >nul
echo ====================================
echo Nougat-OCR 安装脚本
echo ====================================
echo.

REM 检查是否已安装 Python 3.10
echo [1/4] 检查 Python 3.10...
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 未检测到 Python 3.10
    echo.
    echo 请按照以下步骤操作：
    echo 1. 访问: https://www.python.org/downloads/release/python-31011/
    echo 2. 下载 "Windows installer (64-bit)"
    echo 3. 安装时勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✓ 找到 Python 3.10
py -3.10 --version

REM 创建虚拟环境
echo.
echo [2/4] 创建虚拟环境 (venv_nougat)...
if exist venv_nougat (
    echo ⚠ 虚拟环境已存在，将使用现有环境
) else (
    py -3.10 -m venv venv_nougat
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建成功
)

REM 激活虚拟环境并升级 pip
echo.
echo [3/4] 升级 pip...
call venv_nougat\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel -q
echo ✓ pip 升级完成

REM 安装 nougat-ocr
echo.
echo [4/4] 安装 nougat-ocr (这可能需要几分钟)...
pip install nougat-ocr
if %errorlevel% neq 0 (
    echo.
    echo ❌ 安装失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo ✓ 安装完成！
echo ====================================
echo.
echo 使用方法：
echo 1. 激活环境: venv_nougat\Scripts\activate
echo 2. 运行 nougat: nougat your_file.pdf -o output_dir
echo.
echo 按任意键退出...
pause >nul
