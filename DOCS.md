# PDF ➜ Markdown 转换器 - 完整文档

本文档包含项目的完整技术文档和安装指南。

**目录**
- [OCR 功能安装指南](#ocr-功能安装指南)
- [项目技术文档](#项目技术文档)

---

# OCR 功能安装指南

## 问题说明

如果您看到以下错误之一：
- `The program 'tesseract' could not be executed or was not found on your system PATH`
- `The program 'gs' could not be executed or was not found on your system PATH`
- `[WinError 2] 系统找不到指定的文件。`

这表示 OCR（光学字符识别）功能需要的外部程序未安装。

## OCR 功能需要的程序

OCR 功能依赖两个外部程序：

1. **Tesseract OCR** - 开源文字识别引擎
2. **Ghostscript** - PDF/PS 处理工具

**如果您的 PDF 文件都是文本型（可以选择复制文字），可以不安装这些工具。应用会自动跳过 OCR 步骤。**

---

## 完整安装步骤

### 第一步：安装 Ghostscript

#### 1.1 下载 Ghostscript

访问官方下载页面：
https://ghostscript.com/releases/gsdnld.html

选择下载：
- **Windows 64-bit**: `Ghostscript 10.x.x for Windows (64 bit)`
- 文件名类似：`gs10.02.1w64.exe`

#### 1.2 安装 Ghostscript

1. 运行下载的安装程序
2. 使用默认安装路径：`C:\Program Files\gs\gsX.XX.X`
3. 完成安装

#### 1.3 验证 Ghostscript 安装

打开新的 PowerShell 窗口，运行：

```powershell
gswin64c -version
```

或者：

```powershell
gs -version
```

如果显示版本信息，说明安装成功！

---

### 第二步：安装 Tesseract OCR

#### 2.1 下载 Tesseract

访问官方下载页面：
https://github.com/UB-Mannheim/tesseract/wiki

下载最新版本：
- 文件名类似：`tesseract-ocr-w64-setup-5.3.3.xxxxxxxx.exe`

#### 2.2 安装 Tesseract

1. 运行下载的安装程序
2. 在 "Choose Components" 步骤中：
   - 展开 **"Additional language data"**
   - **勾选** ✅ **"Chinese - Simplified"（简体中文）**
   - **勾选** ✅ **"Chinese - Traditional"（繁体中文）**（可选）
3. 使用默认安装路径：`C:\Program Files\Tesseract-OCR`
4. 完成安装

#### 2.3 验证 Tesseract 安装

打开新的 PowerShell 窗口，运行：

```powershell
tesseract --version
```

如果显示版本信息和语言列表，说明安装成功！

#### 2.4 确认中文语言包

检查文件是否存在：
```
C:\Program Files\Tesseract-OCR\tessdata\chi_sim.traineddata
```

如果不存在，需要重新安装 Tesseract 并勾选中文语言包。

---

## 添加中文语言包

如果已安装 Tesseract 但缺少中文语言包：

### 方法 1：修改 Tesseract 安装（推荐）

1. **重新运行安装程序**
   - 找到之前下载的 `tesseract-ocr-w64-setup-xxx.exe`
   - 如果找不到，重新下载：https://github.com/UB-Mannheim/tesseract/wiki

2. **选择 "Modify"（修改）**
   - 双击运行安装程序
   - 会检测到已安装
   - 选择 **"Modify"** 或 **"Change"** 选项

3. **添加中文语言包**
   - 在 "Choose Components" 界面
   - 展开 **"Additional language data"**
   - **勾选** ✅ **"Chinese - Simplified"** (chi_sim)
   - 可选：**勾选** ✅ **"Chinese - Traditional"** (chi_tra)

4. **完成安装**
   - 点击 "Next" → "Install"
   - 等待完成

### 方法 2：使用自动安装脚本

运行项目提供的批处理脚本：

```bash
.\install_chinese_pack.bat
```

脚本会自动：
- 从 GitHub 下载 `chi_sim.traineddata`
- 保存到正确的目录
- 验证安装结果

### 方法 3：手动下载

1. **下载语言包文件**
   - 访问：https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
   - 浏览器会自动下载 `chi_sim.traineddata` 文件（约 50MB）

2. **复制到 tessdata 目录**
   - 将下载的文件复制到：`C:\Program Files\Tesseract-OCR\tessdata\`
   - 需要管理员权限

3. **验证安装**
   ```powershell
   tesseract --list-langs
   ```
   应该能看到 `chi_sim` 在列表中

---

## 重启应用并验证

### 1. 重启所有命令行窗口

安装完成后，**必须关闭所有正在运行的 PowerShell/命令提示符窗口**，然后重新打开。

### 2. 重启 FastAPI 应用

```powershell
cd d:\codeproject\test-pdf2md
python backend/main.py
```

### 3. 检查启动日志

成功启动后，您应该看到：

```
✓ 找到 Tesseract（已在 PATH 中）
✓ 找到 Ghostscript（已在 PATH 中）
✓ OCR 功能已启用
✓ 支持中文 OCR（已安装中文语言包）
   可用语言: chi_sim, eng, osd
```

---

## 故障排查

### 问题 1: 安装后仍然提示找不到程序

**解决方案：手动添加到系统 PATH**

#### 添加 Tesseract 到 PATH：

1. 按 `Win + X`，选择 "系统"
2. 点击 "高级系统设置"
3. 点击 "环境变量"
4. 在 "系统变量" 中找到 `Path`，点击 "编辑"
5. 点击 "新建"，添加：
   ```
   C:\Program Files\Tesseract-OCR
   ```
6. 点击 "确定" 保存

#### 添加 Ghostscript 到 PATH：

同样的步骤，添加：
```
C:\Program Files\gs\gs10.02.1\bin
```

（注意：`gs10.02.1` 要替换为您实际安装的版本号）

7. **重启所有命令行窗口和应用**

### 问题 2: 不确定安装的版本号

运行以下命令查找 Ghostscript 安装路径：

```powershell
dir "C:\Program Files\gs" /s /b | findstr gswin64c.exe
```

### 问题 3: OCR 处理很慢

OCR 处理需要时间，特别是对于大型 PDF 文件。这是正常现象，请耐心等待。

### 问题 4: 中文识别效果不好

确保：
1. Tesseract 安装时已勾选简体中文语言包
2. PDF 图片质量足够高
3. 文字清晰可读

### 问题 5: 我不想使用 OCR 功能

**完全可以！** 应用会自动检测：
- 如果未安装 OCR 依赖，会跳过 OCR 步骤
- 直接提取 PDF 中的文本和表格
- 对于文本型 PDF，完全不需要 OCR

---


---

# 项目技术文档

## 📋 项目概述

这是一个基于 FastAPI 和 Python 的 Web 应用，用于将 PDF 文件转换为 Markdown 格式。支持文本提取、表格识别、图片提取和 OCR 文字识别（可选）。

## 🎯 核心功能

### 1. PDF 文本提取
- 使用 `pdfplumber` 提取 PDF 中的文本内容
- 按页分段处理，保持结构清晰
- 支持中英文文本

### 2. 表格识别与转换
- 自动识别 PDF 中的表格
- 转换为标准的 Markdown 表格格式
- 保留表头和数据结构

### 3. 图片提取
- 使用 `PyMuPDF (fitz)` 提取 PDF 中的图片
- 转换为 Base64 格式嵌入 Markdown
- 支持多种图片格式（PNG, JPEG 等）

### 4. OCR 文字识别（可选）
- 使用 `ocrmypdf` + `Tesseract` 进行 OCR
- 支持中英文识别
- 智能降级：缺少依赖时自动跳过 OCR

### 5. Web 界面
- 现代化的拖拽上传界面
- 实时显示转换结果
- 支持下载 Markdown 文件
- 显示详细的统计信息

## 🏗️ 技术架构

### 后端（FastAPI）

```
backend/main.py
├── FastAPI 应用主程序
├── OCR 依赖检测与配置
│   ├── setup_ocr_dependencies() - 检测 Tesseract 和 Ghostscript
│   └── get_available_ocr_languages() - 检测可用语言包
├── OCR 处理
│   └── ocr_pdf_bytes() - PDF OCR 处理，支持自动语言选择
└── PDF 转换
    └── pdf_bytes_to_markdown() - 完整的转换流程
```

**关键特性：**
- ✅ 智能依赖检测（Windows 路径自动搜索）
- ✅ 优雅降级（缺少 OCR 工具时仍可正常工作）
- ✅ 自动语言包检测（中文/英文自适应）
- ✅ 详细的日志输出

### 前端（原生 HTML/CSS/JS）

```
frontend/
├── index.html - 主页面
│   ├── 拖拽上传区域
│   ├── 文件选择器
│   ├── 转换按钮
│   └── 结果展示区域
└── styles.css - 现代化样式
```

**UI 特性：**
- 响应式设计
- 拖拽上传支持
- 实时进度显示
- 分页统计信息

## 📦 依赖管理

### Python 依赖（requirements.txt）

```
fastapi          # Web 框架
uvicorn          # ASGI 服务器
python-multipart # 文件上传支持
pdfplumber      # PDF 文本和表格提取
pymupdf         # PDF 图片提取
ocrmypdf        # OCR 引擎（需要外部工具）
pillow          # 图片处理
```

### 外部工具（可选，用于 OCR）

1. **Ghostscript** - PDF 处理
   - 作用：OCRMyPDF 依赖，用于 PDF 预处理
   - 安装：https://ghostscript.com/releases/gsdnld.html

2. **Tesseract OCR** - 文字识别引擎
   - 作用：识别图片中的文字
   - 语言包：chi_sim（简体中文）、eng（英文）
   - 安装：https://github.com/UB-Mannheim/tesseract/wiki

## 🔄 转换流程

```
用户上传 PDF
    ↓
FastAPI 接收文件
    ↓
检查 OCR 是否可用
    ↓
[OCR 可用] → ocrmypdf 处理 → 增强版 PDF
    ↓                              ↓
[OCR 不可用] ←―――――――――――――――――――┘
    ↓
pdfplumber 提取文本和表格
    ↓
PyMuPDF 提取图片
    ↓
生成 Markdown
    ↓
返回结果 + 统计信息
```

## 🎨 设计亮点

### 1. 智能降级策略
- OCR 工具缺失时不会报错，而是优雅降级
- 中文语言包缺失时自动使用英文 OCR
- 所有错误都有友好的提示信息

### 2. 自动检测机制
- 启动时自动检测 OCR 依赖
- 自动搜索常见安装路径（Windows）
- 自动检测可用的语言包

### 3. 用户友好
- 详细的启动日志
- 清晰的错误提示
- 提供多种解决方案
- 实用的检查和安装工具

### 4. 模块化设计
- 核心功能独立
- OCR 功能可选
- 易于扩展和维护

## 📊 功能矩阵

| 功能 | 必需依赖 | 可选依赖 | 说明 |
|------|---------|---------|------|
| 提取文本 | pdfplumber | - | 始终可用 |
| 提取表格 | pdfplumber | - | 始终可用 |
| 提取图片 | PyMuPDF | - | 始终可用 |
| OCR 识别 | ocrmypdf | Tesseract + Ghostscript | 需要外部工具 |
| 中文 OCR | - | chi_sim 语言包 | 需要语言包 |

## 🚀 使用场景

### 场景 1：文本型 PDF 转换
**需求**：转换包含文字的 PDF（如导出的文档、电子书）
**配置**：只需安装 Python 依赖
**功能**：✅ 文本 ✅ 表格 ✅ 图片

### 场景 2：扫描版 PDF 转换
**需求**：转换扫描或拍照的 PDF
**配置**：需要安装 Tesseract + Ghostscript
**功能**：✅ 文本 ✅ 表格 ✅ 图片 ✅ OCR

### 场景 3：中英文混合 PDF
**需求**：转换包含中英文的扫描版 PDF
**配置**：需要安装 OCR 工具 + 中文语言包
**功能**：✅ 文本 ✅ 表格 ✅ 图片 ✅ 中英文 OCR

## 🔧 运维建议

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境
```bash
# 使用 Docker 部署
docker build -t pdf2md .
docker run -p 8000:8000 pdf2md

# 或使用 gunicorn（多进程）
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 性能优化建议
- OCR 处理较慢，建议使用任务队列（Celery）
- 大文件处理建议设置超时时间
- 考虑添加 Redis 缓存转换结果

## 📈 未来扩展方向

### 功能扩展
- [ ] 支持批量转换
- [ ] 添加转换历史记录
- [ ] 支持更多输出格式（HTML, DOCX）
- [ ] 添加文本编辑功能
- [ ] 支持云存储集成

### 技术优化
- [ ] 异步任务队列
- [ ] WebSocket 实时进度
- [ ] 缓存机制
- [ ] API 限流
- [ ] 用户认证

### 易用性改进
- [ ] 拖拽多文件上传
- [ ] 转换进度百分比
- [ ] 预览功能
- [ ] 模板管理
- [ ] 配置面板

## 💡 最佳实践

1. **首次使用**：先运行 `check_ocr_dependencies.bat` 检查依赖
2. **文本型 PDF**：无需安装 OCR 工具
3. **扫描版 PDF**：完整安装 OCR 依赖
4. **中文 PDF**：确保安装中文语言包
5. **故障排查**：查看启动日志，使用检查工具

## 📚 相关资源

- **FastAPI 文档**：https://fastapi.tiangolo.com/
- **pdfplumber 文档**：https://github.com/jsvine/pdfplumber
- **PyMuPDF 文档**：https://pymupdf.readthedocs.io/
- **OCRMyPDF 文档**：https://ocrmypdf.readthedocs.io/
- **Tesseract 文档**：https://tesseract-ocr.github.io/

## 🎯 项目状态

✅ **核心功能**：PDF 到 Markdown 转换 - 完成
✅ **用户界面**：现代化 Web 界面 - 完成
✅ **OCR 支持**：可选的 OCR 功能 - 完成
✅ **中文支持**：中英文 OCR - 完成
✅ **易用性**：自动检测和配置 - 完成
✅ **文档完善**：完整的说明文档 - 完成
✅ **工具支持**：实用的检查和安装脚本 - 完成

**项目状态**：✅ 生产就绪

**最后更新**：2026-01-28
