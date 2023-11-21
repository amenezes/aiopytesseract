import asyncio
import re
from contextlib import asynccontextmanager
from functools import singledispatch
from pathlib import Path
from typing import Any, AsyncGenerator, List, Optional, Tuple

import cattr
from aiofiles import tempfile

from aiopytesseract.validators import file_exists

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
from .exceptions import TesseractRuntimeError, TesseractTimeoutError
from .file_format import FileFormat
from .models import OSD, Box, Data, Parameter
from .returncode import ReturnCode


async def languages(
    config: str = "", encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING
) -> List[str]:
    """Tesseract available languages.

    :param config: config. (valid values: str)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd(f"--list-langs {config}")
    data = await proc.stdout.read()
    langs = []
    for line in data.decode(encoding).split():
        lang = line.strip()
        if lang in TESSERACT_LANGUAGES:
            langs.append(lang)
    return langs


async def get_languages(
    config: str = "", encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING
) -> List[str]:
    """Tesseract available languages.

    :param config: config. (valid values: str)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    langs = await languages(config, encoding=encoding)
    return langs


async def tesseract_version(encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING) -> str:
    """Tesseract version.

    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd("--version")
    data: bytes = await proc.stdout.readuntil()
    return data.decode(encoding).split()[1]


async def get_tesseract_version(encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING) -> str:
    """Tesseract version.

    :param encoding: decode bytes to string. (default: utf-8)
    """
    version = await tesseract_version(encoding)
    return version


async def confidence(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    tessdata_dir: Optional[str] = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> float:
    """Get script confidence.

    :param image: image input to tesseract. (valid values: str)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param oem: ocr engine modes. (default: 3)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param timeout: command timeout. (default: 30)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    cmdline = f"stdin stdout -l {lang} --dpi {dpi} --psm 0 --oem {oem}"
    if tessdata_dir:
        cmdline = f"--tessdata-dir {tessdata_dir} {cmdline}"
    try:
        proc = await execute_cmd(cmdline)
        stdout, _ = await asyncio.wait_for(
            proc.communicate(Path(image).read_bytes()), timeout=timeout
        )
        confidence_value = float(
            re.search(  # type: ignore
                r"(Script.confidence:.(\d{1,10}.\d{1,10})$)",
                stdout.decode(encoding),
            ).group(2)
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError()
    except AttributeError:
        confidence_value = 0.0
    return confidence_value


async def deskew(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    tessdata_dir: Optional[str] = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> float:
    """Get Deskew angle.

    :param image: image input to tesseract. (valid values: str)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param oem: ocr engine modes. (default: 3)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param timeout: command timeout. (default: 30)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    cmdline = f"{image} stdout -l {lang} --dpi {dpi} --psm 2 --oem {oem}"
    if tessdata_dir:
        cmdline = f"--tessdata-dir {tessdata_dir} {cmdline}"
    try:
        proc = await execute_cmd(cmdline)
        data = await asyncio.wait_for(proc.stderr.read(), timeout=timeout)
        deskew_value = float(
            re.search(  # type: ignore
                r"(Deskew.angle:.)(\d{1,10}.\d{1,10}$)",
                data.decode(encoding),
            ).group(2)
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError()
    except AttributeError:
        deskew_value = 0.0
    return deskew_value


async def tesseract_parameters(
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> List[Parameter]:
    """List of all Tesseract parameters with default value and short description.

    - reference: https://tesseract-ocr.github.io/tessdoc/tess3/ControlParams.html

    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd("--print-parameters")
    raw_data: bytes = await proc.stdout.read()
    data = raw_data.decode(encoding)
    params = []
    for line in data.split("\n"):
        param = re.search(r"(\w+)\s+(-?\d+.?\d*)\s+(.*)[^\n]$", line)
        if param:
            params.append(
                cattr.structure_attrs_fromtuple(
                    [param.group(1), param.group(2), param.group(3)], Parameter  # type: ignore
                )
            )
    return params


@singledispatch
async def image_to_string(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    """Extract string from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file. (default: None)
    :param user_patterns: location of user patterns file. (default: None)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes. (default: 3)
    :param oem: ocr engine modes. (default: 3)
    :param timeout: command timeout. (default: 30)
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
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> str:
    image_text: bytes = await execute(
        image,
        output_format=FileFormat.TXT,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
    )
    return image_text.decode(encoding)


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
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> str:
    image_text: bytes = await execute(
        image,
        output_format=FileFormat.TXT,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
    )
    return image_text.decode(encoding)


@singledispatch
async def image_to_hocr(
    image: Any,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> str:
    """HOCR

    :param image: image input to tesseract. (valid values: str, bytes)
    :param user_words: location of user words file. (default: None)
    :param user_patterns: location of user patterns file. (default: None)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
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
    tessdata_dir: Optional[str] = None,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> str:
    output: bytes = await execute(
        image,
        output_format=FileFormat.HOCR,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
    )
    return output.decode(encoding)


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
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> str:
    output: bytes = await execute(
        image,
        output_format=FileFormat.HOCR,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
    )
    return output.decode(encoding)


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
    tessdata_dir: Optional[str] = None,
) -> bytes:
    """Generate a searchable PDF from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes (default: 3)
    :param oem: ocr engine modes (default: 3)
    :param timeout: command timeout (default: 30)
    :param user_words: location of user words file. (default: None)
    :param user_patterns: location of user patterns file. (default: None)
    :param tessdata_dir: location of tessdata path. (default: None)
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
    tessdata_dir: Optional[str] = None,
) -> bytes:
    output: bytes = await execute(
        image,
        output_format=FileFormat.PDF,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
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
    tessdata_dir: Optional[str] = None,
) -> bytes:
    output: bytes = await execute(
        image,
        output_format=FileFormat.PDF,
        dpi=dpi,
        lang=lang,
        psm=psm,
        oem=oem,
        timeout=timeout,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
    )
    return output


@singledispatch
async def image_to_boxes(
    image: Any,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    tessdata_dir: Optional[str] = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> List[Box]:
    """Bounding box estimates.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param timeout: command timeout (default: 30)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    raise NotImplementedError


@image_to_boxes.register(str)
async def _(
    image: str,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    tessdata_dir: Optional[str] = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> List[Box]:
    await file_exists(image)
    boxes = await image_to_boxes(
        Path(image).read_bytes(), lang, tessdata_dir, timeout, encoding
    )
    return boxes


@image_to_boxes.register(bytes)
async def _(
    image: str,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    tessdata_dir: Optional[str] = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> List[Box]:
    cmdline = f"-l {lang} stdin stdout batch.nochop makebox"
    if tessdata_dir:
        cmdline = f"--tessdata-dir {tessdata_dir} {cmdline}"
    print(cmdline)
    try:
        proc = await execute_cmd(cmdline)
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(image), timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError()
    if proc.returncode != ReturnCode.SUCCESS:
        raise TesseractRuntimeError(stderr.decode(encoding))
    data = stdout.decode(encoding)
    datalen = len(data.split("\n")) - 1
    boxes = []
    for line in data.split("\n")[:datalen]:
        boxes.append(cattr.structure_attrs_fromtuple(line.split(), Box))
    return boxes


@singledispatch
async def image_to_data(
    image: Any,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> List[Data]:
    """Information about boxes, confidences, line and page numbers.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param timeout: command timeout (default: 30)
    :param encoding: decode bytes to string. (default: utf-8)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param psm: page segmentation modes. (default: 3)
    """
    raise NotImplementedError


@image_to_data.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> List[Data]:
    await file_exists(image)
    data_values = await image_to_data(
        Path(image).read_bytes(), dpi, lang, timeout, encoding, tessdata_dir, psm
    )
    return data_values


@image_to_data.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> List[Data]:
    cmdline = f"stdin stdout -c tessedit_create_tsv=1 --dpi {dpi} -l {lang} --psm {psm}"
    if tessdata_dir:
        cmdline = f"--tessdata-dir {tessdata_dir} {cmdline}"
    try:
        proc = await execute_cmd(cmdline)
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(image), timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError()
    if proc.returncode != ReturnCode.SUCCESS:
        raise TesseractRuntimeError(stderr.decode(encoding))
    data: str = stdout.decode(encoding)
    datalen = len(data.split("\n")) - 1
    params = []
    for line in data.split("\n")[1:datalen]:
        param = line.split()
        params.append(cattr.structure_attrs_fromtuple(param, Data))  # type: ignore
    return params


@singledispatch
async def image_to_osd(
    image: Any,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
) -> OSD:
    """Information about orientation and script detection.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param oem: ocr engine modes. (default: 3)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param timeout: command timeout. (default: 30)
    :param encoding: decode bytes to string. (default: utf-8)
    :param tessdata_dir: location of tessdata path. (default: None)
    """
    raise NotImplementedError


@image_to_osd.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
) -> OSD:
    await file_exists(image)
    osd = await image_to_osd(
        Path(image).read_bytes(), dpi, oem, lang, timeout, encoding, tessdata_dir
    )
    return osd


@image_to_osd.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: Optional[str] = None,
) -> OSD:
    data = await execute(
        image,
        output_format=FileFormat.OSD,
        lang=lang,
        dpi=dpi,
        psm=0,
        oem=oem,
        timeout=timeout,
        tessdata_dir=tessdata_dir,
    )
    osd = cattr.structure_attrs_fromtuple(
        re.findall(  # type: ignore
            r"\w+\s?:\s*(\d+.?\d*|\w+)",
            data.decode(encoding),
        ),
        OSD,
    )
    return osd


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
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> AsyncGenerator[Tuple[str, ...], None]:
    """Run Tesseract-OCR with multiple analysis.

    This function allow run Tesseract with multiple output format with
    just one execution. For more info:

    - https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc#inout-arguments

    :param image: image input to tesseract. (valid values: str, bytes)
    :param output_filename: base filename.
    :param output_format: output file extensions.
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes. (default: 3)
    :param oem: ocr engine modes. (default: 3)
    :param timeout: command timeout. (default: 30)
    :param user_words: location of user words file. (default: None)
    :param user_patterns: location of user patterns file. (default: None)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param encoding: decode bytes to string. (default: utf-8)
    """
    if not isinstance(image, bytes):
        raise NotImplementedError
    async with tempfile.TemporaryDirectory(prefix="aiopytesseract-") as tmpdir:
        resp = await execute_multi_output_cmd(
            image,
            output_file=f"{tmpdir}/{output_filename}",
            output_format=output_format,
            dpi=dpi,
            lang=lang,
            psm=psm,
            oem=oem,
            timeout=timeout,
            user_words=user_words,
            user_patterns=user_patterns,
            tessdata_dir=tessdata_dir,
            encoding=encoding,
        )
        yield resp
