@echo off
chcp 65001 >nul
echo ================================================
echo       安装 Nougat OCR
echo ================================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo    请先安装 Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python 已安装
echo.

echo [2/3] 安装 Nougat OCR...
echo    这可能需要几分钟，请耐心等待...
echo.
pip install nougat-ocr

if errorlevel 1 (
    echo.
    echo ❌ 安装失败
    echo.
    echo 可能的解决方法:
    echo 1. 升级 pip: python -m pip install --upgrade pip
    echo 2. 使用国内镜像: pip install nougat-ocr -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

echo.
echo [3/3] 验证安装...
python -c "import nougat; print('✓ Nougat 安装成功！')"

if errorlevel 1 (
    echo ❌ 验证失败
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✓ 安装完成！
echo ================================================
echo.
echo 使用方法:
echo   python backend/nougat_converter.py your_paper.pdf
echo.
echo 注意:
echo   - 首次运行会自动下载模型（约350MB）
echo   - 建议使用GPU获得最佳效果
echo   - CPU模式可用但较慢
echo.
pause
