# Nougat 安装故障排除完整指南

本文档记录了在 Windows 上安装 `nougat-ocr` 时遇到的所有问题和解决方案。

## 目录
- [问题概述](#问题概述)
- [环境要求](#环境要求)
- [详细问题列表](#详细问题列表)
- [完整解决方案](#完整解决方案)
- [快速修复](#快速修复)

---

## 问题概述

`nougat-ocr 0.1.17` 发布于 2023 年，其依赖的包版本已经过时。使用 `pip install nougat-ocr` 会安装最新版本的依赖，导致各种不兼容问题。

### 核心矛盾

| 组件 | Nougat 需要 | pip 默认安装 | 结果 |
|------|-----------|------------|------|
| Python | 3.10 | 3.11+ | 编译失败 |
| transformers | 4.30.x | 5.0.0 | API 不存在 |
| pydantic | 1.10.x | 2.x | 验证失败 |
| pypdfium2 | 4.17.0 | 5.3.0 | 方法缺失 ⭐ |

---

## 环境要求

### 推荐配置 ✅
- **Python 3.10** (必须)
- Windows 10/11
- 8GB+ RAM
- （可选）NVIDIA GPU + CUDA

### 不推荐 ❌
- Python 3.11+ (依赖包不兼容)
- Python 3.9- (太旧)
- 32位 Python

---

## 详细问题列表

### 问题 1: 安装时编译错误

**完整错误信息：**
```
error: Microsoft Visual C++ 14.0 is required. Get it with "Build Tools for Visual Studio"
Building wheel for pyarrow failed
ERROR: Failed to build 'pyarrow' when installing build dependencies for pyarrow
```

**原因分析：**
- `pyarrow`、`scipy` 等包需要 C++ 编译器
- Python 3.11+ 需要编译更多包
- Windows 默认没有 C++ 编译环境

**解决方案：**

**方法 1: 安装编译工具（费时）**
1. 下载 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. 安装时选择 "C++ 生成工具"
3. 重新运行 `pip install nougat-ocr`

**方法 2: 使用 Python 3.10（推荐）**
```bash
# 下载安装 Python 3.10
# https://www.python.org/downloads/release/python-31011/

# 创建虚拟环境
python3.10 -m venv venv_nougat
.\venv_nougat\Scripts\activate
pip install nougat-ocr
```

---

### 问题 2: transformers 导入错误

**完整错误信息：**
```python
Traceback (most recent call last):
  File "...", line 1, in <module>
    from nougat import NougatModel
  ...
ImportError: cannot import name 'PretrainedConfig' from 'transformers.modeling_utils'
```

**原因分析：**
- `transformers 5.0.0` 重构了 API
- `PretrainedConfig` 被移动或重命名
- Nougat 0.1.17 使用的是 4.30.x 的 API

**验证问题：**
```python
python -c "import transformers; print(transformers.__version__)"
# 如果输出 5.0.0，就是这个问题
```

**解决方案：**
```bash
pip uninstall transformers -y
pip install "transformers==4.30.2"
```

---

### 问题 3: pydantic 验证错误

**完整错误信息：**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for InitSchema
jpeg_quality
  Input should be 'jpeg' or 'webp' [type=literal_error, input_value=95, input_type=int]
```

**原因分析：**
- pydantic 2.x 验证逻辑更严格
- `albumentations` 包使用旧的 pydantic 1.x API
- 类型检查失败

**解决方案：**
```bash
pip uninstall pydantic -y
pip install "pydantic==1.10.13"
```

---

### 问题 4: albumentations 警告

**完整错误信息：**
```
UserWarning: Passing `quality` as a keyword argument is deprecated. Use `jpeg_quality` instead.
```

**原因分析：**
- albumentations 2.x 参数名变化
- 向后兼容性问题

**解决方案：**
```bash
pip uninstall albumentations -y
pip install "albumentations==1.3.1"
```

---

### 问题 5: pypdfium2 render 方法缺失 ⭐⭐⭐

**完整错误信息：**
```
ERROR:root:'PdfDocument' object has no attribute 'render'
ERROR:root:list index out of range
[Repeated multiple times for each page]
```

**原因分析：**
- **这是最关键的问题！**
- pypdfium2 5.x 完全重写了 API
- `PdfDocument.render()` 方法被移除
- Nougat 依赖这个方法渲染 PDF 页面

**验证问题：**
```python
python -c "import pypdfium2; print(pypdfium2.__version__)"
# 如果输出 5.x，必须降级
```

**解决方案：**
```bash
pip uninstall pypdfium2 -y
pip install "pypdfium2==4.17.0"
```

**为什么这个最关键？**
- 其他问题会阻止安装，但这个问题会在运行时失败
- 症状是 nougat 运行但输出空白
- 难以诊断（错误信息不明显）

---

## 完整解决方案

### 方案 A: 全新安装（推荐）

```bash
# 1. 删除旧虚拟环境（如果存在）
rmdir /s /q venv_nougat

# 2. 使用 Python 3.10 创建虚拟环境
python3.10 -m venv venv_nougat

# 3. 激活虚拟环境
.\venv_nougat\Scripts\activate

# 4. 升级 pip
python -m pip install --upgrade pip setuptools wheel

# 5. 先安装关键依赖（固定版本）
pip install "pydantic==1.10.13"
pip install "transformers==4.30.2"
pip install "pypdfium2==4.17.0"
pip install "albumentations==1.3.1"

# 6. 安装 nougat-ocr
pip install nougat-ocr

# 7. 验证安装
nougat --help
```

### 方案 B: 修复现有安装

```bash
# 在已激活的虚拟环境中
.\venv_nougat\Scripts\activate

# 卸载问题包
pip uninstall transformers pydantic pypdfium2 albumentations -y

# 安装正确版本
pip install "transformers==4.30.2" "pydantic==1.10.13" "pypdfium2==4.17.0" "albumentations==1.3.1"

# 验证
nougat --help
```

---

## 快速修复

### 一键修复脚本

我们提供了自动修复脚本：

```bash
.\fix_nougat.bat
```

**脚本内容：**
```batch
@echo off
echo Fixing Nougat Dependencies...

pip uninstall transformers pydantic pypdfium2 albumentations -y -q
pip install "transformers==4.30.2" "pydantic==1.10.13" "pypdfium2==4.17.0" "albumentations==1.3.1" -q

echo.
echo Testing Nougat...
nougat --help

echo.
echo Done! If you see help text above, Nougat is ready to use.
pause
```

---

## 验证和测试

### 1. 验证安装

```bash
# 应该显示帮助信息，无错误
nougat --help
```

### 2. 验证依赖版本

```python
import transformers
import pydantic
import pypdfium2
import albumentations

print(f"transformers: {transformers.__version__}")  # 应该是 4.30.x
print(f"pydantic: {pydantic.__version__}")  # 应该是 1.10.x
print(f"pypdfium2: {pypdfium2.__version__}")  # 应该是 4.17.0
print(f"albumentations: {albumentations.__version__}")  # 应该是 1.3.x
```

### 3. 测试转换

```bash
# 转换测试 PDF
nougat test.pdf -o . --markdown

# 应该生成 test.mmd 文件，无 ERROR 信息
```

---

## 常见错误和快速诊断

| 症状 | 可能原因 | 快速修复 |
|------|---------|---------|
| 安装时编译失败 | Python 3.11+ | 使用 Python 3.10 |
| `PretrainedConfig` 导入错误 | transformers 5.x | `pip install "transformers==4.30.2"` |
| ValidationError | pydantic 2.x | `pip install "pydantic==1.10.13"` |
| `'PdfDocument' has no attribute 'render'` | pypdfium2 5.x | `pip install "pypdfium2==4.17.0"` ⭐ |
| nougat 运行但输出空白 | pypdfium2 5.x | 同上 ⭐ |
| 大量 ERROR 日志 | 多个依赖版本错误 | 运行 `.\fix_nougat.bat` |

---

## 为什么会这么复杂？

### 技术债务积累

1. **Nougat 0.1.17 (2023.8)** 发布时使用当时的最新依赖
2. **2023-2024** 各依赖包持续更新：
   - transformers 4.x → 5.x (API 重构)
   - pydantic 1.x → 2.x (完全重写)
   - pypdfium2 4.x → 5.x (API 重构)
3. **Nougat 未更新** 仍然依赖旧版本 API
4. **pip install** 默认安装最新版本，导致不兼容

### 教训

- 依赖管理很重要（requirements.txt 应该锁定版本）
- API 重构应该保持向后兼容
- 开源项目需要持续维护

---

## 替代方案

如果实在无法安装 Nougat：

### 1. 使用默认引擎
```bash
# 项目自带的 pdfplumber + PyMuPDF 方案
python backend/main.py
# 访问 http://localhost:8000
```

**优点：**
- 安装简单
- 速度快

**缺点：**
- 双栏 PDF 可能横着读
- 无法识别数学公式

### 2. 使用在线服务
- [Mathpix](https://mathpix.com/) - 商业服务，效果好
- [marker-pdf](https://github.com/VikParuchuri/marker) - 类似 Nougat，可能更新

### 3. 使用 Docker
```bash
docker pull ghcr.io/facebookresearch/nougat
docker run -it --rm -v $(pwd):/data ghcr.io/facebookresearch/nougat nougat /data/paper.pdf -o /data/
```

**优点：**
- 无需安装依赖
- 环境隔离

**缺点：**
- 需要 Docker
- 无 GPU 支持（Docker Desktop on Windows）

---

## 成功案例

经过以上步骤，成功安装并使用 Nougat 的环境配置：

```
操作系统: Windows 11
Python: 3.10.11
虚拟环境: venv

关键依赖版本:
- nougat-ocr: 0.1.17
- transformers: 4.30.2
- pydantic: 1.10.13
- pypdfium2: 4.17.0
- albumentations: 1.3.1
- torch: 2.1.0 (CUDA 11.8)

使用方式:
nougat paper.pdf -o . --markdown

结果: 完美转换双栏学术论文，无错误
```

---

## 参考资源

- [Nougat GitHub](https://github.com/facebookresearch/nougat)
- [Nougat 论文](https://arxiv.org/abs/2308.13418)
- [pypdfium2 文档](https://pypdfium2.readthedocs.io/)
- [transformers 4.30 文档](https://huggingface.co/docs/transformers/v4.30.0)

---

## 贡献

遇到新问题？欢迎提交 Issue 或 PR！

最后更新: 2026-01-29
