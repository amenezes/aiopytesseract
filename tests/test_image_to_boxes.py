from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractRuntimeError
from aiopytesseract.models import Box


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_boxes_with_str_image(image):
    boxes = await aiopytesseract.image_to_boxes(image)
    assert isinstance(boxes, list)
    assert isinstance(boxes[0], Box)
    assert len(boxes) == 78


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_boxes_with_bytes_image(image):
    boxes = await aiopytesseract.image_to_boxes(Path(image).read_bytes())
    assert isinstance(boxes, list)
    assert isinstance(boxes[0], Box)
    assert len(boxes) == 78


async def test_image_to_boxes_with_invalid():
    with pytest.raises(TesseractRuntimeError):
        await aiopytesseract.image_to_boxes("tests/samples/file-sample_150kB.pdf")


async def test_image_to_boxes_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_boxes(None)


def test_box_str():
    box = Box(character="A", x=0, y=0, w=10, h=10)
    assert str(box) == "A"
