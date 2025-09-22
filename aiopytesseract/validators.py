from pathlib import Path

from aiopytesseract.constants import (
    OCR_ENGINE_MODES,
    PAGE_SEGMENTATION_MODES,
    TESSERACT_LANGUAGES,
)
from aiopytesseract.exceptions import (
    LanguageInvalidException,
    NoSuchFileException,
    OEMInvalidException,
    PSMInvalidException,
)


async def psm_is_valid(psm: int) -> None:
    if psm not in PAGE_SEGMENTATION_MODES:
        raise PSMInvalidException(psm)


async def oem_is_valid(oem: int) -> None:
    if oem not in OCR_ENGINE_MODES:
        raise OEMInvalidException(oem)


async def file_exists(file_path: str) -> None:
    if not Path(file_path).exists():
        raise NoSuchFileException(f"No such file: '{file_path}'")


async def language_is_valid(language: str) -> None:
    for lang in language.split("+"):
        if lang not in TESSERACT_LANGUAGES:
            raise LanguageInvalidException(
                f"'{lang}' language is not among the supported by Tesseract."
            )
