from pathlib import Path

import pytest

import aiopytesseract


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_str_image(image):
    text = await aiopytesseract.image_to_string(image)
    assert isinstance(text, str)
    assert len(text) >= 90


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_bytes_image(image):
    text = await aiopytesseract.image_to_string(Path(image).read_bytes())
    assert isinstance(text, str)
    assert len(text) >= 90


@pytest.mark.asyncio
async def test_image_to_string_with_invalid():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_image_to_string_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_string(None)
