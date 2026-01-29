from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import pdfplumber
import base64
import tempfile
import os
import sys
import shutil

# 尝试导入 PyMuPDF，若环境没有安装则走降级路径
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except Exception:
    fitz = None
    HAS_FITZ = False

# 配置 OCR 依赖路径（Windows 系统）
def setup_ocr_dependencies():
    """在 Windows 上自动检测并配置 OCR 依赖（Tesseract 和 Ghostscript）"""
    tesseract_ok = False
    ghostscript_ok = False
    
    if sys.platform == "win32":
        # 1. 检查 Tesseract
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
        ]
        
        if shutil.which("tesseract"):
            tesseract_ok = True
            print("✓ 找到 Tesseract（已在 PATH 中）")
        else:
            for path in tesseract_paths:
                if os.path.exists(path):
                    tesseract_dir = os.path.dirname(path)
                    os.environ["PATH"] = tesseract_dir + os.pathsep + os.environ["PATH"]
                    tesseract_ok = True
                    print(f"✓ 找到 Tesseract: {path}")
                    break
        
        if not tesseract_ok:
            print("⚠ 警告：未找到 Tesseract OCR")
            print("   下载地址: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   安装时请勾选 'Chinese - Simplified' 语言包")
        
        # 2. 检查 Ghostscript
        ghostscript_paths = [
            r"C:\Program Files\gs\gs10.02.1\bin\gswin64c.exe",  # 最新版本
            r"C:\Program Files\gs\gs10.02.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.01.2\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.00.0\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs10.02.1\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\gs10.02.0\bin\gswin32c.exe",
        ]
        
        if shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c"):
            ghostscript_ok = True
            print("✓ 找到 Ghostscript（已在 PATH 中）")
        else:
            for path in ghostscript_paths:
                if os.path.exists(path):
                    gs_dir = os.path.dirname(path)
                    os.environ["PATH"] = gs_dir + os.pathsep + os.environ["PATH"]
                    ghostscript_ok = True
                    print(f"✓ 找到 Ghostscript: {path}")
                    break
        
        if not ghostscript_ok:
            print("⚠ 警告：未找到 Ghostscript")
            print("   下载地址: https://ghostscript.com/releases/gsdnld.html")
            print("   建议安装最新版本的 64 位版本")
        
        return tesseract_ok and ghostscript_ok
    
    # 非 Windows 系统，假设依赖已在 PATH 中
    return True

# 尝试导入 OCR 引擎（OCRMyPDF）
OCR_AVAILABLE = False
try:
    import ocrmypdf
    # 配置 OCR 依赖
    deps_ok = setup_ocr_dependencies()
    OCR_AVAILABLE = deps_ok
    
    if deps_ok:
        print("✓ OCR 功能已启用")
        # 显示可用的语言包
        try:
            langs = get_available_ocr_languages()
            if langs:
                has_chinese = "chi_sim" in langs or "chi_tra" in langs
                if has_chinese:
                    print(f"✓ 支持中文 OCR（已安装中文语言包）")
                else:
                    print(f"⚠ 中文语言包未安装，只能识别英文")
                    print(f"   安装中文包: 运行 .\\verify_chinese_language.bat 查看说明")
                print(f"   可用语言: {', '.join(langs[:10])}")  # 只显示前10个
        except Exception:
            pass
    else:
        print("⚠ OCR 功能已禁用（缺少必要的依赖）")
        print("   应用将跳过 OCR 步骤，仅提取 PDF 中的文本内容")
except Exception as e:
    ocrmypdf = None
    OCR_AVAILABLE = False
    print(f"⚠ OCR 功能已禁用: {e}")

def get_available_ocr_languages():
    """检测 Tesseract 可用的语言包"""
    try:
        result = os.popen("tesseract --list-langs 2>&1").read()
        # 解析输出，获取语言列表
        lines = result.strip().split('\n')
        languages = []
        found_list = False
        for line in lines:
            if "List of available languages" in line:
                found_list = True
                continue
            if found_list and line.strip():
                languages.append(line.strip())
        return languages
    except Exception:
        return ["eng"]  # 默认只有英文

