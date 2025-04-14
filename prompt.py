import streamlit as st
import os
import pytesseract
from PIL import Image
import pdfplumber
import pandas as pd
import docx
import openai  # For calling SambaNova LLM via OpenAI-compatible client

# Configure Tesseract path for OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure SambaNova LLM Client
client = openai.OpenAI(
    api_key="b2483280-5696-437a-a6b4-2a0b01ef0b43",  # Set this in your environment
    base_url="https://api.sambanova.ai/v1",         # SambaNova base endpoint
)

# Streamlit UI Setupa
st.set_page_config(page_title="Universal Document Reader", layout="centered")

st.title("📄 Universal Document Reader with SambaNova LLM")
st.write("Upload a document (PDF, DOCX, Image, CSV, TXT) to extract text and analyze with a SambaNova model.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "png", "jpg", "jpeg", "csv", "txt"])

# ----------------- Extraction Functions ----------------- #
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

# ----------------- Main Logic ----------------- #
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
            st.text_area("Text Output", value=text, height=300)

            st.subheader("🤖 Analyzing with SambaNova LLM...")

            with st.spinner("Sending to SambaNova for analysis..."):
                try:
                    response = client.chat.completions.create(
                        model="DeepSeek-R1",
                        messages=[
                            {"role": "system",
                             "content": "You are a JSON formatting machine. Return ONLY valid JSON with no commentary, explanations, or text outside the JSON structure."},
                            {"role": "user", "content": f"""
                                                    Extract key-value pairs from this document into JSON format. Follow these rules STRICTLY:
                                                    1. Output MUST be pure JSON only
                                                    2. No markdown formatting
                                                    3. No text before/after JSON
                                                    4. Ensure proper escaping for quotes
                                                    5. Maintain original document structure in JSON hierarchy
                                                    6. If unsure about any data, omit it

                                                    Document content:
                                                    {text}
                                                    """}
                        ],
                        temperature=0.3,
                        top_p=0.4
                    )
                    model_response = response.choices[0].message.content
                    st.subheader("🧠 Extracted Key-Value Pairs from LLM:")
                    st.text_area("SambaNova Response", value=model_response, height=300)
                except Exception as e:
                    st.error(f"LLM Error: {e}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
