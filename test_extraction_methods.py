"""
PDF 提取方法对比测试工具

用法:
    python test_extraction_methods.py <pdf文件路径>

输出:
    - 方法1: 默认提取 (default.md)
    - 方法2: layout=True (layout.md)
    - 方法3: 智能提取 (smart.md)
    - 对比报告 (comparison_report.txt)
"""

import sys
import os
from io import BytesIO
import pdfplumber

# 导入智能提取器
from backend.smart_extractor import SmartPDFExtractor

try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False


def method_1_default(pdf_bytes: bytes) -> str:
    """方法1: 默认提取（当前方法）"""
    result = []
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                result.append(f"## Page {idx}\n\n{text}\n")
    
    return '\n'.join(result)


def method_2_layout(pdf_bytes: bytes) -> str:
    """方法2: layout=True 提取"""
    result = []
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(
                layout=True,
                x_tolerance=3,
                y_tolerance=3
            )
            if text:
                # 简单清理：移除过多空格
                lines = text.split('\n')
                cleaned = []
                for line in lines:
                    line = line.rstrip()
                    if line.strip():
                        cleaned.append(line)
                
                result.append(f"## Page {idx}\n\n" + '\n'.join(cleaned) + "\n")
    
    return '\n'.join(result)


def method_3_smart(pdf_bytes: bytes) -> str:
    """方法3: 智能提取"""
    extractor = SmartPDFExtractor()
    markdown, _ = extractor.extract_pdf(pdf_bytes)
    return markdown


def analyze_text(text: str, method_name: str):
    """分析提取的文本质量"""
    lines = text.split('\n')
    
    # 统计信息
    total_chars = len(text)
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    
    # 检测噪声
    noise_patterns = [
        r'^\d+\s*$',
        r'^\[[\w\.\s]+\]$',
        r'^\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}$',
        r'^arXiv:\d+',
        r'^v\d+$',
    ]
    
    import re
    noise_lines = 0
    for line in lines:
        stripped = line.strip()
        for pattern in noise_patterns:
            if re.match(pattern, stripped):
                noise_lines += 1
                break
    
    # 检测断行问题（行中间断开的句子）
    broken_lines = 0
    for i in range(len(lines) - 1):
        line = lines[i].strip()
        next_line = lines[i + 1].strip()
        
        # 如果当前行不以句号结束，且下一行以小写开头
        if (line and next_line and 
            not line.endswith(('.', '!', '?', ':', ';', ',')) and
            len(line) > 20 and  # 排除短标题
            next_line[0].islower()):
            broken_lines += 1
    
    # 检测连字符
    hyphen_breaks = len(re.findall(r'-\s*\n\s*[a-z]', text))
    
    return {
        "method": method_name,
        "total_chars": total_chars,
        "total_lines": total_lines,
        "non_empty_lines": non_empty_lines,
        "noise_lines": noise_lines,
        "broken_lines": broken_lines,
        "hyphen_breaks": hyphen_breaks,
        "noise_ratio": noise_lines / non_empty_lines if non_empty_lines > 0 else 0,
        "broken_ratio": broken_lines / non_empty_lines if non_empty_lines > 0 else 0,
    }


def print_comparison(stats_list):
    """打印对比报告"""
    print("\n" + "=" * 80)
    print("                         提取方法对比报告")
    print("=" * 80)
    print()
    
    # 表头
    print(f"{'指标':<20} {'方法1: 默认':<20} {'方法2: layout':<20} {'方法3: 智能':<20}")
    print("-" * 80)
    
    # 总字符数
    print(f"{'总字符数':<20} {stats_list[0]['total_chars']:<20} {stats_list[1]['total_chars']:<20} {stats_list[2]['total_chars']:<20}")
    
    # 总行数
    print(f"{'总行数':<20} {stats_list[0]['total_lines']:<20} {stats_list[1]['total_lines']:<20} {stats_list[2]['total_lines']:<20}")
    
    # 有效行数
    print(f"{'有效行数':<20} {stats_list[0]['non_empty_lines']:<20} {stats_list[1]['non_empty_lines']:<20} {stats_list[2]['non_empty_lines']:<20}")
    
    # 噪声行数
    print(f"{'噪声行数':<20} {stats_list[0]['noise_lines']:<20} {stats_list[1]['noise_lines']:<20} {stats_list[2]['noise_lines']:<20}")
    
    # 噪声比例
    print(f"{'噪声比例':<20} {stats_list[0]['noise_ratio']:.1%:<20} {stats_list[1]['noise_ratio']:.1%:<20} {stats_list[2]['noise_ratio']:.1%:<20}")
    
    # 断行问题
    print(f"{'断行数':<20} {stats_list[0]['broken_lines']:<20} {stats_list[1]['broken_lines']:<20} {stats_list[2]['broken_lines']:<20}")
    
    # 断行比例
    print(f"{'断行比例':<20} {stats_list[0]['broken_ratio']:.1%:<20} {stats_list[1]['broken_ratio']:.1%:<20} {stats_list[2]['broken_ratio']:.1%:<20}")
    
    # 连字符断行
    print(f"{'连字符断行':<20} {stats_list[0]['hyphen_breaks']:<20} {stats_list[1]['hyphen_breaks']:<20} {stats_list[2]['hyphen_breaks']:<20}")
    
    print("-" * 80)
    
    # 计算总分（越低越好）
    scores = []
    for stats in stats_list:
        score = (
            stats['noise_ratio'] * 100 +
            stats['broken_ratio'] * 100 +
            stats['hyphen_breaks']
        )
        scores.append(score)
    
    print(f"{'质量评分(越低越好)':<20} {scores[0]:<20.1f} {scores[1]:<20.1f} {scores[2]:<20.1f}")
    
    # 推荐
    best_idx = scores.index(min(scores))
    methods = ['方法1: 默认', '方法2: layout', '方法3: 智能']
    print(f"\n🏆 推荐方法: {methods[best_idx]}")
    
    print("\n" + "=" * 80)
    print()