def ocr_pdf_bytes(pdf_bytes: bytes) -> bytes | None:
    """尝试对 PDF 进行 OCR 处理，失败时返回 None"""
    if not OCR_AVAILABLE:
        return None
    
    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, "input.pdf")
        with open(in_path, "wb") as f:
            f.write(pdf_bytes)
        out_path = os.path.join(td, "output.pdf")
        
        # 检测可用的语言包
        available_langs = get_available_ocr_languages()
        
        # 构建语言参数：优先使用中英文，如果中文不可用则只用英文
        if "chi_sim" in available_langs:
            language = "eng+chi_sim"
            lang_desc = "英文+简体中文"
        elif "eng" in available_langs:
            language = "eng"
            lang_desc = "英文"
            print("⚠ 提示: 未找到中文语言包，将只使用英文 OCR")
            print("   如需中文识别，请运行: .\\verify_chinese_language.bat")
        else:
            # 使用第一个可用的语言
            language = available_langs[0] if available_langs else "eng"
            lang_desc = language
        
        try:
            print(f"正在进行 OCR 处理（{lang_desc}）...")
            ocrmypdf.ocr(
                in_path, 
                out_path, 
                language=language, 
                force_ocr=True,
                skip_text=False,
                quiet=True  # 减少输出噪音
            )
            with open(out_path, "rb") as f:
                ocr_result = f.read()
                print(f"✓ OCR 处理完成")
                return ocr_result
        except FileNotFoundError as e:
            print(f"⚠ OCR 失败: 缺少必要的工具 - {e}")
            return None
        except Exception as e:
            error_msg = str(e)
            if "language data" in error_msg.lower():
                print(f"⚠ OCR 失败: 缺少语言包")
                print(f"   请运行: .\\verify_chinese_language.bat 检查语言包")
                print(f"   或运行: .\\download_chinese_traineddata.ps1 自动下载")
            else:
                print(f"⚠ OCR 处理失败: {e}")
            print("   将使用原始 PDF 继续处理...")
            return None

def detect_content_area(page):
    """使用 PyMuPDF 检测主内容区域（排除边栏、页眉页脚）"""
    if not HAS_FITZ:
        return None
    
    try:
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b["type"] == 0]
        
        if not text_blocks:
            return None
        
        all_bboxes = [b["bbox"] for b in text_blocks]
        page_width = page.rect.width
        page_height = page.rect.height
        
        # 分析文本密度分布
        num_strips = 20
        strip_width = page_width / num_strips
        density = [0.0] * num_strips
        
        for bbox in all_bboxes:
            x0, y0, x1, y1 = bbox
            area = (x1 - x0) * (y1 - y0)
            start_strip = int(x0 / strip_width)
            end_strip = int(x1 / strip_width)
            
            for i in range(start_strip, min(end_strip + 1, num_strips)):
                if 0 <= i < num_strips:
                    density[i] += area
        
        # 找出密度显著的区域
        max_density = max(density) if density else 0
        if max_density == 0:
            return None
        
        # 使用更高的阈值来排除边栏
        threshold = max_density * 0.3  # 从 0.2 提高到 0.3
        significant_strips = [i for i, d in enumerate(density) if d > threshold]
        
        if not significant_strips:
            return None
        
        # 计算主内容区域边界
        content_x_min = min(significant_strips) * strip_width
        content_x_max = (max(significant_strips) + 1) * strip_width
        
        # 额外检查：如果左边界太靠左（可能包含边栏），强制向右移动
        if content_x_min < page_width * 0.1:  # 左边界在页面10%以内
            content_x_min = page_width * 0.12  # 强制从12%开始
        
        # Y 轴：排除最上方和最下方（页眉页脚）
        y_coords = [(bbox[1], bbox[3]) for bbox in all_bboxes]
        y_starts = sorted([y[0] for y in y_coords])
        y_ends = sorted([y[1] for y in y_coords])
        
        # 排除最上方 5% 和最下方 5%
        content_y_min = max(y_starts[0], page_height * 0.05)
        content_y_max = min(y_ends[-1], page_height * 0.95)
        
        # 添加小边距避免裁剪过度
        margin = strip_width * 0.3
        content_x_min = max(content_x_min, content_x_min - margin)
        content_x_max = min(page_width, content_x_max + margin)
        
        return (content_x_min, content_y_min, content_x_max, content_y_max)
    
    except Exception:
        return None


