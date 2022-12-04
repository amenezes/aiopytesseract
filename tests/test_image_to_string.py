from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractRuntimeError


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_str_image(image):
    text = await aiopytesseract.image_to_string(image)
    assert isinstance(text, str)
    assert len(text) >= 90


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_bytes_image(image):
    text = await aiopytesseract.image_to_string(Path(image).read_bytes())
    assert isinstance(text, str)
    assert len(text) >= 90


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_bytes_image_args(image):
    text = await aiopytesseract.image_to_string(
        Path(image).read_bytes(),
        tessdata_dir="tests/samples/tessdata_fast",
    )
    assert isinstance(text, str)
    assert len(text) >= 90


async def test_image_to_string_with_invalid():
    with pytest.raises(TesseractRuntimeError):
        await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.pdf")


async def test_image_to_string_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_string(None)
