import fitz  # PyMuPDF
import pdfplumber
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text
import camelot
import re
from PIL import Image
import pytesseract
import io

def method1_pymupdf_improved(pdf_path):
    """
    PyMuPDF with better text extraction using text blocks and positioning
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Method 1a: Extract text blocks (preserves some layout)
        text_blocks = page.get_text("blocks")
        
        # Sort blocks by their position (top to bottom, left to right)
        text_blocks.sort(key=lambda block: (block[1], block[0]))
        
        page_text = ""
        for block in text_blocks:
            if block[6] == 0:  # Text block (not image)
                page_text += block[4] + "\n"
        
        full_text += page_text + "\n"
    
    doc.close()
    return full_text

def method2_pymupdf_dict(pdf_path):
    """
    PyMuPDF with dictionary output for better structure preservation
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Extract text as dictionary with detailed information
        text_dict = page.get_text("dict")
        
        # Process blocks and lines to maintain structure
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    full_text += line_text + "\n"
                full_text += "\n"
    
    doc.close()
    return full_text

def method3_pdfplumber(pdf_path):
    """
    PDFPlumber - Often better for layout preservation
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text with layout preservation
            text = page.extract_text(layout=True)
            if text:
                full_text += text + "\n\n"
    
    # Save to text file
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    return full_text

def method4_pdfminer(pdf_path):
    """
    PDFMiner with custom layout parameters
    """
    laparams = LAParams(
        boxes_flow=0.5,
        word_margin=0.1,
        char_margin=2.0,
        line_margin=0.5,
        all_texts=False
    )
    
    text = extract_text(pdf_path, laparams=laparams)
    return text

def method5_camelot_tables(pdf_path):
    """
    Camelot for table extraction (if resume has tabular data)
    """
    try:
        tables = camelot.read_pdf(pdf_path, pages='all')
        
        extracted_text = ""
        for i, table in enumerate(tables):
            extracted_text += f"Table {i+1}:\n"
            extracted_text += table.df.to_string(index=False) + "\n\n"
        
        return extracted_text
    except Exception as e:
        return f"Error extracting tables: {str(e)}"

def method6_ocr_fallback(pdf_path):
    """
    OCR fallback using Tesseract (for image-based PDFs or better accuracy)
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Convert page to image
        mat = fitz.Matrix(2, 2)  # Scale factor for better OCR
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # OCR the image
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image)
        full_text += text + "\n\n"
    
    doc.close()
    return full_text

def method7_hybrid_approach(pdf_path):
    """
    Combine multiple methods for best results
    """
    results = {}
    
    # Try different methods
    methods = [
        ("PyMuPDF Improved", method1_pymupdf_improved),
        ("PyMuPDF Dict", method2_pymupdf_dict),
        ("PDFPlumber", method3_pdfplumber),
        ("PDFMiner", method4_pdfminer),
    ]
    
    for name, method in methods:
        try:
            results[name] = method(pdf_path)
            print(f"{name}: {len(results[name])} characters extracted")
        except Exception as e:
            results[name] = f"Error: {str(e)}"
    
    return results

def clean_extracted_text(text):
    """
    Clean up extracted text to improve readability
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common extraction issues
    text = re.sub(r'(\w)([A-Z])', r'\1 \2', text)  # Add space between words
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase separation
    
    # Remove extra newlines but preserve paragraph structure
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_resume_sections(text):
    """
    Try to identify and organize resume sections
    """
    sections = {}
    
    # Common resume section headers
    section_patterns = {
        'contact': r'(contact|phone|email|address)',
        'education': r'(education|degree|university|college)',
        'experience': r'(experience|work|employment|career)',
        'skills': r'(skills|technical|competencies)',
        'summary': r'(summary|objective|overview|profile)'
    }
    
    current_section = 'general'
    sections[current_section] = []
    
    # Handle both string and dictionary input
    if isinstance(text, dict):
        # If text is already a dictionary, return it as is
        return text
    
    # Convert text to string if it's not already
    if not isinstance(text, str):
        text = str(text)
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        section_found = False
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line.lower()):
                current_section = section_name
                sections[current_section] = []
                section_found = True
                break
        
        if not section_found:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(line)
    
    return sections

def extract(pdf_path):
    """
    Main extraction function with proper error handling
    """
    try:
        # Try the hybrid approach to compare results
        results = method7_hybrid_approach(pdf_path)
        
        # Print results from each method
        for method_name, text in results.items():
            print(f"\n{'='*50}")
            print(f"METHOD: {method_name}")
            print(f"{'='*50}")
            if isinstance(text, str):
                preview = text[:500] + "..." if len(text) > 500 else text
                print(preview)
            else:
                print(str(text))
        
        # For immediate use, try PDFPlumber first (often best for resumes)
        print("\n" + "="*50)
        print("RECOMMENDED: PDFPlumber Result")
        print("="*50)
        
        try:
            best_result = method3_pdfplumber(pdf_path)
            # if isinstance(best_result, str):
            #     best_result = clean_extracted_text(best_result)
            #     best_result = extract_resume_sections(best_result)
            return best_result
        except Exception as e:
            print(f"Error with PDFPlumber: {e}")
            print("Falling back to improved PyMuPDF...")
            fallback_result = method1_pymupdf_improved(pdf_path)
            if isinstance(fallback_result, str):
                fallback_result = clean_extracted_text(fallback_result)
                fallback_result = extract_resume_sections(fallback_result)
            return fallback_result
    
    except Exception as e:
        print(f"Error in extract function: {e}")
        return f"Error extracting PDF: {str(e)}"