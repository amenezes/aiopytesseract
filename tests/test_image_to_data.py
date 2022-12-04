from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractRuntimeError
from aiopytesseract.models import Data


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_data_with_str_image(image):
    data = await aiopytesseract.image_to_data(image)
    assert isinstance(data, list)
    assert isinstance(data[0], Data)
    assert len(data) == 22


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_data_with_bytes_image(image):
    data = await aiopytesseract.image_to_data(Path(image).read_bytes())
    assert isinstance(data, list)
    assert isinstance(data[0], Data)
    assert len(data) == 22


async def test_image_to_data_with_invalid():
    with pytest.raises(TesseractRuntimeError):
        await aiopytesseract.image_to_data("tests/samples/file-sample_150kB.pdf")


async def test_image_to_data_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_data(None)
