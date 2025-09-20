#!/usr/bin/env python3
"""
PDF to Text converter
- Simple usage: set input_pdf, output_txt, and pages_to_extract
- Uses PyPDF2 (pip install PyPDF2)
"""

from PyPDF2 import PdfReader
from pathlib import Path
import tiktoken
import pandas as pd
from utils.token_count import count_tokens



disease_page_dic = {
    "Neurodevelopmental Disorders": [31, 86],
    "Schizophrenia Spectrum and Other Psychotic Disorders": [87, 122],
    "Bipolar and Related Disorders": [123, 154],
    "Depressive Disorders": [155, 188],
    "Anxiety Disorders": [189, 234],
    "Obsessive-Compulsive and Related Disorders": [235, 264],
    "Trauma- and Stressor-Related Disorders": [265, 290],
    "Dissociative Disorders": [291, 308],
    "Somatic Symptom and Related Disorders": [309, 328],
    "Feeding and Eating Disorders": [329, 354],
    "Elimination Disorders": [355, 360],
    "Sleep-Wake Disorders": [361, 422],
    "Sexual Dysfunctions": [423, 450],
    "Gender Dysphoria": [451, 460],
    "Disruptive, Impulse-Control, and Conduct Disorders": [461, 480],
    "Substance-Related and Addictive Disorders": [481, 590],
    "Neurocognitive Disorders": [591, 644],
    "Personality Disorders": [645, 684],
    "Paraphilic Disorders": [685, 706],
    "Other Mental Disorders": [707, 708],
    "Medication-Induced Movement Disorders and Other Adverse Effects of Medication": [709, 714],
    "Other Conditions That May Be a Focus of Clinical Attention": [715, None]  # last section, no end page given
}



# ===== USER SETTINGS =====
input_pdf = "docs/DOC-20250318-WA0006._"        
                
# ==========================



def pdf_to_text(pdf_path: str, page_list=None) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    num_pages = len(reader.pages)

    if not page_list:  # If no page list, take all
        page_list = [0,num_pages-1]

    if page_list[1] is None:
        page_list[1] = num_pages-1

    for i in range(page_list[0], page_list[1]+1):
        if i < 0 or i >= num_pages:
            print(f"⚠️ Skipping invalid page index: {i}")
            continue
        try:
            text = reader.pages[i].extract_text() or ""
        except Exception as e:
            print(f"⚠️ Could not extract page {i}: {e}")
            text = ""
        pages.append(text)

    return "\n".join(pages)

def main():
    pdf_path = Path(input_pdf)

    data = []

    for disease in disease_page_dic:
        pages_to_extract = disease_page_dic[disease]
        l = [disease] + pages_to_extract
        pages_to_extract[0] = pages_to_extract[0] + 44
        try:
            pages_to_extract[1] = pages_to_extract[1] + 44
        except TypeError:
            pass
        output_txt = f"docs/disorders/{disease.replace('Disorders','').strip()}.txt"
        out_path = Path(output_txt)

        text = pdf_to_text(pdf_path, pages_to_extract)
        out_path.write_text(text, encoding="utf-8")

        l += [output_txt, len(text), count_tokens(text)]
        data.append(l)

        print(f"✅ Extracted {len(text)} characters to '{out_path}' with number of tokens: {count_tokens(text)}")
    
    data = pd.DataFrame(data)
    data.to_excel("docs/disorder_docs.xlsx", index=False, header=["Disease", "Start Page", "End Page", "Doc File Name", "Length", "Tokens"])

if __name__ == "__main__":
    # main()
    file = "docs/mse.pdf"
    text = pdf_to_text(pdf_path=file)
    
    out_path = Path(file.split('.')[0] + '.txt')
    out_path.write_text(text, encoding="utf-8")
