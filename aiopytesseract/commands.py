import shlex
from functools import singledispatch
from typing import Any, List, Optional

try:
    import PIL
except ModuleNotFoundError:
    PIL = None

from .base_command import execute, execute_cmd
from .constants import (
    AIOPYTESSERACT_DEFAULT_ENCODING,
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
    data = await proc.stdout.readuntil()
    return data.decode(AIOPYTESSERACT_DEFAULT_ENCODING).split()[1]


async def get_tesseract_version() -> str:
    version = await tesseract_version()
    return version


@singledispatch
async def image_to_string(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    raise NotImplementedError(f"Type {type(image)} not supported.")


@image_to_string.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    async with execute(
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
    ) as output_file:
        image_text = output_file.read_text(encoding=AIOPYTESSERACT_DEFAULT_ENCODING)
    return image_text


@image_to_string.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    async with execute(
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
    ) as output_file:
        image_text = output_file.read_text(encoding=AIOPYTESSERACT_DEFAULT_ENCODING)
    return image_text


@singledispatch
async def image_to_hocr(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    raise NotImplementedError


@image_to_hocr.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    async with execute(
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
    ) as output:
        return output.read_bytes()


@image_to_hocr.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    async with execute(
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
    ) as output:
        return output.read_bytes()


@singledispatch
async def image_to_pdf(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
):
    raise NotImplementedError


@image_to_pdf.register(str)
async def _(
    image: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    async with execute(
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
    ) as output:
        return output.read_bytes()


@image_to_pdf.register(bytes)
async def _(
    image: bytes,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    async with execute(
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
    ) as output:
        return output.read_bytes()


async def image_to_boxes():
    pass


async def image_to_data():
    pass


async def image_to_osd():
    pass
