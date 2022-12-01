import errno
import pathlib
import requests
#from pdf2image import convert_from_bytes
import os
from io import BytesIO
from multiprocessing.pool import ThreadPool

EXAMPLE_DIR = pathlib.Path("example_nfes")
PROCESSED_DIR = pathlib.Path("processadas")
MANUAL_DIR = pathlib.Path("manual")

#API_URL = "http://localhost:8080/v1/nfe_number"
API_URL = "https://python-http-function-b26i67gfva-uk.a.run.app"
#API_URL = "http://localhost:8080"


class OCRClient:
    PROCESSED = 1
    ERROR = 2

    def __init__(self, root_folder=None, dest_folder=None):
        if root_folder is None:
            raise Exception("Pasta nao selecionada.")

        if dest_folder is None:
            raise Exception("Pasta destino nao selecionada.")

        self.root_folder = pathlib.Path(root_folder)
        self.dest_folder = pathlib.Path(dest_folder)
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
        r = requests.post(f"{API_URL}", files=files)
        return r

    def move_file(self, filename, target, rename=None):
        if rename is None:
            dest = filename
        else:
            dest = rename

        os.rename(self.root_folder/filename, self.root_folder/target/dest)

    def __find_dir(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in dirs:
                return os.path.join(root, name)
        return None

    def find_target_dir(self, ch_nfe: str):
        # CNPJ(NOME DA EMPRESA)/ANO/SEMESTRE(PRIMEIRO,SEGUNDO)/MUNICIPIO/ESCOLA/NF_AUT_TERMO/NF 123123123/nf.pdf
        cnpjs = {
            "91360420000134": "OURO DO SUL",
            "01112137000109": "COOTAP_POA",
            "83310441006239": "AURORA",
            "02609254000137": "COOPAT_TAPES"
        }
        ano = "20" + str(ch_nfe[2:4])
        semestre = "PRIMEIRO" if int(ch_nfe[4:6]) < 7 else "SEGUNDO"
        cnpj = ch_nfe[6:20]
        numero_nf = str(ch_nfe[25:34]).lstrip("0")

        partial_path = pathlib.Path(self.dest_folder) / cnpjs[cnpj] / ano / semestre

        fname = f"NF {numero_nf}"

        print(f"Searching dir: {str(partial_path)}")
        target = self.__find_dir(fname, partial_path)
        if target is None:
            return None

        return pathlib.Path(target)

    def file_iterator(self, file):
        print(f"Enviadas: {self.sent_count}/{self.total_count}")
        self.sent_count += 1
        print(f"Sending file {file}")
        filepath = self.root_folder / pathlib.Path(file)
        with open(filepath, 'rb') as f:
            image: BytesIO = BytesIO(f.read())
            req = self.make_request(image)
            print(f"Received response for {file}")
            if req.status_code != 200:
                self.move_file(filename=pathlib.Path(file), target=MANUAL_DIR)
            else:
                ch_nfe = req.json()["nfe_number"]
                numero_nf = str(ch_nfe[25:34]).lstrip("0")

                target = self.find_target_dir(ch_nfe)

                if target is None:
                    self.move_file(filename=pathlib.Path(file), target=MANUAL_DIR, rename=f"NF {numero_nf}.pdf")
                else:
                    self.move_file(filename=pathlib.Path(file), target=target, rename=f"NF {numero_nf}.pdf")

        if self.total_count == self.sent_count:
            self.finished = True

    def __create_dirs(self):
        try:
            os.makedirs(self.root_folder/PROCESSED_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        try:
            os.makedirs(self.root_folder/MANUAL_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def run(self):
        self.__create_dirs()
        files = []
        for f in os.listdir(self.root_folder):
            if str(f).endswith("pdf"):
                files.append(f)
        self.total_count = len(files)
        self.thread_pool.map_async(self.file_iterator, files)
        return len(files)
