from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractRuntimeError


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_hocr_with_str_image(image):
    hocr = await aiopytesseract.image_to_hocr(image)
    assert isinstance(hocr, str)
    assert len(hocr) > 50


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_hocr_with_bytes_image(image):
    hocr = await aiopytesseract.image_to_hocr(Path(image).read_bytes())
    assert isinstance(hocr, str)
    assert len(hocr) > 50


@pytest.mark.asyncio
async def test_image_to_hocr_with_invalid():
    with pytest.raises(TesseractRuntimeError):
        await aiopytesseract.image_to_hocr("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_image_to_hocr_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_hocr(None)
