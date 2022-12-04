from pathlib import Path

import pytest

import aiopytesseract


async def test_image_to_pdf_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_pdf(None)


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_pdf_str(image):
    resp = await aiopytesseract.image_to_pdf(image)
    assert len(resp) > 0


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_pdf_bytes(image):
    resp = await aiopytesseract.image_to_pdf(Path(image).read_bytes())
    assert len(resp) > 0
