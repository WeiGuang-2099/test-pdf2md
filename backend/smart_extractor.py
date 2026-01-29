"""
智能 PDF 提取器 - 通用解决方案
结合 PyMuPDF 布局分析 + pdfplumber 文本提取

核心理念：
1. 自动检测主内容区域（排除边栏、页眉页脚）
2. 自动识别栏数和位置（单栏/双栏/多栏）
3. 使用 layout=True 保留结构
4. 智能清理和格式化
"""

import re
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
import pdfplumber


# 条件导入 PyMuPDF
try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False


class SmartPDFExtractor:
    """智能 PDF 提取器"""
    
    def __init__(self):
        self.noise_patterns = [
            r'^\d+\s*$',                              # 纯页码
            r'^Page\s+\d+\s*$',                       # "Page 1"
            r'^\[[\w\.\s]+\]$',                       # [cs.AI]
            r'^\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}$',    # 日期: 10 Nov 2025
            r'^arXiv:\d+\.\d+v?\d*$',                 # arXiv:2511.07587v1
            r'^v\d+$',                                # v1, v2
            r'^viXra$',                               # viXra
            r'^[A-Z]{2,4}$',                          # 缩写（如 AI, ML）
        ]
    
    def detect_content_area(self, page) -> Optional[Tuple[float, float, float, float]]:
        """
        使用 PyMuPDF 检测主内容区域
        返回: (x0, y0, x1, y1) 或 None
        """
        if not HAS_PYMUPDF:
            return None
        
        try:
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b["type"] == 0]
            
            if not text_blocks:
                return None
            
            all_bboxes = [b["bbox"] for b in text_blocks]
            
            # 计算页面尺寸
            page_width = page.rect.width
            page_height = page.rect.height
            
            # 将页面分为垂直条带，计算文本密度
            num_strips = 20
            strip_width = page_width / num_strips
            density = [0.0] * num_strips
            
            for bbox in all_bboxes:
                x0, y0, x1, y1 = bbox
                # 计算文本块的面积
                area = (x1 - x0) * (y1 - y0)
                
                # 计算占据哪些条带
                start_strip = int(x0 / strip_width)
                end_strip = int(x1 / strip_width)
                
                for i in range(start_strip, min(end_strip + 1, num_strips)):
                    if 0 <= i < num_strips:
                        density[i] += area
            
            # 找出密度显著的区域
            max_density = max(density) if density else 0
            if max_density == 0:
                return None
            
            threshold = max_density * 0.2  # 20% 的最大密度作为阈值
            significant_strips = [i for i, d in enumerate(density) if d > threshold]
            
            if not significant_strips:
                return None
            
            # 计算主内容区域的边界
            content_x_min = min(significant_strips) * strip_width
            content_x_max = (max(significant_strips) + 1) * strip_width
            
            # Y轴方向：使用所有文本块的边界
            content_y_min = min(bbox[1] for bbox in all_bboxes)
            content_y_max = max(bbox[3] for bbox in all_bboxes)
            
            # 添加一些边距（避免裁剪过度）
            margin = strip_width * 0.5
            content_x_min = max(0, content_x_min - margin)
            content_x_max = min(page_width, content_x_max + margin)
            
            return (content_x_min, content_y_min, content_x_max, content_y_max)
        
        except Exception as e:
            print(f"⚠ 内容区域检测失败: {e}")
            return None
    
    def detect_columns(self, page, content_bbox: Tuple[float, float, float, float]) -> List[Tuple[float, float, float, float]]:
        """
        检测栏布局
        返回: 每一栏的边界框列表 [(x0, y0, x1, y1), ...]
        """
        if not HAS_PYMUPDF:
            # 回退：假设单栏
            return [content_bbox]
        
        try:
            x0, y0, x1, y1 = content_bbox
            content_width = x1 - x0
            
            # 获取主内容区域内的文本块
            blocks = page.get_text("dict")["blocks"]
            content_blocks = [
                b for b in blocks 
                if b["type"] == 0 and 
                b["bbox"][0] >= x0 - 5 and 
                b["bbox"][2] <= x1 + 5
            ]
            
            if not content_blocks:
                return [content_bbox]
            
            # 分析水平位置分布，找出"空白列"
            num_strips = 100
            strip_width = content_width / num_strips
            occupancy = [0] * num_strips
            
            for block in content_blocks:
                bbox = block["bbox"]
                start_strip = int((bbox[0] - x0) / strip_width)
                end_strip = int((bbox[2] - x0) / strip_width)
                
                for i in range(max(0, start_strip), min(end_strip + 1, num_strips)):
                    if 0 <= i < num_strips:
                        occupancy[i] += 1
            
            # 识别显著的空白区域（栏间隙）
            gaps = []
            in_gap = False
            gap_start = 0
            min_gap_width = 5  # 最小间隙宽度（条带数）
            
            for i, occ in enumerate(occupancy):
                if occ == 0:  # 空白
                    if not in_gap:
                        gap_start = i
                        in_gap = True
                else:  # 有文本
                    if in_gap:
                        gap_width = i - gap_start
                        if gap_width >= min_gap_width:
                            gap_center = gap_start + gap_width / 2
                            gaps.append(gap_center * strip_width + x0)
                        in_gap = False
            
            # 根据间隙数量确定栏数
            if len(gaps) == 0:
                # 单栏
                return [content_bbox]
            
            # 多栏：按间隙分割
            columns = []
            prev_x = x0
            
            for gap_x in gaps:
                columns.append((prev_x, y0, gap_x, y1))
                prev_x = gap_x
            
            # 添加最后一栏
            columns.append((prev_x, y0, x1, y1))
            
            return columns
        
        except Exception as e:
            print(f"⚠ 栏检测失败: {e}, 回退到单栏模式")
            return [content_bbox]
    
    def is_noise_line(self, line: str) -> bool:
        """判断是否为噪声行"""
        line = line.strip()
        
        if not line or len(line) <= 2:
            return True
        
        for pattern in self.noise_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def clean_layout_text(self, text: str) -> str:
        """
        清理 layout=True 产生的文本
        - 移除多余空格
        - 过滤噪声行
        - 修复连字符断行
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # 跳过噪声行
            if self.is_noise_line(line):
                i += 1
                continue
            
            # 压缩行内多个空格
            line = ' '.join(line.split())
            
            # 处理连字符断行
            if line.endswith('-') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and next_line[0].islower():
                    # 合并单词
                    line = line[:-1] + next_line.split()[0]
                    # 剩余部分
                    remaining = ' '.join(next_line.split()[1:])
                    if remaining:
                        lines[i + 1] = remaining
                    else:
                        i += 1  # 跳过下一行
            
            # 处理未结束的句子（可选：可能导致误合并）
            # if (not line.endswith(('.', '!', '?', ':', ';')) and 
            #     i + 1 < len(lines)):
            #     next_line = lines[i + 1].strip()
            #     if next_line and next_line[0].islower():
            #         line = line + ' ' + next_line
            #         i += 1
            
            if line:
                cleaned_lines.append(line)
            
            i += 1
        
        return '\n'.join(cleaned_lines)
    
    def detect_structure(self, text: str) -> str:
        """
        检测文档结构，添加 Markdown 格式标记
        """
        lines = text.split('\n')
        formatted = []
        
        # 常见章节标题关键词
        section_keywords = [
            'Abstract', 'Introduction', 'Background', 'Related Work',
            'Methodology', 'Method', 'Approach', 'Implementation',
            'Results', 'Experiments', 'Evaluation', 'Discussion',
            'Conclusion', 'Future Work', 'References', 'Acknowledgments',
            'Acknowledgements', 'Appendix'
        ]
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测章节标题
            is_section = False
            for keyword in section_keywords:
                if stripped == keyword or (stripped.startswith(keyword) and len(stripped) < len(keyword) + 10):
                    formatted.append(f"\n## {stripped}\n")
                    is_section = True
                    break
            
            if not is_section:
                # 检测可能的文档标题（第一个较长的行）
                if (len(formatted) < 3 and 
                    len(stripped) > 30 and 
                    len(stripped) < 200 and
                    not stripped.endswith(('.', '!', '?'))):
                    formatted.append(f"\n# {stripped}\n")
                else:
                    formatted.append(line)
        
        return '\n'.join(formatted)
    
    def extract_page_smart(self, page_pymupdf, page_plumber, page_num: int) -> str:
        """
        智能提取单个页面
        
        Args:
            page_pymupdf: PyMuPDF 页面对象（用于布局分析）
            page_plumber: pdfplumber 页面对象（用于文本提取）
            page_num: 页码
        
        Returns:
            提取的文本
        """
        result_parts = []
        
        # 第一步：检测主内容区域
        if HAS_PYMUPDF and page_pymupdf:
            content_bbox = self.detect_content_area(page_pymupdf)
        else:
            content_bbox = None
        
        # 如果没有检测到，使用整个页面
        if content_bbox is None:
            content_bbox = (0, 0, page_plumber.width, page_plumber.height)
        
        # 第二步：检测栏布局
        if HAS_PYMUPDF and page_pymupdf:
            columns = self.detect_columns(page_pymupdf, content_bbox)
        else:
            columns = [content_bbox]
        
        # 第三步：按栏提取文本
        for col_idx, col_bbox in enumerate(columns):
            try:
                # 使用 pdfplumber 的 layout 模式提取
                col_text = page_plumber.within_bbox(col_bbox).extract_text(
                    layout=True,
                    x_tolerance=3,
                    y_tolerance=3
                )
                
                if col_text:
                    # 清理文本
                    col_text = self.clean_layout_text(col_text)
                    
                    if col_text.strip():
                        result_parts.append(col_text)
            
            except Exception as e:
                print(f"⚠ 第 {page_num} 页第 {col_idx} 栏提取失败: {e}")
        
        # 合并所有栏
        page_text = '\n\n'.join(result_parts)
        
        # 第四步：结构识别和格式化
        page_text = self.detect_structure(page_text)
        
        return page_text
    
    def extract_pdf(self, pdf_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """
        提取整个 PDF
        
        Returns:
            (markdown_text, page_stats)
        """
        markdown_parts = []
        page_stats = []
        
        # 打开 PyMuPDF 文档（用于布局分析）
        doc_pymupdf = None
        if HAS_PYMUPDF:
            try:
                doc_pymupdf = fitz.open(stream=pdf_bytes, filetype="pdf")
            except Exception as e:
                print(f"⚠ PyMuPDF 打开失败: {e}")
        
        # 打开 pdfplumber 文档（用于文本提取）
        with pdfplumber.open(BytesIO(pdf_bytes)) as doc_plumber:
            for page_num in range(len(doc_plumber.pages)):
                page_plumber = doc_plumber.pages[page_num]
                
                # 获取对应的 PyMuPDF 页面
                page_pymupdf = None
                if doc_pymupdf and page_num < doc_pymupdf.page_count:
                    page_pymupdf = doc_pymupdf.load_page(page_num)
                
                # 提取页面
                page_text = self.extract_page_smart(
                    page_pymupdf, 
                    page_plumber, 
                    page_num + 1
                )
                
                if page_text.strip():
                    markdown_parts.append(f"<!-- Page {page_num + 1} -->\n\n{page_text}")
                
                # 统计信息
                page_stats.append({
                    "page": page_num + 1,
                    "text_len": len(page_text),
                    "has_pymupdf": page_pymupdf is not None
                })
        
        # 关闭 PyMuPDF 文档
        if doc_pymupdf:
            doc_pymupdf.close()
        
        markdown = '\n\n---\n\n'.join(markdown_parts)
        return markdown, page_stats


# 便捷函数
def extract_pdf_smart(pdf_bytes: bytes) -> str:
    """
    便捷函数：使用智能提取器提取 PDF
    
    Args:
        pdf_bytes: PDF 文件的字节内容
    
    Returns:
        Markdown 格式的文本
    """
    extractor = SmartPDFExtractor()
    markdown, stats = extractor.extract_pdf(pdf_bytes)
    
    # 打印统计信息
    print(f"✓ 提取完成:")
    print(f"  - 总页数: {len(stats)}")
    print(f"  - 总字符: {sum(s['text_len'] for s in stats)}")
    if any(s['has_pymupdf'] for s in stats):
        print(f"  - 使用智能布局分析: ✓")
    else:
        print(f"  - 使用基础提取模式（建议安装 PyMuPDF 以获得更好效果）")
    
    return markdown


# 测试代码
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python smart_extractor.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print(f"正在提取: {pdf_path}")
    print("=" * 60)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    markdown = extract_pdf_smart(pdf_bytes)
    
    # 保存结果
    output_path = pdf_path.replace(".pdf", "_smart.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"\n✓ 结果已保存到: {output_path}")
    
    # 预览前500字符
    print("\n" + "=" * 60)
    print("预览:")
    print("=" * 60)
    print(markdown[:500])
