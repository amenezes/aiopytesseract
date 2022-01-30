from pathlib import Path

import pytest

import aiopytesseract

DATA = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n1\t1\t0\t0\t0\t0\t0\t0\t1232\t297\t-1\t\n2\t1\t1\t0\t0\t0\t407\t2\t459\t70\t-1\t\n3\t1\t1\t1\t0\t0\t407\t2\t459\t70\t-1\t\n4\t1\t1\t1\t1\t0\t407\t2\t459\t70\t-1\t\n5\t1\t1\t1\t1\t1\t407\t5\t219\t52\t95\tLorem\n5\t1\t1\t1\t1\t2\t656\t2\t210\t70\t95\tipsum\n2\t1\t2\t0\t0\t0\t6\t199\t1221\t91\t-1\t\n3\t1\t2\t1\t0\t0\t6\t199\t1221\t91\t-1\t\n4\t1\t2\t1\t1\t0\t56\t199\t1171\t45\t-1\t\n5\t1\t2\t1\t1\t1\t56\t201\t140\t33\t96\tLorem\n5\t1\t2\t1\t1\t2\t215\t199\t136\t45\t95\tipsum\n5\t1\t2\t1\t1\t3\t369\t199\t117\t35\t96\tdolor\n5\t1\t2\t1\t1\t4\t502\t199\t53\t35\t96\tsit\n5\t1\t2\t1\t1\t5\t570\t203\t121\t38\t95\tamet,\n5\t1\t2\t1\t1\t6\t710\t203\t269\t31\t95\tconsectetur\n5\t1\t2\t1\t1\t7\t994\t199\t233\t45\t95\tadipiscing\n4\t1\t2\t1\t2\t0\t6\t255\t616\t35\t-1\t\n5\t1\t2\t1\t2\t1\t6\t255\t78\t35\t94\telit.\n5\t1\t2\t1\t2\t2\t103\t257\t116\t33\t96\tNunc\n5\t1\t2\t1\t2\t3\t235\t264\t50\t26\t95\tac\n5\t1\t2\t1\t2\t4\t301\t255\t195\t35\t95\tfaucibus\n5\t1\t2\t1\t2\t5\t513\t255\t109\t35\t96\todio.\n"


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_data_with_str_image(image):
    data = await aiopytesseract.image_to_data(image)
    assert isinstance(data, str)
    assert data == DATA


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_data_with_bytes_image(image):
    data = await aiopytesseract.image_to_data(Path(image).read_bytes())
    assert isinstance(data, str)
    assert data == DATA


@pytest.mark.asyncio
async def test_image_to_data_with_invalid():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_data("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_image_to_data_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_data(None)
