import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# CONFIGURATION
input_root = "./"        # Replace with your nested input directory
output_folder = "output_txts"            # Flat folder to hold all .txt OCR results

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def sanitize_filename(path):
    return os.path.splitext(os.path.relpath(path, input_root).replace(os.sep, "_"))[0]

def process_image_to_txt(image: Image.Image, out_txt_path: str):
    text = pytesseract.image_to_string(image)
    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[✓] OCR text saved: {out_txt_path}")

def process_pdf(pdf_path: str, base_name: str):
    final_txt_path = os.path.join(output_folder, f"{base_name}.txt")
    if os.path.exists(final_txt_path):
        print(f"[↪] Skipping (already processed): {final_txt_path}")
        return

    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for img in images:
            full_text += pytesseract.image_to_string(img) + "\n\n"

        with open(final_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"[✓] OCR text from PDF saved: {final_txt_path}")

    except Exception as e:
        print(f"[!] Failed to process PDF {pdf_path}: {e}")

def process_image_file(img_path: str, base_name: str):
    out_txt_path = os.path.join(output_folder, f"{base_name}.txt")
    if os.path.exists(out_txt_path):
        print(f"[↪] Skipping (already processed): {out_txt_path}")
        return

    try:
        img = Image.open(img_path)
        process_image_to_txt(img, out_txt_path)
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
