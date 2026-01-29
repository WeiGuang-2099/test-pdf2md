# Nougat PDF 转换指南

## 什么是 Nougat？

Nougat（Neural Optical Understanding for Academic Documents）是 Meta 开发的神经网络模型，专门用于将学术文档（特别是 PDF）转换为 Markdown 格式。

**优势：**
- ✅ 专为学术论文设计
- ✅ 能正确处理双栏布局
- ✅ 识别数学公式（LaTeX 格式）
- ✅ 识别表格、图片
- ✅ 保留文档结构

## 快速开始

### 步骤 1: 安装

#### 方法 A: 使用安装脚本（推荐）

```bash
.\install_nougat.bat
```

#### 方法 B: 手动安装

```bash
pip install nougat-ocr
```

#### 方法 C: 使用国内镜像（网络慢时）

```bash
pip install nougat-ocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤 2: 转换 PDF

```bash
python backend/nougat_converter.py your_paper.pdf
```

**输出：** `your_paper.mmd` (Markdown格式)

### 步骤 3: 查看结果

转换后的文件在 PDF 同目录下，文件名为 `原文件名.mmd`

## 使用示例

### 基本用法

```bash
# 转换单个文件
python backend/nougat_converter.py paper.pdf

# 指定输出目录
python backend/nougat_converter.py paper.pdf output_dir
```

### 命令行直接使用

```bash
# 基本转换
nougat paper.pdf -o output_dir

# 使用 CPU（无 GPU 时）
nougat paper.pdf -o output_dir --no-cuda

# 只转换特定页面
nougat paper.pdf -o output_dir --pages 1-5
```

## 常见问题

### Q1: 首次运行很慢？

**原因：** 首次运行需要下载模型（约 350MB）

**解决：**
- 等待下载完成（只需下载一次）
- 模型保存在: `C:\Users\你的用户名\.cache\huggingface\hub`

### Q2: 内存不足错误？

**原因：** Nougat 需要较多内存（建议 8GB+）

**解决：**
1. 关闭其他占用内存的程序
2. 分批转换（一次转换少量页面）
3. 使用页面范围参数：`--pages 1-10`

### Q3: 转换速度慢？

**情况 1: 有 NVIDIA GPU**
```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**情况 2: 无 GPU（CPU模式）**
- CPU 模式较慢是正常的
- 一页约需 30-60 秒
- 建议转换时做其他事情

### Q4: 如何验证 GPU 是否启用？

```python
import torch
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"GPU 数量: {torch.cuda.device_count()}")
```

### Q5: 模型下载失败？

**原因：** 网络问题（模型在 Hugging Face 上）

**解决：**
1. 使用代理/VPN
2. 手动下载模型：
   - 访问: https://huggingface.co/facebook/nougat-base
   - 下载到: `~/.cache/huggingface/hub/`

## 性能对比

| 方法 | 速度 | 准确度 | 双栏处理 | 公式识别 |
|------|------|--------|----------|----------|
| pdfplumber | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | ❌ |
| PyMuPDF | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ | ❌ |
| Nougat | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ✅ |

## 输出格式

Nougat 输出的 Markdown 文件（.mmd）包含：

- **标题层级**: 自动识别并添加 `#`
- **段落**: 自然分段
- **数学公式**: LaTeX 格式，如 `$E=mc^2$`
- **表格**: Markdown 表格格式
- **引用**: 自动识别参考文献

## 高级配置

### 批量转换

```python
import os
from pathlib import Path

pdf_dir = "papers"
output_dir = "markdown_output"

for pdf_file in Path(pdf_dir).glob("*.pdf"):
    print(f"转换: {pdf_file.name}")
    os.system(f'nougat "{pdf_file}" -o "{output_dir}"')
```

### 集成到 FastAPI

```python
from fastapi import FastAPI, UploadFile
import subprocess
import tempfile

app = FastAPI()

@app.post("/convert-nougat")
async def convert_with_nougat(file: UploadFile):
    with tempfile.TemporaryDirectory() as tmpdir:
        # 保存上传的 PDF
        pdf_path = f"{tmpdir}/input.pdf"
        with open(pdf_path, "wb") as f:
            f.write(await file.read())
        
        # 转换
        subprocess.run(
            ["nougat", pdf_path, "-o", tmpdir],
            check=True
        )
        
        # 读取结果
        output_path = f"{tmpdir}/input.mmd"
        with open(output_path, "r", encoding="utf-8") as f:
            markdown = f.read()
        
        return {"markdown": markdown}
```

## 系统要求

### 最低配置
- Python 3.8+
- 4GB RAM
- CPU 模式

### 推荐配置
- Python 3.9+
- 8GB+ RAM
- NVIDIA GPU (6GB+ VRAM)
- CUDA 11.8+

## 资源链接

- **官方仓库**: https://github.com/facebookresearch/nougat
- **论文**: https://arxiv.org/abs/2308.13418
- **模型**: https://huggingface.co/facebook/nougat-base
- **文档**: https://facebookresearch.github.io/nougat/

## 故障排除

### 错误: "No module named 'nougat'"

```bash
pip install nougat-ocr
```

### 错误: "CUDA out of memory"

```bash
# 使用 CPU 模式
nougat paper.pdf -o output --no-cuda
```

### 错误: "Model not found"

```bash
# 清理缓存重新下载
rm -rf ~/.cache/huggingface/hub/models--facebook--nougat-base
nougat paper.pdf -o output
```

## 许可证

Nougat 使用 CC-BY-NC 许可证（非商业用途）。

商业使用请联系 Meta AI 获取授权。
