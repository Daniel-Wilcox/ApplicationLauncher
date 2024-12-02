import tkinter as tk
from tkinter import ttk


class ApplicationLauncher(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window properties
        self.title("Application Launcher")
        self.geometry("600x100")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()

    

def main():
    app = ApplicationLauncher()
    app.mainloop()

    

if __name__ == "__main__":
    main()