"""
Script to convert TXT FNOL documents to PDF format.
Requires: pip install reportlab
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def create_pdf_from_txt(txt_file, pdf_file):
    """Convert a text file to PDF with proper formatting."""
    # Read the text file
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create PDF
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    # Set up text formatting
    y_position = height - inch
    line_height = 14
    left_margin = inch
    
    c.setFont("Helvetica", 10)
    
    for line in lines:
        # Check if we need a new page
        if y_position < inch:
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - inch
        
        # Handle bold headers (lines ending with colon)
        if line.strip().endswith(':') and not line.strip().startswith(' '):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin, y_position, line.strip())
            c.setFont("Helvetica", 10)
        else:
            c.drawString(left_margin, y_position, line.rstrip())
        
        y_position -= line_height
    
    c.save()
    print(f"Created: {pdf_file}")

def main():
    """Convert all TXT files in sample_docs to PDF."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    txt_files = [
        'fnol_fasttrack.txt',
        'fnol_investigation.txt',
        'fnol_specialist_queue.txt'
    ]
    
    for txt_file in txt_files:
        txt_path = os.path.join(script_dir, txt_file)
        pdf_file = txt_file.replace('.txt', '.pdf')
        pdf_path = os.path.join(script_dir, pdf_file)
        
        if os.path.exists(txt_path):
            create_pdf_from_txt(txt_path, pdf_path)
        else:
            print(f"Warning: {txt_path} not found")

if __name__ == '__main__':
    main()
