# PDF ➜ Markdown 转换器

一个功能强大的 PDF 转 Markdown 转换工具，支持文本提取、表格识别、图片提取和 OCR 识别。

## ✨ 功能特性

### 核心功能
- ✅ 提取 PDF 中的文本内容
- ✅ 识别并转换表格为 Markdown 格式
- ✅ 提取 PDF 中的图片（Base64 格式）
- ✅ OCR 识别（支持中英文）
- ✅ 现代化的 Web 界面
- ✅ 实时预览转换结果
- ✅ 下载 Markdown 文件

### 🆕 双引擎支持
- **默认引擎**：pdfplumber + PyMuPDF 智能提取（快速）
- **Nougat 引擎**：Meta AI 神经网络 OCR（学术论文推荐⭐）
  - 完美处理双栏布局
  - 识别数学公式（LaTeX 格式）
  - 专为学术文档优化

## 🚀 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. （可选）安装 Nougat 引擎

如果你需要转换学术论文（双栏布局），强烈推荐安装 Nougat：

#### 方法 A：使用安装脚本
```bash
.\install_nougat.bat
```

#### 方法 B：手动安装
```bash
pip install nougat-ocr
```

### 3. 启动应用

```bash
python backend/main.py
```

或使用 uvicorn：

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问应用

打开浏览器访问：http://localhost:8000

在界面中选择转换引擎：
- **默认引擎**：适合一般 PDF，速度快
- **Nougat 引擎**：适合学术论文，效果最佳

## 📦 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **pdfplumber** - PDF 文本和表格提取
- **PyMuPDF (fitz)** - PDF 图片提取
- **ocrmypdf** - OCR 引擎
- **Tesseract** - 文字识别
- **Ghostscript** - PDF 处理

### 前端
- **原生 HTML/CSS/JavaScript**
- **现代化 UI 设计**

## 📖 使用方法

### Web 界面

1. 上传 PDF 文件（拖拽或点击选择）
2. 选择转换引擎：
   - **默认引擎**：快速转换，适合一般 PDF
   - **Nougat 引擎**：高质量转换，推荐学术论文
3. 点击"转换"按钮
4. 查看结果并下载

### 命令行使用

#### 使用默认引擎
```bash
# 通过 Web API
curl -X POST -F "file=@paper.pdf" http://localhost:8000/convert > output.json
```

#### 使用 Nougat 引擎
```bash
# 方法1: 通过 Web API
curl -X POST -F "file=@paper.pdf" http://localhost:8000/convert-nougat > output.json

# 方法2: 直接使用 Nougat 命令
nougat paper.pdf -o output_dir --markdown

# 方法3: 使用我们的包装脚本
python backend/nougat_converter.py paper.pdf

# 方法4: 对比两种引擎效果
python convert_compare.py paper.pdf
```

## 🔧 OCR 功能配置（可选）

OCR 功能用于识别扫描版 PDF 中的文字。**如果您的 PDF 都是文本型（可选择文字），可以跳过此步骤。**

### 快速检查

运行诊断工具查看当前状态：

```bash
.\check_ocr_dependencies.bat
```

### 需要安装的工具

OCR 功能需要两个外部程序：

1. **Ghostscript** - PDF 处理工具
   - 下载：https://ghostscript.com/releases/gsdnld.html
   - 选择 Windows 64-bit 版本

2. **Tesseract OCR** - 文字识别引擎
   - 下载：https://github.com/UB-Mannheim/tesseract/wiki
   - **重要**：安装时勾选 "Chinese - Simplified"（简体中文）语言包

### 快速安装中文语言包

如果已安装 Tesseract 但缺少中文包：

```bash
.\install_chinese_pack.bat
```

