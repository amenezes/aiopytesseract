import shlex
from contextlib import asynccontextmanager
from functools import singledispatch
from pathlib import Path
from typing import Any, AsyncGenerator, List, Optional, Tuple

from aiofiles import tempfile  # type: ignore

from .base_command import execute, execute_cmd, execute_multi_output_cmd
from .constants import (
    AIOPYTESSERACT_DEFAULT_DPI,
    AIOPYTESSERACT_DEFAULT_ENCODING,
    AIOPYTESSERACT_DEFAULT_NICE,
    AIOPYTESSERACT_DEFAULT_OEM,
    AIOPYTESSERACT_DEFAULT_PSM,
    AIOPYTESSERACT_DEFAULT_TIMEOUT,
    TESSERACT_LANGUAGES,
)
from .file_format import FileFormat


async def languages(config: str = "") -> List:
    proc = await execute_cmd(["--list-langs", shlex.quote(config)])
    data = await proc.stdout.read()
    languages = []
    for line in data.decode(AIOPYTESSERACT_DEFAULT_ENCODING).split():
        lang = line.strip()
        if lang in TESSERACT_LANGUAGES:
            languages.append(lang)
    return languages


async def get_languages(config: str = "") -> List:
    langs = await languages(config)
    return langs


async def tesseract_version() -> str:
    proc = await execute_cmd(["--version"])
    data: bytes = await proc.stdout.readuntil()
    return data.decode(AIOPYTESSERACT_DEFAULT_ENCODING).split()[1]


async def get_tesseract_version() -> str:
    version = await tesseract_version()
    return version


@singledispatch
async def image_to_string(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    """Extract string from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words:
    :param user_patterns:
    :param dpi:
    :param lang:
    :param psm:
    :param oem:
    :param nice:
    :param timeout:
    """
    raise NotImplementedError(f"Type {type(image)} not supported.")


@image_to_string.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    image_text: bytes = await execute(
        image,
        FileFormat.TXT,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return image_text.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@image_to_string.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    image_text: bytes = await execute(
        image,
        FileFormat.TXT,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return image_text.decode(AIOPYTESSERACT_DEFAULT_ENCODING)


@singledispatch
async def image_to_hocr(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    """TODO

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words:
    :param user_patterns:
    :param dpi:
    :param lang:
    :param psm:
    :param oem:
    :param nice:
    :param timeout:
    """
    raise NotImplementedError


@image_to_hocr.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    output: Path = await execute(
        image,
        FileFormat.HOCR,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return output.read_bytes()


@image_to_hocr.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    output: Path = await execute(
        image,
        FileFormat.HOCR,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return output.read_bytes()


@singledispatch
async def image_to_pdf(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    """Generate a searchable PDF from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words:
    :param user_patterns:
    :param dpi:
    :param lang:
    :param psm:
    :param oem:
    :param nice:
    :param timeout:
    """
    raise NotImplementedError


@image_to_pdf.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.PDF,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return output


@image_to_pdf.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    nice: int = AIOPYTESSERACT_DEFAULT_NICE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    output: bytes = await execute(
        image,
        FileFormat.PDF,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return output


async def image_to_boxes():
    pass


async def image_to_data():
    pass


async def image_to_osd():
    pass


@asynccontextmanager
async def run(
    image: bytes,
    output_filename: str,
    output_format: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
) -> AsyncGenerator[Tuple[str, ...], None]:
    """TODO

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words:
    :param user_patterns:
    :param dpi:
    :param lang:
    :param psm:
    :param oem:
    :param nice:
    :param timeout:
    """
    if not isinstance(image, bytes):
        raise Exception
    async with tempfile.TemporaryDirectory(prefix="aiopytesseract-") as tmpdir:
        resp = await execute_multi_output_cmd(
            image,
            f"{tmpdir}/{output_filename}",
            output_format,
            user_words,
            user_patterns,
            dpi,
            lang,
            psm,
            oem,
        )
        yield resp
