import tkinter.filedialog as fd
from tkinter import *
from tkinter.ttk import Progressbar

from ocr_client import OCRClient


class Application:
    def __init__(self, master=None):

        self.ocr_client = None

        self.widget1 = Frame(master)
        self.widget1["pady"] = 30
        self.widget1.pack()

        self.selected_folder = ""

        self.msg = Label(self.widget1, text="Pasta selecionada: ")
        self.msg["font"] = ("Verdana", "12", "bold")
        self.msg.pack(side=LEFT, anchor=NW)

        self.dir_label = Label(self.widget1, text=self.selected_folder)
        self.dir_label["text"] = "Nenhuma pasta selecionada"
        self.dir_label["font"] = ("Verdana", "12", "italic", "bold")
        self.dir_label.pack(side=RIGHT, anchor=NE)

        self.widget2 = Frame(master)
        self.widget2["padx"] = 50
        self.widget2.pack()

        self.select_folder = Button(self.widget2)
        self.select_folder["text"] = "Selecionar pasta com as Notas Fiscais"
        self.select_folder["font"] = ("Calibri", "14")
        self.select_folder["width"] = 40
        self.select_folder["pady"] = 10
        self.select_folder["command"] = self.select_dir
        self.select_folder.pack()

        self.run_ocr_button = Button(self.widget2)
        self.__toggle_enable_run_ocr_button()
        self.run_ocr_button["text"] = "Executar"
        self.run_ocr_button["pady"] = 10
        self.run_ocr_button["font"] = ("Calibri", "14")
        self.run_ocr_button["width"] = 40
        self.run_ocr_button["command"] = self.run_ocr
        self.run_ocr_button.pack()

        self.widget3 = Frame(master)
        self.widget3["padx"] = 20
        self.widget3.pack()

        self.progress_count = DoubleVar()

        self.progress_bar = Progressbar(self.widget3, variable=self.progress_count, orient=HORIZONTAL,
                                        length=300, mode='determinate')
        self.progress_bar["value"] = 0
        self.progress_bar.pack()

        self.progress_message_lbl = Label(self.widget3, text="")
        self.progress_message_lbl["font"] = ("Verdana", "12", "bold")
        self.progress_message_lbl.pack()

        # self.sair = Button(self.widget1)
        # self.sair["text"] = "Sair"
        # self.sair["font"] = ("Calibri", "10")
        # self.sair["width"] = 5
        # self.sair["command"] = self.widget1.quit
        # self.sair.pack()

    def select_dir(self):
        folder = self.dir_label["text"] = fd.askdirectory()
        if folder != "":
            self.selected_folder = folder

            self.ocr_client = OCRClient(self.selected_folder)
            self.__toggle_enable_run_ocr_button(state=NORMAL)

    def __toggle_enable_run_ocr_button(self, state=None):
        if state is not None:
            self.run_ocr_button["state"] = state
            return

        if self.run_ocr_button["state"] == DISABLED:
            self.run_ocr_button["state"] = NORMAL
            return

        self.run_ocr_button["state"] = DISABLED

    def run_ocr(self):
        self.ocr_client.run()
        while not self.ocr_client.finished:
            print(self.ocr_client.sent_count)
            print(self.ocr_client.total_count)
            progr = (self.ocr_client.sent_count*100)/self.ocr_client.total_count
            print(progr)
            self.progress_count.set(progr)
            self.progress_message_lbl["text"] = f"{self.ocr_client.sent_count} de {self.ocr_client.total_count}"
            self.widget3.master.update_idletasks()
