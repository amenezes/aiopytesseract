[![ci](https://github.com/amenezes/aiopytesseract/actions/workflows/ci.yml/badge.svg)](https://github.com/amenezes/aiopytesseract/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/amenezes/aiopytesseract/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/aiopytesseract)
[![PyPI version](https://badge.fury.io/py/aiopytesseract.svg)](https://badge.fury.io/py/aiopytesseract)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiopytesseract)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# aiopytesseract

asyncio tesseract wrapper for [Tesseract-OCR]().

## Installing

Install and update using pip:

````bash
pip install aiopytesseract
````

## Usage

```python
from pathlib import Path

import aiopytesseract


# list all available languages by tesseract installation
await aiopytesseract.languages()
await aiopytesseract.get_languages()


# tesseract version
await aiopytesseract.tesseract_version()
await aiopytesseract.get_tesseract_version()


# confidence only info
await aiopytesseract.confidence("tests/samples/file-sample_150kB.png")


# deskew info
await aiopytesseract.deskew("tests/samples/file-sample_150kB.png")


# extract text from an image: locally or bytes
await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_string(
	Path("tests/samples/file-sample_150kB.png")read_bytes(), dpi=220, lang='eng+por'
)


# box estimates
await aiopytesseract.image_to_boxes("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_boxes(Path("tests/samples/file-sample_150kB.png")


# boxes, confidence and page numbers
await aiopytesseract.image_to_data("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_data(Path("tests/samples/file-sample_150kB.png")


# information about orientation and script detection
await aiopytesseract.image_to_osd("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_osd(Path("tests/samples/file-sample_150kB.png")


# generate a searchable PDF
await aiopytesseract.image_to_pdf("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_pdf(Path("tests/samples/file-sample_150kB.png")


# generate HOCR output
await aiopytesseract.image_to_hocr("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_hocr(Path("tests/samples/file-sample_150kB.png")


# multi ouput
async with aiopytesseract.run(
	Path('tests/samples/file-sample_150kB.png').read_bytes(),
	'output',
	'alto tsv txt'
) as resp:
	# will generate (output.xml, output.tsv and output.txt)
	print(resp)
	alto_file, tsv_file, txt_file = resp
```

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: [https://github.com/amenezes/aiopytesseract](https://github.com/amenezes/aiopytesseract)
- Issue tracker: [https://github.com/amenezes/aiopytesseract/issues](https://github.com/amenezes/aiopytesseract/issues)
- Docs: [https://aiopytesseract.amenezes.net](https://github.com/amenezes/aiopytesseract)
