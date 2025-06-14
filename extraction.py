import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import re
from PIL import Image
from datetime import datetime

def extract_text(image):
    return pytesseract.image_to_string(image)

def detect_document_type(text):
    if "Permanent Account Number" in text or re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text):
        return "PAN"
    elif "Driving Licence" in text or "Licence" in text:
        return "Driving Licence"
    elif re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text) and "DOB" in text:
        return "Aadhaar"
    else:
        return "Unknown"

def extract_fields(text, doc_type):
    if doc_type == "PAN":
        return {
            "Name": re.findall(r'^([A-Z]{2,}(?:\s[A-Z]{2,})+)', text, re.MULTILINE)[0] if re.findall(r'^([A-Z]{2,}(?:\s[A-Z]{2,})+)', text, re.MULTILINE) else None,
            "Father's Name": re.findall(r'^([A-Z]{2,}(?:\s[A-Z]{2,})+)', text, re.MULTILINE)[1] if len(re.findall(r'^([A-Z]{2,}(?:\s[A-Z]{2,})+)', text, re.MULTILINE)) > 1 else None,
            "DOB": re.search(r'\d{2}/\d{2}/\d{4}', text).group() if re.search(r'\d{2}/\d{2}/\d{4}', text) else None,
            "PAN": re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text).group() if re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text) else None
        }

    elif doc_type == "Aadhaar":
        return {
            "Name": re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text).group() if re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text) else None,
            "DOB": re.search(r'DOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text).group(1) if re.search(r'DOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text) else None,
            "Gender": re.search(r'\b(MALE|FEMALE|Male|Female)\b', text, re.IGNORECASE).group().upper() if re.search(r'\b(MALE|FEMALE|Male|Female)\b', text, re.IGNORECASE) else None,
            "Aadhaar": re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text).group() if re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text) else None
        }

    elif doc_type == "Driving Licence":
        dates = re.findall(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
        return {
            "Licence Number": re.search(r'[A-Z]{2}\d{2}\s?\d{10}', text).group().replace(" ", "") if re.search(r'[A-Z]{2}\d{2}\s?\d{10}', text) else None,
            "Name": re.search(r'Name:\s*\n?([A-Z\s]+)', text).group(1).strip() if re.search(r'Name:\s*\n?([A-Z\s]+)', text) else None,
            "DOB": re.search(r'Date of Birth[:\s]*([0-9]{2}[-/][0-9]{4})', text).group(1) if re.search(r'Date of Birth[:\s]*([0-9]{2}[-/][0-9]{4})', text) else None,
            "Father's Name": re.search(r'Son/Daughter/Wife of:\s*\n?([A-Z\s]+)', text).group(1).strip() if re.search(r'Son/Daughter/Wife of:\s*\n?([A-Z\s]+)', text) else None,
            "Address": re.search(r'Address:\s*\n?([\s\S]*?)\nDate of', text).group(1).strip().replace("\n", ", ") if re.search(r'Address:\s*\n?([\s\S]*?)\nDate of', text) else None,
            "Issue Date": dates[2] if len(dates) > 2 else None,
            "Validity (NT)": dates[0] if len(dates) > 0 else None,
            "Validity (TR)": dates[1] if len(dates) > 1 else None,
        }
    else:
        return {"error": "Unknown or unsupported document type"}

def process_image(image):
    text = extract_text(image)
    doc_type = detect_document_type(text)
    fields = extract_fields(text, doc_type)
    return doc_type, fields