def save_report(stats_list, output_path):
    """保存对比报告到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("                         提取方法对比报告\n")
        f.write("=" * 80 + "\n\n")
        
        for stats in stats_list:
            f.write(f"## {stats['method']}\n\n")
            f.write(f"- 总字符数: {stats['total_chars']}\n")
            f.write(f"- 总行数: {stats['total_lines']}\n")
            f.write(f"- 有效行数: {stats['non_empty_lines']}\n")
            f.write(f"- 噪声行数: {stats['noise_lines']} ({stats['noise_ratio']:.1%})\n")
            f.write(f"- 断行问题: {stats['broken_lines']} ({stats['broken_ratio']:.1%})\n")
            f.write(f"- 连字符断行: {stats['hyphen_breaks']}\n")
            f.write("\n")
        
        # 计算总分
        scores = []
        for stats in stats_list:
            score = (
                stats['noise_ratio'] * 100 +
                stats['broken_ratio'] * 100 +
                stats['hyphen_breaks']
            )
            scores.append(score)
        
        f.write("## 质量评分 (越低越好)\n\n")
        for i, stats in enumerate(stats_list):
            f.write(f"- {stats['method']}: {scores[i]:.1f}\n")
        
        best_idx = scores.index(min(scores))
        f.write(f"\n🏆 推荐方法: {stats_list[best_idx]['method']}\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python test_extraction_methods.py <pdf文件路径>")
        print()
        print("示例: python test_extraction_methods.py sample.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ 错误: 文件不存在: {pdf_path}")
        sys.exit(1)
    
    print(f"正在测试: {pdf_path}")
    print()
    
    # 读取 PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # 输出目录
    base_name = os.path.splitext(pdf_path)[0]
    
    # 测试三种方法
    print("⏳ 方法1: 默认提取...")
    text1 = method_1_default(pdf_bytes)
    output1 = f"{base_name}_default.md"
    with open(output1, 'w', encoding='utf-8') as f:
        f.write(text1)
    print(f"   ✓ 已保存: {output1}")
    
    print("⏳ 方法2: layout=True 提取...")
    text2 = method_2_layout(pdf_bytes)
    output2 = f"{base_name}_layout.md"
    with open(output2, 'w', encoding='utf-8') as f:
        f.write(text2)
    print(f"   ✓ 已保存: {output2}")
    
    print("⏳ 方法3: 智能提取...")
    if not HAS_PYMUPDF:
        print("   ⚠ 警告: 未安装 PyMuPDF，智能提取效果可能受限")
        print("   建议运行: pip install pymupdf")
    text3 = method_3_smart(pdf_bytes)
    output3 = f"{base_name}_smart.md"
    with open(output3, 'w', encoding='utf-8') as f:
        f.write(text3)
    print(f"   ✓ 已保存: {output3}")
    
    # 分析对比
    print("\n⏳ 正在分析结果...")
    stats1 = analyze_text(text1, "方法1: 默认")
    stats2 = analyze_text(text2, "方法2: layout")
    stats3 = analyze_text(text3, "方法3: 智能")
    
    stats_list = [stats1, stats2, stats3]
    
    # 打印对比
    print_comparison(stats_list)
    
    # 保存报告
    report_path = f"{base_name}_comparison_report.txt"
    save_report(stats_list, report_path)
    print(f"✓ 对比报告已保存: {report_path}")
    
    # 显示预览
    print("\n" + "=" * 80)
    print("                            方法3 预览")
    print("=" * 80)
    print(text3[:800])
    if len(text3) > 800:
        print("\n... (更多内容请查看输出文件)")
    print()


if __name__ == "__main__":
    main()
