# PDF ➜ Markdown Converter

A powerful PDF to Markdown conversion tool with support for text extraction, table recognition, image extraction, and OCR.

## ✨ Features

### Core Capabilities
- ✅ Extract text content from PDFs
- ✅ Recognize and convert tables to Markdown format
- ✅ Extract images from PDFs (Base64 format)
- ✅ OCR support (Chinese & English)
- ✅ Modern web interface
- ✅ Real-time conversion preview
- ✅ Download Markdown files

### 🆕 Dual Engine Support
- **Default Engine**: pdfplumber + PyMuPDF intelligent extraction (fast)
- **Nougat Engine**: Meta AI neural network OCR (recommended for academic papers ⭐)
  - Perfect handling of two-column layouts
  - Mathematical formula recognition (LaTeX format)
  - Optimized for academic documents

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Install Nougat Engine

If you need to convert academic papers (two-column layouts), Nougat is highly recommended:

#### Method A: Use Installation Script
```bash
.\install_nougat.bat
```

#### Method B: Manual Installation
```bash
pip install nougat-ocr
```

### 3. Start the Application

```bash
python backend/main.py
```

Or using uvicorn:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

Open your browser and visit: http://localhost:8000

Select the conversion engine in the interface:
- **Default Engine**: Suitable for general PDFs, fast processing
- **Nougat Engine**: Best for academic papers, highest quality

## 📦 Tech Stack

### Backend
- **FastAPI** - High-performance web framework
- **pdfplumber** - PDF text and table extraction
- **PyMuPDF (fitz)** - PDF image extraction
- **ocrmypdf** - OCR engine
- **Tesseract** - Text recognition
- **Ghostscript** - PDF processing

### Frontend
- **Native HTML/CSS/JavaScript**
- **Modern UI design**

## 📖 Usage

### Web Interface

1. Upload PDF file (drag & drop or click to select)
2. Select conversion engine:
   - **Default Engine**: Fast conversion, suitable for general PDFs
   - **Nougat Engine**: High-quality conversion, recommended for academic papers
3. Click "Convert" button
4. View results and download

### Command Line Usage

#### Using Default Engine
```bash
# Via Web API
curl -X POST -F "file=@paper.pdf" http://localhost:8000/convert > output.json
```

#### Using Nougat Engine
```bash
# Method 1: Via Web API
curl -X POST -F "file=@paper.pdf" http://localhost:8000/convert-nougat > output.json

# Method 2: Direct Nougat command
nougat paper.pdf -o output_dir --markdown

# Method 3: Using our wrapper script
python backend/nougat_converter.py paper.pdf

# Method 4: Compare both engines
python convert_compare.py paper.pdf
```

## 🔧 OCR Configuration (Optional)

OCR is used to recognize text in scanned PDFs. **If your PDFs contain selectable text, you can skip this section.**

### Quick Check

Run the diagnostic tool to check current status:

```bash
.\check_ocr_dependencies.bat
```

### Required Tools

OCR functionality requires two external programs:

1. **Ghostscript** - PDF processing tool
   - Download: https://ghostscript.com/releases/gsdnld.html
   - Select Windows 64-bit version

2. **Tesseract OCR** - Text recognition engine
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - **Important**: Check "Chinese - Simplified" language pack during installation

### Quick Install Chinese Language Pack

If Tesseract is already installed but missing Chinese support:

```bash
.\install_chinese_pack.bat
```

