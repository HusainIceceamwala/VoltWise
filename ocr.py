import os
import shutil

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes


def _find_executable(candidates):
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return candidate

    for candidate in candidates:
        if not candidate:
            continue
        found = shutil.which(candidate)
        if found:
            return found

    return None


def _resolve_tesseract_path():
    candidates = [
        os.environ.get("TESSERACT_PATH"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    tesseract_path = _find_executable(candidates)
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    return tesseract_path


def _resolve_poppler_path():
    candidates = [
        os.environ.get("POPPLER_PATH"),
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files\Poppler\bin",
        r"C:\Program Files (x86)\Poppler\bin",
        r"C:\Users\husai\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin",
        r"C:\Program Files\Git\mingw64\bin",
        r"C:\Users\DELL\poppler-26.02.0\Library\bin",
    ]
    required_bins = ["pdftoppm", "pdftocairo"]

    for candidate in candidates:
        if not candidate or not os.path.isdir(candidate):
            continue
        for binary in required_bins:
            exe_path = os.path.join(candidate, f"{binary}.exe")
            if os.path.exists(exe_path):
                return candidate

    poppler_bins = ["pdftoppm", "pdftocairo", "pdfinfo"]
    for binary in poppler_bins:
        found = _find_executable([binary])
        if found:
            return os.path.dirname(found)

    return None


TESSERACT_PATH = _resolve_tesseract_path()
POPPLER_PATH = _resolve_poppler_path()


def _preprocess_image(image):
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)


def extract_text(uploaded_file, poppler_path=None, tesseract_path=None):
    """
    Extract text from uploaded PDF or image.
    """

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    elif not TESSERACT_PATH:
        raise RuntimeError(
            "Tesseract was not found. Install Tesseract OCR or set TESSERACT_PATH. "
            "You can also provide the executable path in the app."
        )

    extension = uploaded_file.name.split(".")[-1].lower()

    if extension == "pdf":
        pdf_bytes = uploaded_file.getvalue()
        convert_kwargs = {"dpi": 300}
        if poppler_path:
            convert_kwargs["poppler_path"] = poppler_path

        try:
            pages = convert_from_bytes(pdf_bytes, **convert_kwargs)
        except Exception as exc:
            if poppler_path:
                raise RuntimeError(
                    f"Failed to render PDF with Poppler path '{poppler_path}'. "
                    f"Please verify the folder contains Poppler binaries like pdftoppm or pdftocairo.\n{exc}"
                ) from exc
            raise RuntimeError(
                "PDF rendering failed because Poppler is not available. "
                "Install Poppler and add it to PATH, or provide the Poppler bin folder path in the app."
            ) from exc

        text = ""
        for page in pages:
            processed = _preprocess_image(page)
            text += pytesseract.image_to_string(processed, config="--psm 6")

        return text

    image = Image.open(uploaded_file)
    processed = _preprocess_image(image)
    return pytesseract.image_to_string(processed, config="--psm 6")