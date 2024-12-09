import tkinter as tk


class Application(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add window properties
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()


def application_launcher():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    application_launcher()
