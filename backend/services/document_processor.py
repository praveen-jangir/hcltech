
import os
from pypdf import PdfReader
import docx
import pandas as pd
from pptx import Presentation
from PIL import Image
import pytesseract


# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

class DocumentProcessor:
    @staticmethod
    def extract_text(filepath):
        extracted_text = ""
        filename = os.path.basename(filepath).lower()
        
        try:
            if filename.endswith('.pdf'):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    extracted_text += (page.extract_text() or "") + "\n"
            
            elif filename.endswith('.docx'):
                doc = docx.Document(filepath)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            
            elif filename.endswith(('.xlsx', '.xls', '.csv')):
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                extracted_text = df.to_string(index=False)

            elif filename.endswith('.pptx'):
                prs = Presentation(filepath)
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            extracted_text += shape.text + "\n"

            elif filename.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                image = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(image)

            elif filename.endswith('.txt'):
                 with open(filepath, 'r', encoding='utf-8') as f:
                     extracted_text = f.read()

            else:
                 raise ValueError(f"Unsupported file type: {filename}")
            
            return extracted_text.strip()
        except Exception as e:
            print(f"Error extracting text from {filename}: {e}")
            raise e

    @staticmethod
    def chunk_text(text, chunk_size=1000):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
