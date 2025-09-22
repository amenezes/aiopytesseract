import asyncio
import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import singledispatch
from pathlib import Path

import cattr
from aiofiles import tempfile

from aiopytesseract._logger import logger
from aiopytesseract.base_command import execute, execute_cmd, execute_multi_output_cmd
from aiopytesseract.constants import (
    AIOPYTESSERACT_DEFAULT_DPI,
    AIOPYTESSERACT_DEFAULT_ENCODING,
    AIOPYTESSERACT_DEFAULT_LANGUAGE,
    AIOPYTESSERACT_DEFAULT_OEM,
    AIOPYTESSERACT_DEFAULT_PSM,
    AIOPYTESSERACT_DEFAULT_TIMEOUT,
    TESSERACT_LANGUAGES,
)
from aiopytesseract.exceptions import TesseractRuntimeError, TesseractTimeoutError
from aiopytesseract.file_format import FileFormat
from aiopytesseract.models import OSD, Box, Data, Parameter
from aiopytesseract.returncode import ReturnCode
from aiopytesseract.validators import file_exists


async def languages(
    config: str = "", encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING
) -> list[str]:
    """Tesseract available languages.

    :param config: config. (valid values: str, default: "")
    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd(f"--list-langs {config}")
    data = await proc.stdout.read()  # type: ignore
    langs = []
    for line in data.decode(encoding).split():
        lang = line.strip()
        if lang in TESSERACT_LANGUAGES:
            langs.append(lang)
    return langs


async def get_languages(
    config: str = "", encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING
) -> list[str]:
    """Tesseract available languages.

    :param config: config. (valid values: str, default: "")
    :param encoding: decode bytes to string. (default: utf-8)
    """
    return await languages(config, encoding=encoding)


async def tesseract_version(encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING) -> str:
    """Tesseract version.

    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd("--version")
    data: bytes = await proc.stdout.readuntil()  # type: ignore
    return data.decode(encoding).split()[1]


async def get_tesseract_version(encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING) -> str:
    """Tesseract version.

    :param encoding: decode bytes to string. (default: utf-8)
    """
    return await tesseract_version(encoding)


