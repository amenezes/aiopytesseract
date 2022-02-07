import asyncio
import re
from contextlib import asynccontextmanager
from functools import singledispatch
from pathlib import Path
from typing import Any, AsyncGenerator, List, Optional, Tuple

from aiofiles import tempfile  # type: ignore

from .base_command import execute, execute_cmd, execute_multi_output_cmd
from .constants import (
    AIOPYTESSERACT_DEFAULT_DPI,
    AIOPYTESSERACT_DEFAULT_ENCODING,
    AIOPYTESSERACT_DEFAULT_LANGUAGE,
    AIOPYTESSERACT_DEFAULT_OEM,
    AIOPYTESSERACT_DEFAULT_PSM,
    AIOPYTESSERACT_DEFAULT_TIMEOUT,
    TESSERACT_LANGUAGES,
)
from .exceptions import TesseractRuntimeError
from .file_format import FileFormat


async def languages(config: str = "") -> List:
    """Tesseract available languages."""
    proc = await execute_cmd(f"--list-langs {config}")
    data = await proc.stdout.read()
    languages = []
    for line in data.decode(AIOPYTESSERACT_DEFAULT_ENCODING).split():
        lang = line.strip()
        if lang in TESSERACT_LANGUAGES:
            languages.append(lang)
    return languages


async def get_languages(config: str = "") -> List:
    """Tesseract available languages."""
    langs = await languages(config)
    return langs


async def tesseract_version() -> str:
    """Tesseract version."""
    proc = await execute_cmd("--version")
    data: bytes = await proc.stdout.readuntil()
    return data.decode(AIOPYTESSERACT_DEFAULT_ENCODING).split()[1]


async def get_tesseract_version() -> str:
    """Tesseract version."""
    version = await tesseract_version()
    return version


async def confidence(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> Optional[str]:
    """Get script confidence.

    :param image: image input to tesseract. (valid values: str)
    :param dpi: image dots per inch (DPI)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    proc = await execute_cmd(f"stdin stdout -l {lang} --dpi {dpi} --psm 0 --oem {oem}")
    stdout, stderr = await asyncio.wait_for(
        proc.communicate(Path(image).read_bytes()), timeout=timeout
    )
    m = re.search(
        r"(Script.confidence:.(\d{1,10}.\d{1,10})$)",
        stdout.decode(AIOPYTESSERACT_DEFAULT_ENCODING),
    )
    resp = None
    if m:
        resp = m.group(2)
    return resp


async def deskew(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> Optional[str]:
    """Get Deskew angle.

    :param image: image input to tesseract. (valid values: str)
    :param dpi: image dots per inch (DPI)
    :param oem: ocr engine modes (default: 3)
    :param lang: tesseract language. (Format: eng, eng+por, eng+por+fra)
    :param timeout: command timeout (default: 30)
    """
    proc = await execute_cmd(
        f"{image} stdout -l {lang} --dpi {dpi} --psm 2 --oem {oem}"
    )
    data = await asyncio.wait_for(proc.stderr.read(), timeout=timeout)
    m = re.search(
        r"(Deskew.angle:.)(\d{1,10}.\d{1,10}$)",
        data.decode(AIOPYTESSERACT_DEFAULT_ENCODING),
    )
    resp = None
    if m:
        resp = m.group(2)
    return resp


@singledispatch
async def image_to_string(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    """Extract string from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file
    :param user_patterns: location of user patterns file
    :param dpi: image dots per inch (DPI)
    :param lang: tesseract language. (Format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes (default: 3)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    raise NotImplementedError(f"Type {type(image)} not supported.")


@image_to_string.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> str:
    image_text: bytes = await execute(
        image,
        FileFormat.TXT,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return image_text.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@image_to_string.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> str:
    image_text: bytes = await execute(
        image,
        FileFormat.TXT,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return image_text.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@singledispatch
async def image_to_hocr(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    """HOCR

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file
    :param user_patterns: location of user patterns file
    :param dpi: image dots per inch (DPI)
    :param lang: tesseract language. (Format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes (default: 3)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    raise NotImplementedError


@image_to_hocr.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.HOCR,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return output


@image_to_hocr.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.HOCR,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return output


@singledispatch
async def image_to_pdf(
    image: Any,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> bytes:
    """Generate a searchable PDF from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file
    :param user_patterns: location of user patterns file
    :param dpi: image dots per inch (DPI)
    :param lang: tesseract language. (Format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes (default: 3)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    raise NotImplementedError


@image_to_pdf.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.PDF,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return output


@image_to_pdf.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.PDF,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
    )
    return output


@singledispatch
async def image_to_boxes(
    image: Any, timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT
) -> str:
    """Bounding box estimates.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param timeout: command timeout (default: 30)
    """
    raise NotImplementedError


@image_to_boxes.register(str)
async def _(image: str, timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT) -> str:
    boxes = await image_to_boxes(Path(image).read_bytes(), timeout)
    return boxes


@image_to_boxes.register(bytes)
async def _(image: bytes, timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT) -> str:
    proc = await execute_cmd("stdin stdout batch.nochop makebox")
    stdout, stderr = await asyncio.wait_for(proc.communicate(image), timeout=timeout)
    if proc.returncode != 0:
        raise TesseractRuntimeError(stderr.decode(AIOPYTESSERACT_DEFAULT_ENCODING))
    return stdout.decode(AIOPYTESSERACT_DEFAULT_ENCODING)  # type: ignore


@singledispatch
async def image_to_data(
    image: Any,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    """Information about boxes, confidences, line and page numbers.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI)
    """
    raise NotImplementedError


@image_to_data.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    resp = await image_to_data(Path(image).read_bytes(), dpi, timeout)
    return resp


@image_to_data.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    proc = await execute_cmd(f"stdin stdout -c tessedit_create_tsv=1 --dpi {dpi}")
    stdout, stderr = await asyncio.wait_for(proc.communicate(image), timeout=timeout)
    if proc.returncode != 0:
        raise TesseractRuntimeError(stderr.decode(AIOPYTESSERACT_DEFAULT_ENCODING))
    return stdout.decode(AIOPYTESSERACT_DEFAULT_ENCODING)  # type: ignore


@singledispatch
async def image_to_osd(
    image: Any,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    """Information about orientation and script detection.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    raise NotImplementedError


@image_to_osd.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    resp = await execute(image, FileFormat.OSD, dpi, None, 0, oem, timeout)
    return resp.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@image_to_osd.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    resp = await execute(image, FileFormat.OSD, dpi, None, 0, oem, timeout)
    return resp.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@asynccontextmanager
async def run(
    image: bytes,
    output_filename: str,
    output_format: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
) -> AsyncGenerator[Tuple[str, ...], None]:
    """Run Tesseract-OCR with multiple analysis.

    This function allow run Tesseract with multiple output format with
    just one execution. For more info:

    - https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc#inout-arguments

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file
    :param user_patterns: location of user patterns file
    :param dpi: image dots per inch (DPI)
    :param lang: tesseract language. (Format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes (default: 3)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    """
    if not isinstance(image, bytes):
        raise NotImplementedError
    async with tempfile.TemporaryDirectory(prefix="aiopytesseract-") as tmpdir:
        resp = await execute_multi_output_cmd(
            image,
            f"{tmpdir}/{output_filename}",
            output_format,
            dpi,
            lang,
            psm,
            oem,
            timeout,
            user_words,
            user_patterns,
        )
        yield resp
