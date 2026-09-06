from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
TEXT = ROOT / "data" / "text"

# Extract 01 Affidavit Format Explained
pdf = pdfplumber.open(SOURCE / '01 Affidavit Format Explained.pdf')
text = ''
for page in pdf.pages:
    t = page.extract_text()
    if t:
        text += t + '\n'
TEXT.joinpath('01_format.txt').write_text(text, encoding='utf-8')
print("01 done")

# Extract 02 Affidavit in Reply Sample
pdf = pdfplumber.open(SOURCE / '02 Affidavit in Reply Sample.docx.pdf')
text = ''
for page in pdf.pages:
    t = page.extract_text()
    if t:
        text += t + '\n'
TEXT.joinpath('02_sample.txt').write_text(text, encoding='utf-8')
print("02 done")

# Extract 03 Case Information
pdf = pdfplumber.open(SOURCE / '03_Case_Information.pdf')
text = ''
for page in pdf.pages:
    t = page.extract_text()
    if t:
        text += t + '\n'
TEXT.joinpath('03_case.txt').write_text(text, encoding='utf-8')
print("03 done")