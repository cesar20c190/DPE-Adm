import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np
import pytesseract
import imutils
from skimage.filters import threshold_local
from PIL import Image
import re
from pdf2image import convert_from_path

# Caminhos
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\cesar\OneDrive\Documentos\Release-24.08.0-0 (1)\poppler-24.08.0\Library\bin"

# Título
st.title("🆔 OCR Inteligente de CNH com Webcam + PDF via pdf2image")

capturar = st.button("📸 Capturar imagem da CNH")

class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        self.frame = img
        return av.VideoFrame.from_ndarray(img, format="bgr24")

ctx = webrtc_streamer(
    key="ocr-inteligente",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={
        "video": {"width": {"ideal": 1920}, "height": {"ideal": 1080}, "frameRate": {"ideal": 30}},
        "audio": False,
    },
    async_processing=True,
)

def cleanImage(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    topHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    blackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    add = cv2.add(gray, topHat)
    subtract = cv2.subtract(add, blackHat)
    T = threshold_local(subtract, 29, offset=35, method="gaussian", mode="mirror")
    thresh = (subtract > T).astype("uint8") * 255
    thresh = cv2.bitwise_not(thresh)
    return thresh

def extract_info_from_text(text):
    data = {"nome": None, "cpf": None, "nascimento": None}
    text = re.sub(r"[\n\r]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)

    nome_match = re.search(r"NOME.*?([\w\s]+(?: [A-Z]{2,})?)", text, re.IGNORECASE)
    if nome_match:
        data["nome"] = nome_match.group(1).strip()
    else:
        lines = text.upper().splitlines()
        for line in lines:
            if "NACIONALIDADE" in line or "FILIACAO" in line:
                break
            if re.match(r"^[A-Z\s]{10,}$", line) and "BRASILEIRO" not in line and not re.search(r"\d", line):
                data["nome"] = line.strip()
                break

    cpf_match = re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", text)
    if cpf_match:
        data["cpf"] = cpf_match.group(0).replace(".", "").replace("-", "")

    nascimento_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if nascimento_match:
        data["nascimento"] = nascimento_match.group(0).strip()

    return data

# --------------------------
# Captura, PDF e OCR
# --------------------------
if capturar and ctx.video_processor:
    frame = ctx.video_processor.frame
    if frame is not None:
        # Exibe imagem HD capturada
        st.image(frame, caption="📷 Imagem capturada em 1080p", use_container_width=True)

        # Salva como PDF em alta resolução
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pdf_path = "imagem_hd.pdf"
        pil_image.save(pdf_path, "PDF", resolution=200.0)
        st.success("📄 Imagem HD salva como PDF!")

        # Converte o PDF em imagem usando poppler_path
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        if images:
            img = np.array(images[0])
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            st.image(img, caption="📄 Primeira página do PDF convertida", use_container_width=True)

            # Pré-processamento
            processed = cleanImage(img)
            st.image(processed, caption="🔍 Após pré-processamento", use_container_width=True)

            # OCR
            text = pytesseract.image_to_string(Image.fromarray(processed), lang="por")
            data = extract_info_from_text(text)

            st.subheader("🧾 Dados extraídos:")
            if any(data.values()):
                st.json(data)
            else:
                st.error("❌ Nenhum dado extraído.")
