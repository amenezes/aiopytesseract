from pathlib import Path

import pytest

import aiopytesseract

DATA = "Page number: 0\nOrientation in degrees: 0\nRotate: 0\nOrientation confidence: 3.47\nScript: Latin\nScript confidence: 46.67\n"


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_osd_with_str_image(image):
    data = await aiopytesseract.image_to_osd(image)
    assert isinstance(data, str)
    assert data == DATA


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_osd_with_bytes_image(image):
    data = await aiopytesseract.image_to_osd(Path(image).read_bytes())
    assert isinstance(data, str)
    assert data == DATA


@pytest.mark.asyncio
async def test_image_to_osd_with_invalid():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_osd("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_image_to_osd_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_osd(None)
