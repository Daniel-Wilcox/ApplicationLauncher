import tkinter as tk
from tkinter import ttk


class NoApplicationPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)

        # Add main page widgets
        text_label = tk.Label(self, text="Need application URL")
        text_label.pack(padx=20, pady=10)

        quit_button = tk.Button(self, text="Quit", command=controller.destroy)
        quit_button.pack(padx=20, pady=10)


class HasApplicationPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)

        # Add main page widgets
        text_label = tk.Label(self, text="Have application URL")
        text_label.pack(padx=20, pady=10)

        quit_button = tk.Button(self, text="Quit", command=controller.destroy)
        quit_button.pack(padx=20, pady=10)


class ApplicationLauncher(tk.Tk):

    def __init__(self, app_available: bool = False):
        super().__init__()

        # Window properties
        self.title("Application Launcher")
        self.geometry("600x100")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()

        if not app_available:
            self.main_page = NoApplicationPage(self)
        else:
            self.main_page = HasApplicationPage(self)

        self.main_page.pack(side="top", fill="both", expand=True)
        self.main_page.grid_rowconfigure(0, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.tkraise()

    

def main():

    # Check if application is available
    application_exists = True

    app = ApplicationLauncher(application_exists)
    app.mainloop()

    

if __name__ == "__main__":
    main()