def detect_columns(page, content_bbox):
    """检测栏布局（单栏/双栏/多栏）"""
    if not HAS_FITZ:
        # 回退方案：简单二分（假设双栏）
        x0, y0, x1, y1 = content_bbox
        mid_x = (x0 + x1) / 2
        return [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]
    
    try:
        x0, y0, x1, y1 = content_bbox
        content_width = x1 - x0
        
        blocks = page.get_text("dict")["blocks"]
        content_blocks = [
            b for b in blocks 
            if b["type"] == 0 and 
            b["bbox"][0] >= x0 - 10 and 
            b["bbox"][2] <= x1 + 10
        ]
        
        if not content_blocks:
            # 简单二分
            mid_x = (x0 + x1) / 2
            return [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]
        
        # 收集所有文本块的中心点 X 坐标
        x_centers = []
        for block in content_blocks:
            bbox = block["bbox"]
            center_x = (bbox[0] + bbox[2]) / 2
            x_centers.append(center_x)
        
        # 如果文本块少于3个，假设双栏
        if len(x_centers) < 3:
            mid_x = (x0 + x1) / 2
            return [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]
        
        # 分析水平占用情况（更精细）
        num_strips = 200
        strip_width = content_width / num_strips
        occupancy = [0] * num_strips
        
        for block in content_blocks:
            bbox = block["bbox"]
            start_strip = int((bbox[0] - x0) / strip_width)
            end_strip = int((bbox[2] - x0) / strip_width)
            
            for i in range(max(0, start_strip), min(end_strip + 1, num_strips)):
                if 0 <= i < num_strips:
                    occupancy[i] += 1
        
        # 识别栏间隙（连续的空白区域）
        gaps = []
        in_gap = False
        gap_start = 0
        min_gap_width = 8  # 提高阈值
        
        for i, occ in enumerate(occupancy):
            if occ == 0:
                if not in_gap:
                    gap_start = i
                    in_gap = True
            else:
                if in_gap:
                    gap_width = i - gap_start
                    if gap_width >= min_gap_width:
                        gap_center = gap_start + gap_width / 2
                        gap_pos = gap_center * strip_width + x0
                        # 确保间隙在中间区域（排除边缘）
                        if gap_pos > x0 + content_width * 0.2 and gap_pos < x1 - content_width * 0.2:
                            gaps.append(gap_pos)
                    in_gap = False
        
        # 如果没有检测到间隙，使用简单二分法
        if len(gaps) == 0:
            mid_x = (x0 + x1) / 2
            return [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]
        
        # 按间隙分割成多栏
        columns = []
        prev_x = x0
        
        for gap_x in sorted(gaps):
            columns.append((prev_x, y0, gap_x, y1))
            prev_x = gap_x
        
        columns.append((prev_x, y0, x1, y1))
        return columns
    
    except Exception:
        # 异常时回退到简单二分
        x0, y0, x1, y1 = content_bbox
        mid_x = (x0 + x1) / 2
        return [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]


import re

def clean_text(text):
    """清理文本：去除噪声、修复断行"""
    if not text:
        return ""
    
    # 扩展噪声模式
    noise_patterns = [
        r'^\d+\s*$',                              # 纯数字
        r'^Page\s+\d+\s*$',                       # Page 1
        r'^\[[\w\.\s]+\]$',                       # [cs.AI]
        r'^\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}$',    # 10 Nov 2025
        r'^arXiv:\d+\.\d+v?\d*$',                 # arXiv:2511.07587v1
        r'^v\d+$',                                # v1
        r'^viXra$',                               # viXra
        r'^voN$',                                 # Nov 倒序
        r'^][\w\.]+\[$',                          # ]cs.AI[
        r'^\d+v\d+\.\d+$',                        # 1v78570.1152
        r'^[A-Z]{2,4}$',                          # 大写缩写
        r'^Copyright\s*©',                        # 版权信息
        r'^www\.',                                # 网址
        r'^\{[\w\s,@\.]+\}$',                    # 邮箱列表
    ]
    
    lines = text.split('\n')
    cleaned = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 跳过空行和过短行
        stripped = line.strip()
        if not stripped or len(stripped) <= 2:
            i += 1
            continue
        
        # 跳过噪声行
        is_noise = False
        for pattern in noise_patterns:
            if re.match(pattern, stripped):
                is_noise = True
                break
        
        # 跳过碎片化的短行（可能是边栏或被切断的文本）
        if len(stripped) < 20 and not any(keyword in stripped for keyword in ['Abstract', 'Introduction', 'Method', 'Result', 'Conclusion']):
            # 检查是否像是被切断的文本（没有句号结尾，且很短）
            if not stripped.endswith(('.', '!', '?', ':', ';', ',', ')')):
                is_noise = True
        
        if is_noise:
            i += 1
            continue
        
        # 压缩空格
        line = ' '.join(line.split())
        
        # 修复连字符断行
        if line.endswith('-') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and next_line[0].islower():
                line = line[:-1] + next_line.split()[0]
                remaining = ' '.join(next_line.split()[1:])
                if remaining:
                    lines[i + 1] = remaining
                else:
                    i += 1
        
        if line:
            cleaned.append(line)
        
        i += 1
    
    return '\n'.join(cleaned)


