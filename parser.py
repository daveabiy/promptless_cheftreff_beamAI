import pandas as pd
import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import requests
import sys
import csv

import openai
from openai import OpenAI
from PIL import Image
import pytesseract
from jsonformats import ORDER_FORMAT, INVOICE_FORMAT

def name_link(data):
    # Regular expression to extract PDF name and URL
    match = re.match(r'(.+\.pdf) \((http.+)\)', data, re.IGNORECASE)
    if match:
        pdf_name = match.group(1)
        pdf_link = match.group(2)
        return pdf_name, pdf_link
    else:
        return None, None
      
def link_to_text(pdf_path, pdf_link, output_file=None):
    # Download the PDF file
    response = requests.get(pdf_link)
    with open(pdf_path, 'wb') as file:
        file.write(response.content)
    
    # Parse the PDF file using OCR
    full_text = ""
    pdf_document = fitz.open(pdf_path)
    
    # save the PDF to a 'pdf_saved'
    pdf_saved_path = os.path.join("pdf_saved", os.path.basename(pdf_path))
    os.makedirs(os.path.dirname(pdf_saved_path), exist_ok=True)
    pdf_document.save(pdf_saved_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        
        # Convert PDF page to image (higher DPI for better OCR results)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        img_bytes = pix.tobytes("png")
        
        # Create PIL Image from bytes
        img = Image.open(io.BytesIO(img_bytes))
        page_text = pytesseract.image_to_string(img)
        full_text += page_text + "\n\n"
        
            
    # Save to output file if provided
    if output_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as file:
            file.write(full_text)
    
    return full_text

def main(csv_file):
    print(f"Processing CSV file: {csv_file}")
    
    # Create output directories
    output_dir = "extracted_text_2"
    pdf_dir = "downloaded_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Read the CSV file
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip header row
        
        # Find the column containing the PDF URLs
        file_column_index = header.index('File') if 'File' in header else None
        expected_formats_index = header.index('Expected Output') if 'Expected Output' in header else None
        # print(expected_formats, file_column_index)
        if file_column_index is None:
            print("Error: 'File' column not found in CSV")
            return
        
        # Process each row
        for i, row in enumerate(csv_reader):
            if i == 21:
                if i % 10 == 0:
                    print(f"Processing row {i}...")
                    
                # Get the cell containing the PDF info
                if file_column_index < len(row):
                    file_data = row[file_column_index]
                    expected_format = row[expected_formats_index]
                    
                    # Extract PDF name and URL
                    pdf_name, pdf_link = name_link(file_data)
                    if pdf_name and pdf_link:
                        print(f"Processing: {pdf_name}")
                        
                        # Define paths
                        pdf_path = os.path.join(pdf_dir, pdf_name)
                        txt_path = os.path.join(output_dir, os.path.splitext(pdf_name)[0] + ".txt")
                        
                        try:
                            # Extract text using OCR
                            text = link_to_text(pdf_path, pdf_link, output_file=txt_path)#, method = 'ai', expected_format=expected_format)
                            print(f"Successfully processed: {pdf_name}")
                        except Exception as e:
                            print(f"Error processing {pdf_name}: {str(e)}")
                    else:
                        print(f"Could not extract PDF name and URL from: {file_data}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        main(csv_file)
    else:
        print("Usage: python parser.py <csv_file>")
        print("Example: python parser.py Testdata_Hackathon.csv")