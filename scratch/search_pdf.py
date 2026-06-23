import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Try to import PDF libraries
try:
    import pypdf
    print("pypdf is available")
except ImportError:
    pypdf = None

try:
    import pdfplumber
    print("pdfplumber is available")
except ImportError:
    pdfplumber = None

pdf_path = r"d:\AI_Agent_PLC_LADDER_ONLY\ĐỀ THI VÒNG SƠ KHẢO.pdf"
if not os.path.exists(pdf_path):
    print("Error: PDF file not found at", pdf_path)
    exit(1)

print("PDF size:", os.path.getsize(pdf_path))

if pdfplumber:
    with pdfplumber.open(pdf_path) as pdf:
        print("Pages:", len(pdf.pages))
        keywords = ["cement", "xi măng", "nghiền", "bài", "bai", "mill"]
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for kw in keywords:
                    if kw in text.lower():
                        print(f"Page {i+1} has keyword '{kw}':")
                        lines = text.split("\n")
                        for line in lines:
                            if kw in line.lower():
                                print("  ", line.strip()[:100])
else:
    print("No PDF library available to extract text.")
