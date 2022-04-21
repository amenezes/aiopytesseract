import asyncio
import shlex
from collections import deque
from functools import singledispatch
from pathlib import Path
from typing import Any, List, Optional, Tuple

from ._logger import logger
from .constants import (
    AIOPYTESSERACT_DEFAULT_ENCODING,
    AIOPYTESSERACT_DEFAULT_TIMEOUT,
    OUTPUT_FILE_EXTENSIONS,
    TESSERACT_CMD,
)
from .exceptions import TesseractRuntimeError
from .returncode import ReturnCode
from .validators import file_exists, language_is_valid, oem_is_valid, psm_is_valid


async def execute_cmd(cmd_args: str, timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT):
    logger.debug(
        f"aiopytesseract command: '{TESSERACT_CMD} {shlex.join(shlex.split(cmd_args))}'"
    )
    proc = await asyncio.wait_for(
        asyncio.create_subprocess_exec(
            TESSERACT_CMD,
            *shlex.split(cmd_args),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        ),
        timeout=timeout,
    )
    return proc


@singledispatch
async def execute(
    image: Any,
    output_format: str,
    dpi: int,
    lang: Optional[str],
    psm: int,
    oem: int,
    timeout: float,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
) -> bytes:
    raise NotImplementedError


@execute.register(str)
async def _(
    image: str,
    output_format: str,
    dpi: int,
    lang: Optional[str],
    psm: int,
    oem: int,
    timeout: float,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
) -> bytes:
    await file_exists(image)
    response: bytes = await execute(
        Path(image).read_bytes(),
        output_format,
        dpi,
        lang,
        psm,
        oem,
        timeout,
        user_words,
        user_patterns,
        tessdata_dir,
    )
    return response


@execute.register(bytes)
async def _(
    image: bytes,
    output_format: str,
    dpi: int,
    lang: Optional[str],
    psm: int,
    oem: int,
    timeout: float,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> bytes:
    cmd_args = await _build_cmd_args(
        output_extension=output_format,
        dpi=dpi,
        psm=psm,
        oem=oem,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
        lang=lang,
    )
    try:
        proc = None
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                TESSERACT_CMD,
                *cmd_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            ),
            timeout=timeout,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(image), timeout=timeout
        )
        if proc.returncode != ReturnCode.SUCCESS:
            raise TesseractRuntimeError(stderr.decode(encoding))
    except asyncio.TimeoutError:
        raise TesseractRuntimeError("Exceed the timeout")
    finally:
        if proc is not None and proc.returncode is None:
            proc.kill()
    return stdout


async def execute_multi_output_cmd(
    image: bytes,
    output_file: str,
    output_format: str,
    dpi: int,
    lang: str,
    psm: int,
    oem: int,
    timeout: float,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
    encoding: str = AIOPYTESSERACT_DEFAULT_ENCODING,
) -> Tuple[str, ...]:
    cmd_args = await _build_cmd_args(
        output_extension=output_format,
        dpi=dpi,
        psm=psm,
        oem=oem,
        user_words=user_words,
        user_patterns=user_patterns,
        tessdata_dir=tessdata_dir,
        lang=lang,
        output=output_file,
    )
    try:
        proc = None
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                TESSERACT_CMD,
                *cmd_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            ),
            timeout=timeout,
        )
        _, stderr = await asyncio.wait_for(proc.communicate(image), timeout=timeout)
        if proc.returncode != ReturnCode.SUCCESS:
            raise TesseractRuntimeError(stderr.decode(encoding))
        return tuple(
            [f"{output_file}{OUTPUT_FILE_EXTENSIONS[ext]}" for ext in output_format.split()]  # type: ignore
        )
    except asyncio.TimeoutError:
        raise TesseractRuntimeError("Exceed the timeout")
    finally:
        if proc is not None and proc.returncode is None:
            proc.kill()


async def _build_cmd_args(
    output_extension: str,
    dpi: int,
    psm: int,
    oem: int,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    tessdata_dir: Optional[str] = None,
    lang: Optional[str] = None,
    output: str = "stdout",
) -> List[str]:
    await asyncio.gather(psm_is_valid(psm), oem_is_valid(oem))
    cmd_args = deque(
        ["stdin", f"{output}", "--dpi", f"{dpi}", "--psm", f"{psm}", "--oem", f"{oem}"]
    )
    if user_words:
        cmd_args.append("--user-words")
        cmd_args.append(user_words)

    if user_patterns:
        cmd_args.append("--user-patterns")
        cmd_args.append(user_patterns)

    if tessdata_dir:
        cmd_args.append("--tessdata-dir")
        cmd_args.append(tessdata_dir)

    if lang:
        await language_is_valid(lang)
        cmd_args.append("-l")
        cmd_args.append(lang)

    extension = reversed(output_extension.split())
    for ext in extension:
        cmd_args.append(ext)

    logger.debug(f"aiopytesseract command: 'tesseract {shlex.join(cmd_args)}'")
    return shlex.split(shlex.join(cmd_args))
