import os
import pathlib
import requests
from pdf2image import convert_from_bytes
from io import BytesIO

EXAMPLE_DIR = pathlib.Path("example_nfes")
API_URL = "http://localhost:8080/v1"


def pdf_to_image(file) -> BytesIO:
    with open(EXAMPLE_DIR / pathlib.Path(file), 'rb') as f:
        pages = convert_from_bytes(f.read())
        buf = BytesIO()
        pages[0].save(buf, format="png")
        buf.seek(0)
    return buf


def make_request(image: BytesIO):
    files = {
        'file': ('nfe.png', image, 'application/octet-stream')
    }
    r = requests.post(f"{API_URL}/nfe_number", files=files)
    return r


def run_example():
    for file in os.listdir(EXAMPLE_DIR):
        print(f"Sending file {file}")
        image: BytesIO = pdf_to_image(file)
        make_request(image)
        pass
    pass


if __name__ == "__main__":
    run_example()
