import tkinter as tk

LARGE_FONT = ("Verdana", 12)


class StartView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Define locals
        self.controller = controller

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(
            self,
            text="Visit Page 1",
            command=lambda: print("Changing to 'PageOneView'."),
        )
        button1.pack()

        button2 = tk.Button(
            self,
            text="Visit Page 2",
            command=lambda: print("Changing to 'PageTwoView'."),
        )
        button2.pack()

    def reset_defaults(self):
        pass


class ApplicationController(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add window properties
        self.set_window_properties()

        # Set 'main frame' to be parent of all application views
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Add start view to application's main frame
        first_page = StartView(parent=self.main_frame, controller=self)
        first_page.grid(row=0, column=0, sticky="nsew")
        first_page.tkraise()

    def set_window_properties(self):
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()


def application_launcher():

    # Todo: Add in configuration capabilities for
    app = ApplicationController()
    app.mainloop()


if __name__ == "__main__":
    application_launcher()