def detect_structure(text):
    """检测文档结构，添加 Markdown 格式"""
    lines = text.split('\n')
    formatted = []
    
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
            # 检测文档标题
            if (len(formatted) < 3 and 
                len(stripped) > 30 and 
                len(stripped) < 200 and
                not stripped.endswith(('.', '!', '?'))):
                formatted.append(f"\n# {stripped}\n")
            else:
                formatted.append(line)
    
    return '\n'.join(formatted)


def pdf_bytes_to_markdown(pdf_bytes: bytes) -> tuple[str, list]:
    """Convert PDF bytes to Markdown and per-page summaries, including images (data URLs).
    Returns (markdown_text, pages_summary).
    pages_summary: list of dicts with keys: page, text_len, table_count, table_details, images
    """
    md_lines = []
    pages = []

    # 1) 尝试 OCR 提升文本质量
    target_bytes = pdf_bytes
    if OCR_AVAILABLE:
        ocr_bytes = ocr_pdf_bytes(pdf_bytes)
        if ocr_bytes:
            target_bytes = ocr_bytes

    # 2) 使用 PyMuPDF 进行布局分析
    doc_pymupdf = None
    if HAS_FITZ:
        try:
            doc_pymupdf = fitz.open(stream=target_bytes, filetype="pdf")
        except Exception:
            pass

    # 3) 智能提取文本和表格
    with pdfplumber.open(BytesIO(target_bytes)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            page_text_parts = []
            
            # 获取 PyMuPDF 页面用于布局分析
            page_pymupdf = None
            if doc_pymupdf and idx - 1 < doc_pymupdf.page_count:
                page_pymupdf = doc_pymupdf.load_page(idx - 1)
            
            # 检测主内容区域
            if page_pymupdf:
                content_bbox = detect_content_area(page_pymupdf)
            else:
                content_bbox = None
            
            if content_bbox is None:
                # 无 PyMuPDF 时，手动排除左侧边栏和页眉页脚
                # 假设左侧边栏约占页面宽度的 10-12%
                margin_left = page.width * 0.12
                margin_top = page.height * 0.05
                margin_bottom = page.height * 0.95
                content_bbox = (margin_left, margin_top, page.width, margin_bottom)
            
            # 检测栏布局
            if page_pymupdf:
                columns = detect_columns(page_pymupdf, content_bbox)
            else:
                # 无 PyMuPDF 时，在排除边栏后的区域内二分
                x0, y0, x1, y1 = content_bbox
                mid_x = (x0 + x1) / 2
                columns = [(x0, y0, mid_x, y1), (mid_x, y0, x1, y1)]
            
            # 调试信息
            if idx == 1:
                print(f"  页面 {idx}: 检测到 {len(columns)} 栏")
                x0, y0, x1, y1 = content_bbox
                print(f"  内容区域: x=[{x0:.1f}, {x1:.1f}], y=[{y0:.1f}, {y1:.1f}]")
            
            # 按栏提取文本
            # 关键：每一栏单独提取，不使用 layout=True（会横着读）
            for col_bbox in columns:
                try:
                    # 使用 within_bbox 限制区域，然后正常提取
                    col_page = page.within_bbox(col_bbox)
                    col_text = col_page.extract_text()
                    
                    if col_text:
                        col_text = clean_text(col_text)
                        if col_text.strip():
                            page_text_parts.append(col_text)
                
                except Exception:
                    pass
            
            # 合并所有栏的文本
            page_text = '\n\n'.join(page_text_parts)
            
            # 结构识别
            if page_text:
                page_text = detect_structure(page_text)
            
            # 提取表格
            tables = page.extract_tables()
            
            # 添加到输出（不添加分页标记，自然连接段落）
            if page_text:
                md_lines.append(page_text)
                # 页面之间添加分隔（但不显示页码）
                if idx < len(pdf.pages):  # 不是最后一页
                    md_lines.append("")  # 空行分隔
            
            if tables:
                for tbl in tables:
                    if not tbl:
                        continue
                    header = tbl[0]
                    md_lines.append("| " + " | ".join((str(h) if h is not None else "" ) for h in header) + " |")
                    md_lines.append("|" + "|".join(["---"] * len(header)) + "|")
                    for row in tbl[1:]:
                        md_lines.append("| " + " | ".join((str(cell) if cell is not None else "" ) for cell in row) + " |")
                    md_lines.append("")
            
            # 统计信息
            text_len = len(page_text) if page_text else 0
            table_details = []
            if tables:
                for tbl in tables:
                    if not tbl:
                        continue
                    header = tbl[0]
                    table_details.append({"rows": len(tbl) - 1, "cols": len(header) if header else 0})
            
            per_page = {
                "page": idx, 
                "text_len": text_len, 
                "table_count": len(tables) if tables else 0, 
                "table_details": table_details, 
                "images": []
            }
            pages.append(per_page)

    # 关闭 PyMuPDF 文档
    if doc_pymupdf:
        doc_pymupdf.close()

    # 4) 图片提取（PyMuPDF）
    if HAS_FITZ:
        with fitz.open(stream=target_bytes, filetype="pdf") as doc:
            for i in range(doc.page_count):
                page = doc.load_page(i)
                imgs = page.get_images(full=True)
                data_urls = []
                for img in imgs:
                    xref = img[0]
                    base = doc.extract_image(xref)
                    image_bytes = base.get("image")
                    ext = base.get("ext", "png")
                    if image_bytes:
                        b64 = base64.b64encode(image_bytes).decode("utf-8")
                        data_urls.append(f"data:image/{ext};base64,{b64}")
                pages[i]["images"] = data_urls

    markdown = "\n".join(md_lines)
    if not markdown.strip() and any(p.get("images") for p in pages):
        markdown = "[该 PDF 可能包含图片，未检测到文本。若需要文本，请考虑对 PDF 进行 OCR。]"
    return markdown, pages

app = FastAPI(title="PDF to Markdown")

# 允许跨域（开发阶段，生产请用固定来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    content = await file.read()
    try:
        md, pages = pdf_bytes_to_markdown(content)
        return JSONResponse({"markdown": md, "pages": pages})
    except Exception as e:
        return JSONResponse({"error": f"Conversion error: {e}"}, status_code=500)


@app.post("/convert-nougat")
async def convert_nougat(file: UploadFile = File(...)):
    """使用 Nougat 转换 PDF（需要安装 nougat-ocr）"""
    import subprocess
    
    try:
        # 检查 nougat 是否可用
        try:
            import nougat
        except ImportError:
            return JSONResponse({
                "error": "Nougat 未安装。请运行: pip install nougat-ocr",
                "install_guide": "或运行: .\\install_nougat.bat"
            }, status_code=400)
        
        # 保存上传的文件到临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.pdf")
            with open(input_path, "wb") as f:
                f.write(await file.read())
            
            # 运行 nougat
            result = subprocess.run(
                ["nougat", input_path, "-o", tmpdir, "--markdown"],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                return JSONResponse({
                    "error": f"Nougat 转换失败: {result.stderr}"
                }, status_code=500)
            
            # 读取输出文件
            output_path = os.path.join(tmpdir, "input.mmd")
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as f:
                    markdown = f.read()
                
                # 返回结果（格式与原接口兼容）
                return JSONResponse({
                    "markdown": markdown,
                    "pages": [{
                        "page": 1,
                        "text_len": len(markdown),
                        "table_count": 0,
                        "table_details": [],
                        "images": []
                    }],
                    "method": "nougat"
                })
            else:
                return JSONResponse({
                    "error": "未找到 Nougat 输出文件"
                }, status_code=500)
    
    except subprocess.TimeoutExpired:
        return JSONResponse({
            "error": "转换超时（超过5分钟）"
        }, status_code=500)
    except Exception as e:
        return JSONResponse({
            "error": f"Conversion error: {e}"
        }, status_code=500)

@app.get("/convert")
async def convert_get():
    return PlainTextResponse("请通过 POST 提交 PDF 文件到 /convert 以获得 Markdown 输出。", status_code=200, media_type="text/plain")

@app.get("/", response_class=HTMLResponse)
async def root_index():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception:
        return HTMLResponse("<h1>PDF ➜ Markdown 转换器</h1>")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
