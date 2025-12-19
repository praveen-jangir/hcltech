import os
import pdfplumber
import fitz
import pytesseract

from PIL import Image

images_dir = "extracted_images"
os.makedirs(images_dir, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text_by_page(pdf_path):
    page_texts = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_texts[page_number] = text.strip()

    return page_texts

def needs_ocr(text, min_chars=200):
    """
    Decide whether OCR is required based on extracted text quality.
    """
    return len(text.strip()) < min_chars


def extract_page_as_image(pdf_path, page_number, output_dir="temp_images"):
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    page = doc[page_number]

    pix = page.get_pixmap(dpi=300)
    image_path = os.path.join(output_dir, f"page_{page_number}.png")
    pix.save(image_path)

    return [image_path]



def ocr_images(image_paths):
    ocr_text = ""

    for image_path in image_paths:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        ocr_text += text + "\n"

    return ocr_text.strip()

def process_pdf(pdf_path):
    page_text_dict = {}

    page_texts = extract_text_by_page(pdf_path)

    for page_number, text in page_texts.items():
        if needs_ocr(text):
            print(f"Extracting OCR Text in file {pdf_path} at page {page_number}")
            image_paths = extract_page_as_image(
                pdf_path,
                page_number,
                output_dir="temp_images"
            )
            ocr_text = ocr_images(image_paths)
            page_text_dict[page_number] = ocr_text
        else:
            page_text_dict[page_number] = text

    return page_text_dict

files = ["ml.pdf", "HCL_Plan.pdf", "grp6.pdf"]
for file in files:
    d = process_pdf(file)
    #page_c = 1
    content = ""
    for page in d:
        content += f"Page number {page}: {d[page]}\n"
    print("--------------------------------------------------------")
    print(file)
    print(content)
    print("--------------------------------------------------------")