import asyncio
import shlex
from collections import deque
from contextlib import asynccontextmanager
from functools import singledispatch
from pathlib import Path
from typing import Any, List, Optional

from aiofiles import tempfile

from aiopytesseract._logger import logger
from aiopytesseract.constants import (
    AIOPYTESSERACT_DEFAULT_ENCODING,
    AIOPYTESSERACT_DEFAULT_TIMEOUT,
    TESSERACT_CMD,
)
from aiopytesseract.exceptions import TesseractNotFoundError, TesseractRuntimeError
from aiopytesseract.validators import file_exists, oem_is_valid, psm_is_valid


async def execute_cmd(cmd_args: List[str]):
    proc = await asyncio.create_subprocess_exec(
        TESSERACT_CMD,
        *cmd_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc


@singledispatch
@asynccontextmanager
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
@asynccontextmanager
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
):
    async with tempfile.NamedTemporaryFile() as output_file:
        cmd_args = await _build_cmd_args(
            image,
            output_file.name,
            output_format,
            dpi,
            psm,
            oem,
            user_words,
            user_patterns,
            lang,
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                TESSERACT_CMD,
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError:
            raise TesseractNotFoundError(f"{TESSERACT_CMD} not found.")
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if proc.returncode != 0:
            raise TesseractRuntimeError(stderr.decode(AIOPYTESSERACT_DEFAULT_ENCODING))
        yield Path(f"{output_file.name}.{output_format}")


@execute.register(bytes)
@asynccontextmanager
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
):
    async with tempfile.NamedTemporaryFile() as input_file:
        await input_file.write(image)
        async with execute(
            input_file.name,
            output_format,
            user_words,
            user_patterns,
            dpi,
            lang,
            psm,
            oem,
            nice,
            timeout,
        ) as output:
            yield output


async def _build_cmd_args(
    input_file: str,
    output_file: str,
    extension: str,
    dpi: int,
    psm: int,
    oem: int,
    user_words: Optional[str] = None,
    user_patterns: Optional[str] = None,
    lang: Optional[str] = None,
) -> deque:
    await asyncio.gather(psm_is_valid(psm), oem_is_valid(oem), file_exists(input_file))
    cmd_args = deque(
        [input_file, "--dpi", f"{dpi}", "--psm", f"{psm}", "--oem", f"{oem}"]
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
    cmd_args.insert(1, output_file)
    cmd_args.insert(2, extension)
    logger.debug(f"Command: tesseract {shlex.join(cmd_args)}")
    return shlex.split(shlex.join(cmd_args))
