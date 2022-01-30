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
from .exceptions import TesseractNotFoundError, TesseractRuntimeError
from .validators import file_exists, oem_is_valid, psm_is_valid


async def execute_cmd(cmd_args: List[str]):
    proc = await asyncio.create_subprocess_exec(
        TESSERACT_CMD,
        *cmd_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc


@singledispatch
async def execute(
    image: Any,
    output_format: str,
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


@execute.register(str)
async def _(
    image: str,
    output_format: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    await file_exists(image)
    response: bytes = await execute(
        Path(image).read_bytes(),
        output_format,
        user_words,
        user_patterns,
        dpi,
        lang,
        psm,
        oem,
        nice,
        timeout,
    )
    return response


@execute.register(bytes)
async def _(
    image: bytes,
    output_format: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> bytes:
    cmd_args = await _build_cmd_args(
        output_extension=output_format,
        dpi=dpi,
        psm=psm,
        oem=oem,
        user_words=user_words,
        user_patterns=user_patterns,
        lang=lang,
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            TESSERACT_CMD,
            *cmd_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError:
        raise TesseractNotFoundError(f"{TESSERACT_CMD} not found.")
    stdout, stderr = await asyncio.wait_for(proc.communicate(image), timeout=timeout)
    if proc.returncode != 0:
        raise TesseractRuntimeError(stderr.decode(AIOPYTESSERACT_DEFAULT_ENCODING))
    return stdout


async def execute_multi_output_cmd(
    image: bytes,
    output_file: str,
    output_format: str,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    dpi: int = 200,
    lang: Optional[str] = None,
    psm: int = 3,
    oem: int = 3,
    nice: int = 0,
    timeout: float = AIOPYTESSERACT_DEFAULT_TIMEOUT,
) -> Tuple[str, ...]:
    cmd_args = await _build_cmd_args(
        output_extension=output_format,
        dpi=dpi,
        psm=psm,
        oem=oem,
        user_words=user_words,
        user_patterns=user_patterns,
        lang=lang,
        output=output_file,
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            TESSERACT_CMD,
            *cmd_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError:
        raise TesseractNotFoundError(f"{TESSERACT_CMD} not found.")
    _, stderr = await asyncio.wait_for(proc.communicate(image), timeout=timeout)
    if proc.returncode != 0:
        raise TesseractRuntimeError(stderr.decode(AIOPYTESSERACT_DEFAULT_ENCODING))
    return tuple(
        [f"{output_file}{OUTPUT_FILE_EXTENSIONS[ext]}" for ext in output_format.split()]  # type: ignore
    )


async def _build_cmd_args(
    output_extension: str,
    dpi: int,
    psm: int,
    oem: int,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
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

    if lang:
        cmd_args.append("-l")
        cmd_args.append(lang)

    extension = reversed(output_extension.split())
    for ext in extension:
        cmd_args.append(ext)

    logger.debug(f"Command: 'tesseract {shlex.join(cmd_args)}'")
    return shlex.split(shlex.join(cmd_args))
