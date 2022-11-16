import pathlib
import requests
#from pdf2image import convert_from_bytes
import os
from io import BytesIO
from multiprocessing.pool import ThreadPool

EXAMPLE_DIR = pathlib.Path("example_nfes")
PROCESSED_DIR = pathlib.Path("processadas")
MANUAL_DIR = pathlib.Path("manual")

API_URL = "http://localhost:8080/v1"


class OCRClient:
    def __init__(self, root_folder = None):
        if root_folder is None:
            raise Exception("Pasta nao selecionada.")

        self.root_folder = pathlib.Path(root_folder)
        self.thread_pool = ThreadPool(os.cpu_count())
        self.sent_count = 0
        self.total_count = 0
        self.finished = False

    #def pdf_to_image(self, file) -> BytesIO:
    #    print(f"Converting {file} to image...")
    #    with open(EXAMPLE_DIR / pathlib.Path(file), 'rb') as f:
    #        pages = convert_from_bytes(f.read())
    #        buf = BytesIO()
    #        pages[0].save(buf, format="png")
    #        buf.seek(0)
    #    return buf

    def make_request(self, image: BytesIO):
        files = {
            'file': ('nfe.png', image, 'application/octet-stream')
        }
        r = requests.post(f"{API_URL}/nfe_number", files=files)
        print(r.status_code)
        return r

    def file_iterator(self, file):
        from time import sleep
        self.sent_count += 1
        print(f"Sending file {file}")
        with open(self.root_folder / pathlib.Path(file), 'rb') as f:
            image: BytesIO = BytesIO(f.read())
            try:
                self.make_request(image)
            except Exception:
                pass

        if self.total_count == self.sent_count:
            self.finished = True

        sleep(1)

    def run(self):
        files = os.listdir(self.root_folder)
        self.total_count = len(files)
        self.thread_pool.map_async(self.file_iterator, files)
        return len(files)
