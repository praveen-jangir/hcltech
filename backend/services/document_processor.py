
import os
from pypdf import PdfReader

class DocumentProcessor:
    @staticmethod
    def extract_text(filepath):
        
        extracted_text = ""
        filename = os.path.basename(filepath)
        
        try:
            if filename.lower().endswith('.pdf'):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            elif filename.lower().endswith('.txt'):
                 with open(filepath, 'r', encoding='utf-8') as f:
                     extracted_text = f.read()
            else:
                 raise ValueError("Unsupported file type")
            
            return extracted_text
        except Exception as e:
            print(f"Error extracting text from {filename}: {e}")
            raise e

    @staticmethod
    def chunk_text(text, chunk_size=1000):
        
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]