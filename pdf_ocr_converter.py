import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfMerger

# CONFIGURATION
input_root = "./"       # Replace with your nested input directory
output_folder = "output_pdfs"        # Flat folder to hold all searchable PDFs

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def sanitize_filename(path):
    return os.path.splitext(os.path.relpath(path, input_root).replace(os.sep, "_"))[0]

def process_image_to_pdf(image: Image.Image, out_pdf_path: str):
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    with open(out_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"[✓] Searchable PDF saved: {out_pdf_path}")

def process_pdf(pdf_path: str, base_name: str):
    try:
        images = convert_from_path(pdf_path)
        page_pdfs = []
        for i, img in enumerate(images):
            temp_pdf = os.path.join(output_folder, f"{base_name}_page_{i+1}_temp.pdf")
            process_image_to_pdf(img, temp_pdf)
            page_pdfs.append(temp_pdf)

        # Merge individual page PDFs into one searchable PDF
        final_pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
        merger = PdfMerger()
        for p in page_pdfs:
            merger.append(p)
        merger.write(final_pdf_path)
        merger.close()

        # Clean up temporary page PDFs
        for p in page_pdfs:
            os.remove(p)

    except Exception as e:
        print(f"[!] Failed to process PDF {pdf_path}: {e}")

def process_image_file(img_path: str, base_name: str):
    try:
        img = Image.open(img_path)
        out_pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
        process_image_to_pdf(img, out_pdf_path)
    except Exception as e:
        print(f"[!] Failed to process image {img_path}: {e}")

# Traverse and process all files in the input directory
for root, _, files in os.walk(input_root):
    for file in files:
        file_path = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        base_name = sanitize_filename(file_path)

        if ext == ".pdf":
            process_pdf(file_path, base_name)
        elif ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
            process_image_file(file_path, base_name)
