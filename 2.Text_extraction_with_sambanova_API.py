import streamlit as st
import os
import pytesseract
from PIL import Image
import pdfplumber
import pandas as pd
import docx
import tempfile
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



st.set_page_config(page_title="Universal Document Reader", layout="centered")

st.title("📄 Universal Document Reader")
st.write("Upload a document (PDF, DOCX, Image, CSV, TXT) to extract text.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "png", "jpg", "jpeg", "csv", "txt"])

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string(index=False)

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

if uploaded_file is not None:
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()

    st.success(f"Uploaded: {uploaded_file.name}")

    try:
        if file_ext == ".pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_ext == ".docx":
            text = extract_text_from_docx(uploaded_file)
        elif file_ext in [".png", ".jpg", ".jpeg"]:
            text = extract_text_from_image(uploaded_file)
        elif file_ext == ".csv":
            text = extract_text_from_csv(uploaded_file)
        elif file_ext == ".txt":
            text = extract_text_from_txt(uploaded_file)
        else:
            st.error("Unsupported file type.")
            text = None

        if text:
            st.subheader("📄 Extracted Text:")
            st.text_area("Text Output", value=text, height=400)
    except Exception as e:
        st.error(f"An error occurred: {e}")
