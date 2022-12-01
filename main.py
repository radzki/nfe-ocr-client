import tkinter as tk
from application import Application


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Leitor de Notas Fiscais v1.0")
    root.minsize(750, 250)
    Application(root)
    root.mainloop()