或手动下载：
- 访问：https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
- 保存到：`C:\Program Files\Tesseract-OCR\tessdata\`

### 详细安装指南

查看完整的安装和配置说明：**[DOCS.md](./DOCS.md#ocr-功能安装指南)**

## 📂 项目结构

```
test-pdf2md/
├── backend/
│   └── main.py                      # FastAPI 应用主文件
├── frontend/
│   ├── index.html                   # 前端页面
│   └── styles.css                   # 样式文件
├── requirements.txt                 # Python 依赖
├── Dockerfile                       # Docker 配置
├── README.md                        # 项目说明（本文件）
├── DOCS.md                          # 完整文档（OCR 安装 + 技术文档）
├── check_ocr_dependencies.bat      # OCR 依赖检查工具
├── verify_chinese_language.bat     # 中文语言包检查工具
└── install_chinese_pack.bat        # 中文语言包安装工具
```

## 🔌 API 接口

### POST /convert

上传 PDF 文件并转换为 Markdown

**请求：**
- Content-Type: multipart/form-data
- Body: PDF 文件

**响应：**
```json
{
  "markdown": "转换后的 Markdown 文本",
  "pages": [
    {
      "page": 1,
      "text_len": 1234,
      "table_count": 2,
      "table_details": [{"rows": 5, "cols": 3}],
      "images": ["data:image/png;base64,..."]
    }
  ]
}
```

## ⚠️ Nougat 安装故障排除

> 📚 **完整故障排除指南**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### 常见问题和解决方案

#### 问题 1: Microsoft Visual C++ 14.0 错误

**错误信息：**
```
error: Microsoft Visual C++ 14.0 is required
```

**原因：** 缺少 C++ 编译器，某些 Python 包需要编译。

**解决方案：**
1. 下载安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. 或使用 Python 3.10（推荐，避免大部分编译问题）

---

#### 问题 2: Python 3.11+ 不兼容

**错误：** 在 Python 3.11 上安装 `nougat-ocr` 各种依赖失败

**原因：** `nougat-ocr 0.1.17` (2023年发布) 依赖的包不支持 Python 3.11+

**解决方案：** 使用 Python 3.10
```bash
# 创建 Python 3.10 虚拟环境
python3.10 -m venv venv_nougat
.\venv_nougat\Scripts\activate
pip install nougat-ocr
```

---

#### 问题 3: transformers 版本不兼容

**错误信息：**
```
ImportError: cannot import name 'PretrainedConfig' from 'transformers.modeling_utils'
```

**原因：** 安装了 transformers 5.0.0，但 nougat 需要 4.30.x

**解决方案：**
```bash
pip uninstall transformers -y
pip install "transformers==4.30.2"
```

---

#### 问题 4: pydantic 验证错误

**错误信息：**
```
ValidationError: Input should be 'jpeg' or 'webp' [type=literal_error]
```

**原因：** pydantic 2.x 与 nougat 不兼容

**解决方案：**
```bash
pip uninstall pydantic -y
pip install "pydantic==1.10.13"
```

---

#### 问题 5: pypdfium2 render 方法缺失 ⭐

**错误信息：**
```
ERROR:root:'PdfDocument' object has no attribute 'render'
```

**原因：** pypdfium2 5.x API 变化，nougat 需要 4.17.0

**解决方案：**
```bash
pip uninstall pypdfium2 -y
pip install "pypdfium2==4.17.0"
```

---

### 🎯 一键修复脚本

如果遇到上述任何问题，运行修复脚本：

```bash
.\fix_nougat.bat
```

或手动执行：
```bash
# 在虚拟环境中
pip uninstall transformers pydantic pypdfium2 albumentations -y
pip install "transformers==4.30.2" "pydantic==1.10.13" "pypdfium2==4.17.0" "albumentations==1.3.1"
```

---

### 📋 Nougat 依赖版本对照表

| 包 | 需要版本 | pip 默认安装 | 后果 |
|---|---|---|---|
| Python | **3.10** | 3.11+ | 编译失败 |
| transformers | **4.30.2** | 5.0.0 | API 变化，导入失败 |
| pydantic | **1.10.13** | 2.x | 验证逻辑变化 |
| albumentations | **1.3.1** | 2.x | 参数不兼容 |
| **pypdfium2** | **4.17.0** | **5.3.0** | **render 方法缺失** ⭐ |

**最关键的是 pypdfium2 版本！** 如果只修复一个，就修复这个。

---

### ✅ 验证安装

```bash
# 测试 nougat 是否正常工作
nougat --help

# 如果看到帮助信息且无错误，说明安装成功

