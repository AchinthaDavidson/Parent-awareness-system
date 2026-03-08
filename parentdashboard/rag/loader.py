"""
PDF loader module for RAG pipeline.
Loads PDFs from the knowledge base directory.
"""
import os
from pathlib import Path
from typing import List
import PyPDF2
from parentdashboard.config import PDFS_DIR


def load_pdfs() -> List[dict]:
    """
    Load all PDF files from the PDFs directory.
    
    Returns:
        List of dictionaries containing 'text' and 'source' (filename) for each page.
    """
    pdf_data = []
    
    if not PDFS_DIR.exists():
        PDFS_DIR.mkdir(parents=True, exist_ok=True)
        return pdf_data
    
    # Get all PDF files
    pdf_files = list(PDFS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        return pdf_data
    
    for pdf_path in pdf_files:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        pdf_data.append({
                            'text': text,
                            'source': pdf_path.name,
                            'page': page_num + 1
                        })
        except Exception as e:
            print(f"Error loading PDF {pdf_path.name}: {str(e)}")
            continue
    
    return pdf_data


def load_single_pdf(filename: str) -> List[dict]:
    """
    Load a single PDF file by filename.
    
    Args:
        filename: Name of the PDF file to load
    
    Returns:
        List of dictionaries containing 'text' and 'source' (filename) for each page.
    """
    pdf_data = []
    
    if not PDFS_DIR.exists():
        return pdf_data
    
    pdf_path = PDFS_DIR / filename
    
    if not pdf_path.exists():
        return pdf_data
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pdf_data.append({
                        'text': text,
                        'source': filename,
                        'page': page_num + 1
                    })
    except Exception as e:
        print(f"Error loading PDF {filename}: {str(e)}")
        return []
    
    return pdf_data
