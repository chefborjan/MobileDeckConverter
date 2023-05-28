import fitz
import io
import os
from PIL import Image

pdf_path = "/Users/ryan/Downloads/test deck Deck - v14.pdf"
doc = fitz.open(pdf_path)

for i in range(len(doc)):
    for img in doc.get_page_images(i):
        xref = img[0]
        base = img[1]
        pix = fitz.Pixmap(doc, xref)
        if pix.n < 5:  # this is GRAY or RGB
            pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        else:  # CMYK: convert to RGB first
            pix = fitz.Pixmap(fitz.csRGB, pix)
            pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pil_img.save(os.path.join("/Users/ryan/Desktop/SaaS/MobileDeckConverter/media/images", f"{base}.png"))
        pix = None  # free Pixmap resources

doc.close()