# 测试转换
nougat test.pdf -o . --markdown
```

---

### 💡 成功安装后的建议

1. **使用虚拟环境**
   ```bash
   # 每次使用 nougat 前激活虚拟环境
   .\venv_nougat\Scripts\activate
   ```

2. **推荐使用方式**
   ```bash
   # 直接命令行（最简单）
   nougat paper.pdf -o . --markdown
   
   # 或使用 Web 界面
   python backend/main.py
   # 浏览器访问 http://localhost:8000
   ```

3. **性能优化**
   - 有 GPU：转换速度快 10 倍+
   - 无 GPU：可以先转换几页测试
   ```bash
   nougat paper.pdf -o . --pages 1-3
   ```

---

### 📝 故障排除经验总结

**Nougat 安装困难的根本原因：**

`nougat-ocr` 发布于 2023 年，当时的依赖环境已经过时。随着 Python 和各个依赖包的更新，出现了大量不兼容问题。

**核心解决策略：**

1. **使用 Python 3.10**（避免 90% 的编译问题）
2. **降级 5 个关键依赖包**到 2023 年的版本
3. **最关键是 `pypdfium2==4.17.0`**（否则会遇到 render 错误）

**如果仍有问题：**

1. 删除虚拟环境重新开始
   ```bash
   rmdir /s /q venv_nougat
   python3.10 -m venv venv_nougat
   ```

2. 使用固定版本安装
   ```bash
   .\venv_nougat\Scripts\activate
   pip install "pydantic==1.10.13" "transformers==4.30.2" "pypdfium2==4.17.0" "albumentations==1.3.1"
   pip install nougat-ocr
   ```

3. 实在不行，使用默认引擎
   - 虽然默认引擎对双栏PDF效果不如 Nougat
   - 但对一般文档已经够用，且无需复杂配置

---

## ❓ 常见问题

### Q1: 提示找不到 tesseract 或 gs？

**错误信息：**
```
The program 'tesseract' could not be executed or was not found
The program 'gs' could not be executed or was not found
```

**解决方案：**
1. 运行检查工具：`.\check_ocr_dependencies.bat`
2. 按照提示安装缺失的程序
3. 或查看详细指南：[DOCS.md](./DOCS.md#ocr-功能安装指南)

### Q2: OCR 无法识别中文？

**错误信息：**
```
OCR engine does not have language data for the following requested languages: chi_sim
```

**解决方案：**

**方法 1（推荐）**：修改 Tesseract 安装
1. 重新运行 Tesseract 安装程序
2. 选择 "Modify"
3. 勾选 "Chinese - Simplified" 语言包

**方法 2**：使用自动安装脚本
```bash
.\install_chinese_pack.bat
```

**方法 3**：手动下载
- 下载：https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
- 保存到：`C:\Program Files\Tesseract-OCR\tessdata\`

### Q3: 启动后如何确认 OCR 功能可用？

查看启动日志，成功的输出应该是：
```
✓ 找到 Tesseract: C:\Program Files\Tesseract-OCR\tesseract.exe
✓ 找到 Ghostscript（已在 PATH 中）
✓ OCR 功能已启用
✓ 支持中文 OCR（已安装中文语言包）
   可用语言: chi_sim, eng, osd
```

如果看到警告，说明缺少依赖或语言包。

### Q4: 可以不安装 OCR 工具吗？

**完全可以！** 应用会自动跳过 OCR 步骤：
- ✅ 仍可提取文本型 PDF 的内容
- ✅ 仍可提取表格和图片
- ❌ 无法识别扫描版 PDF 中的文字

只有处理扫描版 PDF 时才需要 OCR 功能。

### Q5: 我的 PDF 是哪种类型？

**测试方法：**
- 用 PDF 阅读器打开，尝试选择文字
- 能选择 → 文本型 PDF，无需 OCR
- 不能选择 → 扫描版 PDF，需要 OCR

## 🐳 Docker 部署

项目包含 Dockerfile，可使用 Docker 部署：

```bash
docker build -t pdf2md .
docker run -p 8000:8000 pdf2md
```

## 📦 依赖说明

核心依赖：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `pdfplumber` - PDF 处理
- `pymupdf` - 图片提取
- `ocrmypdf` - OCR 功能
- `pillow` - 图片处理

外部依赖（可选，用于 OCR）：
- **Tesseract OCR** - 文字识别引擎
- **Ghostscript** - PDF 处理工具

## 📚 相关文档

### 核心文档
- **[README.md](./README.md)** - 项目说明（本文件）
- **[DOCS.md](./DOCS.md)** - 完整文档（OCR 安装指南 + 项目技术文档）
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Nougat 安装故障排除完整指南 ⭐

### Nougat 相关
- **[NOUGAT_GUIDE.md](./NOUGAT_GUIDE.md)** - Nougat 使用指南
- **[install_nougat.bat](./install_nougat.bat)** - Nougat 一键安装脚本
- **[fix_nougat.bat](./fix_nougat.bat)** - Nougat 依赖修复脚本

### OCR 工具
- **[check_ocr_dependencies.bat](./check_ocr_dependencies.bat)** - 一键检查 OCR 依赖状态
- **[verify_chinese_language.bat](./verify_chinese_language.bat)** - 检查中文语言包是否安装
- **[install_chinese_pack.bat](./install_chinese_pack.bat)** - 自动下载并安装中文语言包

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 💬 联系方式

如有问题，请提交 Issue。
