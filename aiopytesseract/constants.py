import os

TESSERACT_CMD: str = str(os.getenv("TESSERACT_CMD", "tesseract"))

# https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html
TESSERACT_LANGUAGES = (
    "afr",
    "amh",
    "ara",
    "asm",
    "aze",
    "aze_cyrl",
    "bel",
    "ben",
    "bod",
    "bos",
    "bre",
    "bul",
    "cat",
    "ceb",
    "ces",
    "chi_sim",
    "chi_tra",
    "chr",
    "cos",
    "cym",
    "dan",
    "dan_frak",
    "deu",
    "deu_frak",
    "dzo",
    "ell",
    "eng",
    "enm",
    "epo",
    "equ",
    "est",
    "eus",
    "fao",
    "fas",
    "fil",
    "fin",
    "fra",
    "frk",
    "frm",
    "fry",
    "gla",
    "gle",
    "glg",
    "grc",
    "guj",
    "hat",
    "heb",
    "hin",
    "hrv",
    "hun",
    "hye",
    "iku",
    "ind",
    "isl",
    "ita",
    "ita_old",
    "jav",
    "jpn",
    "kan",
    "kat",
    "kat_old",
    "kaz",
    "khm",
    "kir",
    "kmr",
    "kor",
    "kor_vert",
    "kur",
    "lao",
    "lat",
    "lav",
    "lit",
    "ltz",
    "mal",
    "mar",
    "mkd",
    "mlt",
    "mon",
    "mri",
    "msa",
    "mya",
    "nep",
    "nld",
    "nor",
    "oci",
    "osd",
    "pan",
    "pol",
    "por",
    "pus",
    "que",
    "ron",
    "rus",
    "san",
    "sin",
    "slk",
    "slk_frak",
    "slv",
    "snd",
    "spa",
    "spa_old",
    "sqi",
    "srp_latn",
    "sun",
    "swa",
    "swe",
    "syr",
    "tam",
    "tat",
    "tel",
    "tgk",
    "tgl",
    "tha",
    "tir",
    "ton",
    "tur",
    "uig",
    "ukr",
    "urd",
    "uzb",
    "uzb_cyrl",
    "vie",
    "yid",
    "yor",
)

PAGE_SEGMENTATION_MODES = {
    0: "Orientation and script detection (OSD) only.",
    1: "Automatic page segmentation with OSD.",
    2: "Automatic page segmentation, but no OSD, or OCR. (not implemented)",
    3: "Fully automatic page segmentation, but no OSD. (Default)",
    4: "Assume a single column of text of variable sizes.",
    5: "Assume a single uniform block of vertically aligned text.",
    6: "Assume a single uniform block of text.",
    7: "Treat the image as a single text line.",
    8: "Treat the image as a single word.",
    9: "Treat the image as a single word in a circle.",
    10: "Treat the image as a single character.",
    11: "Sparse text. Find as much text as possible in no particular order.",
    12: "Sparse text with OSD.",
    13: "Raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific.",
}

# https://github.com/tesseract-ocr/tesseract/wiki#linux
OCR_ENGINE_MODES = {
    0: "Legacy engine only.",
    1: "Neural nets LSTM engine only.",
    2: "Legacy + LSTM engines.",
    3: "Default, based on what is available.",
}

AIOPYTESSERACT_DEFAULT_ENCODING: str = str(
    os.getenv("AIOPYTESSERACT_DEFAULT_ENCODING", "utf-8")
)
AIOPYTESSERACT_DEFAULT_TIMEOUT: float = float(
    os.getenv("AIOPYTESSERACT_DEFAULT_TIMEOUT", 30)
)
