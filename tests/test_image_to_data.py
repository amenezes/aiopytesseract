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


def test_data_str():
    data = Data(
        level=0,
        page_num=0,
        block_num=0,
        par_num=0,
        line_num=0,
        word_num=0,
        left=0,
        top=0,
        width=0,
        height=0,
        conf=0,
        text="",
    )
    assert str(data) == ""
