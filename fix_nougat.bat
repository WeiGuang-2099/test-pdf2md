@echo off
chcp 65001 >nul
echo ====================================
echo 修复 Nougat 依赖问题
echo ====================================
echo.

REM 激活虚拟环境
call venv_nougat\Scripts\activate.bat

echo [1/4] 卸载不兼容的包...
pip uninstall transformers pydantic albumentations -y

echo.
echo [2/4] 安装兼容版本的核心依赖...
pip install "pydantic==1.10.13"

echo.
echo [3/4] 安装兼容版本的其他依赖...
pip install "transformers==4.30.2" "albumentations==1.3.1"

echo.
echo [4/4] 验证安装...
echo.
python -c "import nougat; print('✓ Nougat 包导入成功')"

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo ✓ 修复完成！
    echo ====================================
    echo.
    echo 现在可以使用 nougat 了：
    echo   nougat your_file.pdf -o output_dir
    echo.
) else (
    echo.
    echo ====================================
    echo ❌ 仍有问题
    echo ====================================
    echo.
    echo 建议完全重装。请执行：
    echo 1. 删除 venv_nougat 文件夹
    echo 2. 运行: .\reinstall_nougat.bat
    echo.
)

pause
