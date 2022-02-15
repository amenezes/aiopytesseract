import asyncio
import base64
import logging
import tempfile

import streamlit as st

import aiopytesseract
from aiopytesseract.constants import (AIOPYTESSERACT_DEFAULT_TIMEOUT,
                                      OCR_ENGINE_MODES,
                                      PAGE_SEGMENTATION_MODES,
                                      TESSERACT_LANGUAGES)

logging.basicConfig(level=logging.DEBUG)
loop = asyncio.new_event_loop()
loop.set_debug(True)

st.markdown(
    """
# aiopytesseract

> *options **user_words** and **user_patterns** not available in this example.*
"""
)

st.sidebar.title("Settings")
operation = st.sidebar.selectbox(
    "Operation",
    (
        "Image to Text",
        "Image to PDF",
        "Image to HOCR",
        "Image to Boxes",
        "Image to Data",
        "Image to OSD",
        "Confidence",
        "Deskew",
        "Parameters"
    ),
)
dpi = st.sidebar.number_input("DPI", min_value=1, value=200)
lang = st.sidebar.multiselect("Language", TESSERACT_LANGUAGES, default=["eng"])
psm = st.sidebar.slider(
    "PSM",
    min_value=min(PAGE_SEGMENTATION_MODES.keys()),
    max_value=max(PAGE_SEGMENTATION_MODES.keys()),
    value=3,
)
oem = st.sidebar.slider(
    "OEM",
    min_value=min(OCR_ENGINE_MODES.keys()),
    max_value=max(OCR_ENGINE_MODES.keys()),
    value=3,
)
timeout = st.sidebar.text_input("Timeout", value=AIOPYTESSERACT_DEFAULT_TIMEOUT)
image = st.sidebar.file_uploader("Attach image")
if st.sidebar.button("Execute"):
    with st.spinner("Processing..."):
        match operation:
            case "Image to Text":
                text = loop.run_until_complete(
                    aiopytesseract.image_to_string(
                        image.getvalue(),
                        dpi=dpi,
                        lang="+".join(lang),
                        psm=psm,
                        oem=oem,
                        timeout=float(timeout),
                    )
                )
                st.markdown("""### Result:""")
                st.write(text)
            case "Image to PDF":
                pdf = loop.run_until_complete(
                    aiopytesseract.image_to_pdf(
                        image.getvalue(),
                        dpi=dpi,
                        lang="+".join(lang),
                        psm=psm,
                        oem=oem,
                        timeout=float(timeout),
                    )
                )
                base64_pdf = base64.b64encode(pdf).decode("utf-8")
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="900" height="1000" type="application/pdf">'
                st.markdown("""### Result:""")
                st.markdown(pdf_display, unsafe_allow_html=True)
            case "Image to HOCR":
                hocr = loop.run_until_complete(
                    aiopytesseract.image_to_hocr(
                        image.getvalue(),
                        dpi=dpi,
                        lang="+".join(lang),
                        psm=psm,
                        oem=oem,
                        timeout=float(timeout),
                    )
                )
                st.markdown("""### Result:""")
                st.code(hocr.decode("utf-8"))
            case "Image to Boxes":
                boxes = loop.run_until_complete(
                    aiopytesseract.image_to_boxes(image.getvalue())
                )
                st.markdown("""### Result:""")
                st.code(boxes)
            case "Image to Data":
                data = loop.run_until_complete(
                    aiopytesseract.image_to_data(image.getvalue())
                )
                st.markdown("""### Result:""")
                st.code(data)
            case "Image to OSD":
                osd = loop.run_until_complete(
                    aiopytesseract.image_to_osd(
                        image.getvalue(), dpi=dpi, oem=oem, timeout=float(timeout)
                    )
                )
                st.markdown("""### Result:""")
                st.text(osd)
            case "Confidence":
                with tempfile.NamedTemporaryFile(mode="w+b") as tmpfile:
                    tmpfile.write(image.getvalue())
                    tmpfile.seek(0)
                    confidence = loop.run_until_complete(
                        aiopytesseract.confidence(
                            tmpfile.name,
                            dpi=dpi,
                            lang="+".join(lang),
                            oem=oem,
                            timeout=float(timeout),
                        )
                    )
                if not confidence:
                    st.error("Confidence it's empty")
                st.markdown(f"""### Result: {confidence}""")
            case "Deskew":
                with tempfile.NamedTemporaryFile(mode="w+b") as tmpfile:
                    tmpfile.write(image.getvalue())
                    tmpfile.seek(0)
                    deskew = loop.run_until_complete(
                        aiopytesseract.deskew(
                            tmpfile.name, dpi=dpi, lang="+".join(lang), oem=oem
                        )
                    )
                if not deskew:
                    st.error("Deskew it's empty")
                st.markdown(f"""### Result: {deskew}""")
            case "Parameters":
                params = loop.run_until_complete(
                    aiopytesseract.tesseract_parameters()
                )
                st.table(data=params)