Or download manually:
- Visit: https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
- Save to: `C:\Program Files\Tesseract-OCR\tessdata\`

### Detailed Installation Guide

See complete installation and configuration instructions: **[DOCS.md](./DOCS.md#ocr-功能安装指南)**

## 📂 Project Structure

```
test-pdf2md/
├── backend/
│   └── main.py                      # FastAPI main application
├── frontend/
│   ├── index.html                   # Frontend page
│   └── styles.css                   # Style file
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── README.md                        # Project documentation (this file)
├── DOCS.md                          # Complete documentation (OCR install + technical docs)
├── check_ocr_dependencies.bat      # OCR dependency checker
├── verify_chinese_language.bat     # Chinese language pack checker
└── install_chinese_pack.bat        # Chinese language pack installer
```

## 🔌 API Endpoints

### POST /convert

Upload PDF file and convert to Markdown

**Request:**
- Content-Type: multipart/form-data
- Body: PDF file

**Response:**
```json
{
  "markdown": "Converted Markdown text",
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

## ⚠️ Nougat Installation Troubleshooting

> 📚 **Complete Troubleshooting Guide**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Common Issues and Solutions

#### Issue 1: Microsoft Visual C++ 14.0 Error

**Error Message:**
```
error: Microsoft Visual C++ 14.0 is required
```

**Cause:** Missing C++ compiler, required by some Python packages.

**Solution:**
1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. Or use Python 3.10 (recommended, avoids most compilation issues)

---

#### Issue 2: Python 3.11+ Incompatibility

**Error:** Various dependency failures when installing `nougat-ocr` on Python 3.11

**Cause:** `nougat-ocr 0.1.17` (released in 2023) dependencies don't support Python 3.11+

**Solution:** Use Python 3.10
```bash
# Create Python 3.10 virtual environment
python3.10 -m venv venv_nougat
.\venv_nougat\Scripts\activate
pip install nougat-ocr
```

---

#### Issue 3: transformers Version Incompatibility

**Error Message:**
```
ImportError: cannot import name 'PretrainedConfig' from 'transformers.modeling_utils'
```

**Cause:** Installed transformers 5.0.0, but nougat requires 4.30.x

**Solution:**
```bash
pip uninstall transformers -y
pip install "transformers==4.30.2"
```

---

#### Issue 4: pydantic Validation Error

**Error Message:**
```
ValidationError: Input should be 'jpeg' or 'webp' [type=literal_error]
```

**Cause:** pydantic 2.x is incompatible with nougat

**Solution:**
```bash
pip uninstall pydantic -y
pip install "pydantic==1.10.13"
```

---

#### Issue 5: pypdfium2 Missing render Method ⭐

**Error Message:**
```
ERROR:root:'PdfDocument' object has no attribute 'render'
```

**Cause:** pypdfium2 5.x API changed, nougat requires 4.17.0

**Solution:**
```bash
pip uninstall pypdfium2 -y
pip install "pypdfium2==4.17.0"
```

---

### 🎯 One-Click Fix Script

If you encounter any of the above issues, run the fix script:

```bash
.\fix_nougat.bat
```

Or execute manually:
```bash
# In virtual environment
pip uninstall transformers pydantic pypdfium2 albumentations -y
pip install "transformers==4.30.2" "pydantic==1.10.13" "pypdfium2==4.17.0" "albumentations==1.3.1"
```

---

### 📋 Nougat Dependency Version Table

| Package | Required Version | pip Default | Consequence |
|---|---|---|---|
| Python | **3.10** | 3.11+ | Compilation failure |
| transformers | **4.30.2** | 5.0.0 | API changes, import fails |
| pydantic | **1.10.13** | 2.x | Validation logic changes |
| albumentations | **1.3.1** | 2.x | Parameter incompatibility |
| **pypdfium2** | **4.17.0** | **5.3.0** | **Missing render method** ⭐ |

**pypdfium2 version is most critical!** If you fix only one, fix this.

---

### ✅ Verify Installation

```bash
# Test if nougat works properly
nougat --help

# If you see help information without errors, installation succeeded

# Test conversion
nougat test.pdf -o . --markdown
```

---

### 💡 Post-Installation Recommendations

1. **Use Virtual Environment**
   ```bash
   # Activate virtual environment before using nougat
   .\venv_nougat\Scripts\activate
   ```

2. **Recommended Usage**
   ```bash
   # Direct command line (simplest)
   nougat paper.pdf -o . --markdown
   
   # Or use Web interface
   python backend/main.py
   # Visit http://localhost:8000 in browser
   ```

3. **Performance Optimization**
   - With GPU: 10x+ faster conversion
   - Without GPU: Test with a few pages first
   ```bash
   nougat paper.pdf -o . --pages 1-3
   ```

---

### 📝 Troubleshooting Summary

**Root Cause of Nougat Installation Difficulties:**

`nougat-ocr` was released in 2023, and its dependency environment is now outdated. As Python and dependency packages have updated, numerous incompatibility issues emerged.

**Core Solution Strategy:**

1. **Use Python 3.10** (avoids 90% of compilation issues)
2. **Downgrade 5 key dependencies** to 2023 versions
3. **Most critical is `pypdfium2==4.17.0`** (otherwise you'll encounter render errors)

**If Problems Persist:**

1. Delete virtual environment and start over
   ```bash
   rmdir /s /q venv_nougat
   python3.10 -m venv venv_nougat
   ```

2. Install with fixed versions
   ```bash
   .\venv_nougat\Scripts\activate
   pip install "pydantic==1.10.13" "transformers==4.30.2" "pypdfium2==4.17.0" "albumentations==1.3.1"
   pip install nougat-ocr
   ```

3. Fall back to default engine
   - While the default engine isn't as good for two-column PDFs as Nougat
   - It's sufficient for general documents and requires no complex configuration

---

## ❓ FAQ

### Q1: "tesseract or gs not found" error?

**Error Message:**
```
The program 'tesseract' could not be executed or was not found
The program 'gs' could not be executed or was not found
```

**Solution:**
1. Run the check tool: `.\check_ocr_dependencies.bat`
2. Follow prompts to install missing programs
3. Or see detailed guide: [DOCS.md](./DOCS.md#ocr-功能安装指南)

### Q2: OCR can't recognize Chinese?

**Error Message:**
```
OCR engine does not have language data for the following requested languages: chi_sim
```

**Solutions:**

**Method 1 (Recommended)**: Modify Tesseract installation
1. Re-run Tesseract installer
2. Select "Modify"
3. Check "Chinese - Simplified" language pack

**Method 2**: Use auto-install script
```bash
.\install_chinese_pack.bat
```

**Method 3**: Manual download
- Download: https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
- Save to: `C:\Program Files\Tesseract-OCR\tessdata\`

### Q3: How to confirm OCR is working after startup?

Check the startup logs, successful output should be:
```
✓ Found Tesseract: C:\Program Files\Tesseract-OCR\tesseract.exe
✓ Found Ghostscript (in PATH)
✓ OCR functionality enabled
✓ Chinese OCR supported (language pack installed)
   Available languages: chi_sim, eng, osd
```

If you see warnings, dependencies or language packs are missing.

### Q4: Can I skip OCR tool installation?

**Absolutely!** The application will automatically skip OCR:
- ✅ Can still extract text from text-based PDFs
- ✅ Can still extract tables and images
- ❌ Cannot recognize text in scanned PDFs

OCR is only needed for scanned PDFs.

### Q5: What type is my PDF?

**Test method:**
- Open with a PDF reader and try to select text
- Can select → Text-based PDF, no OCR needed
- Cannot select → Scanned PDF, OCR required

## 🐳 Docker Deployment

The project includes a Dockerfile for Docker deployment:

```bash
docker build -t pdf2md .
docker run -p 8000:8000 pdf2md
```

## 📦 Dependencies

Core dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pdfplumber` - PDF processing
- `pymupdf` - Image extraction
- `ocrmypdf` - OCR functionality
- `pillow` - Image processing

External dependencies (optional, for OCR):
- **Tesseract OCR** - Text recognition engine
- **Ghostscript** - PDF processing tool

## 📚 Documentation

### Core Documentation
- **[README.md](./README.md)** - Project documentation (this file)
- **[DOCS.md](./DOCS.md)** - Complete documentation (OCR installation guide + technical docs)
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Complete Nougat installation troubleshooting guide ⭐

### Nougat Related
- **[NOUGAT_GUIDE.md](./NOUGAT_GUIDE.md)** - Nougat usage guide
- **[install_nougat.bat](./install_nougat.bat)** - Nougat one-click installation script
- **[fix_nougat.bat](./fix_nougat.bat)** - Nougat dependency fix script

### OCR Tools
- **[check_ocr_dependencies.bat](./check_ocr_dependencies.bat)** - One-click OCR dependency status check
- **[verify_chinese_language.bat](./verify_chinese_language.bat)** - Check if Chinese language pack is installed
- **[install_chinese_pack.bat](./install_chinese_pack.bat)** - Auto-download and install Chinese language pack

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 💬 Contact

For questions, please submit an Issue.
