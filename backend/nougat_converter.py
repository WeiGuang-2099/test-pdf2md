"""
Nougat PDF 转 Markdown 转换器
使用 Meta 的 Nougat 神经网络模型
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_nougat_installed():
    """检查 Nougat 是否已安装"""
    # 检查 nougat 命令是否可用
    if shutil.which("nougat"):
        return True
    
    # 备用检查：尝试导入 nougat 包
    try:
        result = subprocess.run(
            ["nougat", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def convert_with_nougat(pdf_path: str, output_dir: str = None, use_gpu: bool = None):
    """
    使用 Nougat 转换 PDF
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录（默认为 PDF 同目录）
        use_gpu: 是否使用 GPU（None=自动检测）
    """
    
    # 检查安装
    if not check_nougat_installed():
        print("❌ Nougat 未安装")
        print()
        print("请运行以下命令安装:")
        print("  pip install nougat-ocr")
        print()
        print("或运行安装脚本:")
        print("  .\\install_nougat.bat")
        return False
    
    # 检查文件
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path) or "."
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建命令
    cmd = ["nougat", pdf_path, "-o", output_dir]
    
    # GPU 设置
    if use_gpu is False:
        cmd.extend(["--no-cuda"])
    
    # 其他优化参数
    cmd.extend([
        "--markdown",  # 输出 Markdown 格式
        "--no-skipping",  # 不跳过任何页面
    ])
    
    print("=" * 70)
    print("  Nougat PDF → Markdown 转换器")
    print("=" * 70)
    print()
    print(f"输入文件: {pdf_path}")
    print(f"输出目录: {output_dir}")
    
    # 检测 GPU
    try:
        import torch
        has_gpu = torch.cuda.is_available()
        if has_gpu:
            print(f"GPU: ✓ CUDA 可用")
        else:
            print(f"GPU: ✗ 使用 CPU 模式（速度较慢）")
    except ImportError:
        print(f"GPU: ✗ 使用 CPU 模式")
    
    print()
    print("正在转换...")
    print("-" * 70)
    
    # 首次运行提示
    model_dir = Path.home() / ".cache" / "huggingface" / "hub"
    if not model_dir.exists() or not any(model_dir.glob("models--*nougat*")):
        print()
        print("⏳ 首次运行需要下载模型（约 350MB）")
        print("   这可能需要几分钟，请耐心等待...")
        print()
    
    try:
        # 执行转换
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        print()
        print("=" * 70)
        print("✓ 转换完成！")
        print("=" * 70)
        
        # 查找输出文件
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
        
        if os.path.exists(output_file):
            print(f"输出文件: {output_file}")
            
            # 显示文件大小
            size = os.path.getsize(output_file)
            print(f"文件大小: {size:,} 字节")
            
            # 预览前500字符
            print()
            print("-" * 70)
            print("预览:")
            print("-" * 70)
            with open(output_file, 'r', encoding='utf-8') as f:
                preview = f.read(500)
                print(preview)
                if size > 500:
                    print("\n... (更多内容请查看输出文件)")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 70)
        print("❌ 转换失败")
        print("=" * 70)
        print()
        
        if e.stderr:
            print("错误信息:")
            print(e.stderr)
        
        print()
        print("可能的原因:")
        print("1. PDF 文件损坏或格式不支持")
        print("2. 内存不足（Nougat 需要较多内存）")
        print("3. 模型下载失败（网络问题）")
        print()
        print("建议:")
        print("- 尝试使用更小的 PDF 文件测试")
        print("- 确保有足够的内存（建议 8GB+）")
        print("- 检查网络连接（首次运行需要下载模型）")
        
        return False
    
    except Exception as e:
        print()
        print(f"❌ 发生错误: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python nougat_converter.py <pdf文件> [输出目录]")
        print()
        print("示例:")
        print("  python nougat_converter.py paper.pdf")
        print("  python nougat_converter.py paper.pdf output_dir")
        print()
        print("参数:")
        print("  <pdf文件>    - 要转换的 PDF 文件路径")
        print("  [输出目录]   - 可选，输出目录（默认为 PDF 同目录）")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_with_nougat(pdf_path, output_dir)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
