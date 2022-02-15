FROM python:3.10.2-slim

RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    rm -rf /var/cache/apt/*
RUN pip install streamlit aiopytesseract

CMD ["run", "https://github.com/amenezes/aiopytesseract/blob/master/examples/streamlit/app.py"]
ENTRYPOINT ["streamlit"]