async def confidence(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    tessdata_dir: str | None = None,
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
        raise TesseractTimeoutError(timeout) from None
    except AttributeError:
        confidence_value = 0.0
    return confidence_value


async def deskew(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    tessdata_dir: str | None = None,
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
        data = await asyncio.wait_for(proc.stderr.read(), timeout=timeout)  # type: ignore
        deskew_value = float(
            re.search(  # type: ignore
                r"(Deskew.angle:.)(\d{1,10}.\d{1,10}$)",
                data.decode(encoding),
            ).group(2)
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError(timeout) from None
    except AttributeError:
        deskew_value = 0.0
    return deskew_value


async def tesseract_parameters(
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> list[Parameter]:
    """list of all Tesseract parameters with default value and short description.

    - reference: https://tesseract-ocr.github.io/tessdoc/tess3/ControlParams.html

    :param encoding: decode bytes to string. (default: utf-8)
    """
    proc = await execute_cmd("--print-parameters")
    raw_data: bytes = await proc.stdout.read()  # type: ignore
    data = raw_data.decode(encoding)
    params = []
    # [1:] - skip first line with text: "Tesseract parameters:\n"
    for line in data.split("\n")[1:]:
        param = re.search(r"(\w+)\s+(-?\d+.?\d*)\s+(.*)[^\n]$", line)
        if param:
            params.append(
                cattr.structure_attrs_fromtuple(
                    (param.group(1), param.group(3), param.group(2)),
                    Parameter,
                )
            )
        else:
            param = re.search(r"(\w+)\s+(.*)[^\n]$", line)
            if param:
                params.append(
                    cattr.structure_attrs_fromtuple(
                        (param.group(1), param.group(2)),
                        Parameter,
                    )
                )
    return sorted(params, key=lambda p: p.name)


@singledispatch
async def image_to_string(
    image: str | bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
    config: list[tuple[str, str]] | None = None,
) -> str:
    """Extract string from an image.

    :param image: image input to tesseract. (valid values: str, bytes)
    :param dpi: image dots per inch (DPI). (default: 300)
    :param lang: tesseract language. (default: eng, format: eng, eng+por, eng+por+fra)
    :param psm: page segmentation modes. (default: 3)
    :param oem: ocr engine modes. (default: 3)
    :param encoding: encoding. (default: UTF-8)
    :param timeout: command timeout. (default: 30)
    :param user_words: location of user words file. (default: None)
    :param user_patterns: location of user patterns file. (default: None)
    :param tessdata_dir: location of tessdata path. (default: None)
    :param config: set value for config variables. (default: None)
    """
    raise NotImplementedError(f"Type {type(image)} not supported.")


@image_to_string.register(str)
async def _(
    image: str,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
    config: list[tuple[str, str]] | None = None,
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
        config=config,
    )
    return image_text.decode(encoding)


@image_to_string.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
    config: list[tuple[str, str]] | None = None,
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
        config=config,
    )
    return image_text.decode(encoding)


@singledispatch
async def image_to_hocr(
    image: str | bytes,
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    image: str | bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
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
    image: str | bytes,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    tessdata_dir: str | None = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> list[Box]:
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
    tessdata_dir: str | None = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> list[Box]:
    await file_exists(image)
    return await image_to_boxes(
        Path(image).read_bytes(), lang, tessdata_dir, timeout, encoding
    )


@image_to_boxes.register(bytes)
async def _(
    image: bytes,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    tessdata_dir: str | None = None,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> list[Box]:
    cmdline = f"-l {lang} stdin stdout batch.nochop makebox"
    if tessdata_dir:
        cmdline = f"--tessdata-dir {tessdata_dir} {cmdline}"
    logger.debug(f"Executing tesseract command: {cmdline}")
    try:
        proc = await execute_cmd(cmdline)
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(image),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise TesseractTimeoutError(timeout) from None
    if proc.returncode != ReturnCode.SUCCESS:
        raise TesseractRuntimeError(stderr.decode(encoding))
    data = stdout.decode(encoding)
    datalen = len(data.split("\n")) - 1
    return [
        cattr.structure_attrs_fromtuple(tuple(line.split()), Box)
        for line in data.split("\n")[:datalen]
    ]


@singledispatch
async def image_to_data(
    image: str | bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: str | None = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> list[Data]:
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
    tessdata_dir: str | None = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> list[Data]:
    await file_exists(image)
    return await image_to_data(
        Path(image).read_bytes(), dpi, lang, timeout, encoding, tessdata_dir, psm
    )


@image_to_data.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: str | None = None,
    psm: int = AIOPYTESSERACT_DEFAULT_PSM,
) -> list[Data]:
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
        raise TesseractTimeoutError(timeout) from None
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
    image: str | bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: str | None = None,
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
    tessdata_dir: str | None = None,
) -> OSD:
    await file_exists(image)
    return await image_to_osd(
        Path(image).read_bytes(), dpi, oem, lang, timeout, encoding, tessdata_dir
    )


@image_to_osd.register(bytes)
async def _(
    image: bytes,
    dpi: int = AIOPYTESSERACT_DEFAULT_DPI,
    oem: int = AIOPYTESSERACT_DEFAULT_OEM,
    lang: str = AIOPYTESSERACT_DEFAULT_LANGUAGE,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
    tessdata_dir: str | None = None,
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
    return cattr.structure_attrs_fromtuple(
        re.findall(  # type: ignore
            r"\w+\s?:\s*(\d+.?\d*|\w+)",
            data.decode(encoding),
        ),
        OSD,
    )


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
    user_words: str | None = None,
    user_patterns: str | None = None,
    tessdata_dir: str | None = None,
    config: list[tuple[str, str]] | None = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> AsyncGenerator[tuple[str, ...], None]:
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
    :param config: set value for config variables. (default: None)
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
            config=config,
            encoding=encoding,
        )
        yield resp
