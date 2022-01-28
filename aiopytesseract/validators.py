from pathlib import Path

from .constants import OCR_ENGINE_MODES, PAGE_SEGMENTATION_MODES
from .exceptions import NoSuchFileException, OEMInvalidException, PSMInvalidException


async def psm_is_valid(psm: int):
    if psm not in PAGE_SEGMENTATION_MODES.keys():
        raise PSMInvalidException


async def oem_is_valid(oem: int):
    if oem not in OCR_ENGINE_MODES.keys():
        raise OEMInvalidException


async def file_exists(file_path: str):
    if not Path(file_path).exists():
        raise NoSuchFileException(f"No such file: '{file_path}'")
