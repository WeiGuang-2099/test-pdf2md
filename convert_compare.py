"""
对比不同PDF转换方法的效果
"""

import os
import sys
import time
from pathlib import Path


def check_nougat():
    """检查 Nougat 是否可用"""
    try:
        import nougat
        return True
    except ImportError:
        return False


def convert_method_current(pdf_path: str):
    """方法1: 当前方法（pdfplumber + PyMuPDF）"""
    print("\n" + "=" * 70)
    print("方法 1: 当前方法（pdfplumber + PyMuPDF 智能提取）")
    print("=" * 70)
    
    from backend.main import pdf_bytes_to_markdown
    
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    start = time.time()
    markdown, pages = pdf_bytes_to_markdown(pdf_bytes)
    elapsed = time.time() - start
    
    output_path = pdf_path.replace('.pdf', '_current.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✓ 完成: {elapsed:.2f}秒")
    print(f"  输出: {output_path}")
    print(f"  字符数: {len(markdown):,}")
    print(f"  页数: {len(pages)}")
    
    return output_path, markdown


def convert_method_nougat(pdf_path: str):
    """方法2: Nougat（神经网络OCR）"""
    print("\n" + "=" * 70)
    print("方法 2: Nougat（Meta 神经网络 OCR）")
    print("=" * 70)
    
    if not check_nougat():
        print("❌ Nougat 未安装")
        print("   运行: .\\install_nougat.bat")
        return None, None
    
    import subprocess
    
    output_dir = os.path.dirname(pdf_path) or "."
    
    start = time.time()
    
    try:
        result = subprocess.run(
            ["nougat", pdf_path, "-o", output_dir, "--markdown"],
            capture_output=True,
            text=True,
            check=True
        )
        elapsed = time.time() - start
        
        # 查找输出文件
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        nougat_output = os.path.join(output_dir, f"{pdf_name}.mmd")
        
        if os.path.exists(nougat_output):
            # 重命名为 _nougat.md
            output_path = pdf_path.replace('.pdf', '_nougat.md')
            os.rename(nougat_output, output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                markdown = f.read()
            
            print(f"✓ 完成: {elapsed:.2f}秒")
            print(f"  输出: {output_path}")
            print(f"  字符数: {len(markdown):,}")
            
            return output_path, markdown
        else:
            print("❌ 未找到输出文件")
            return None, None
    
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换失败")
        if e.stderr:
            print(f"   错误: {e.stderr[:200]}")
        return None, None


def analyze_quality(text: str, method_name: str):
    """简单分析文本质量"""
    import re
    
    lines = text.split('\n')
    non_empty = [l for l in lines if l.strip()]
    
    # 检测问题
    broken_words = len(re.findall(r'\b[a-z]{1,3}\b\s+\b[a-z]{1,3}\b', text))
    short_lines = len([l for l in non_empty if len(l.strip()) < 20])
    
    print(f"\n{method_name} 质量分析:")
    print(f"  总行数: {len(lines)}")
    print(f"  非空行: {len(non_empty)}")
    print(f"  可疑断词: {broken_words}")
    print(f"  短行数: {short_lines}")


def show_preview(text: str, method_name: str, chars: int = 500):
    """显示预览"""
    print(f"\n{method_name} 预览（前{chars}字符）:")
    print("-" * 70)
    print(text[:chars])
    if len(text) > chars:
        print("\n... (更多内容请查看输出文件)")


def main():
    if len(sys.argv) < 2:
        print("用法: python convert_compare.py <pdf文件>")
        print()
        print("示例:")
        print("  python convert_compare.py paper.pdf")
        print()
        print("功能:")
        print("  对比两种转换方法的效果")
        print("  - 方法1: 当前方法（pdfplumber + PyMuPDF）")
        print("  - 方法2: Nougat（神经网络OCR）")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("  PDF 转换方法对比测试")
    print("=" * 70)
    print(f"\n输入文件: {pdf_path}")
    
    # 方法1: 当前方法
    output1, text1 = convert_method_current(pdf_path)
    if text1:
        analyze_quality(text1, "方法1")
        show_preview(text1, "方法1")
    
    # 方法2: Nougat
    output2, text2 = convert_method_nougat(pdf_path)
    if text2:
        analyze_quality(text2, "方法2 (Nougat)")
        show_preview(text2, "方法2 (Nougat)")
    
    # 总结
    print("\n" + "=" * 70)
    print("  对比总结")
    print("=" * 70)
    
    if text1:
        print(f"\n方法1（当前）:")
        print(f"  文件: {output1}")
        print(f"  大小: {len(text1):,} 字符")
    
    if text2:
        print(f"\n方法2（Nougat）:")
        print(f"  文件: {output2}")
        print(f"  大小: {len(text2):,} 字符")
    
    print("\n推荐:")
    if text2:
        print("  ✓ 方法2（Nougat）- 专为学术论文优化，双栏处理最佳")
    else:
        print("  ⚠ 安装 Nougat 后可获得更好效果")
        print("    运行: .\\install_nougat.bat")


if __name__ == "__main__":
    main()
