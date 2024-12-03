import tkinter as tk
from tkinter import ttk, messagebox
import re


class HasApplicationView(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        # define defaults and load widgets
        text_label = tk.Label(self, text="Has application URL")
        text_label.pack(padx=20, pady=10)

        quit_button = tk.Button(self, text="Quit", command=self.controller.destroy)
        quit_button.pack(padx=20, pady=10)


class DoesNotHaveApplicationView(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        # define defaults
        self.default_project_url = ""
        self.project_url = tk.StringVar(value=self.default_project_url)

        # Load widgets
        # Text label
        text_label = tk.Label(self, text="Please provide application's GitHub URL:")
        text_label.pack(padx=20, pady=10)

        # Add user entry widget
        self.user_entry = tk.Entry(self, textvariable=self.project_url)
        self.user_entry.pack()

        # Define a callback for when the user hits return.
        self.user_entry.bind("<Key-Return>", self.get_github_project)

        quit_button = tk.Button(self, text="Quit", command=self.controller.destroy)
        quit_button.pack(padx=20, pady=10)

    def get_github_project(self, event=None):

        url = self.project_url.get()

        if not self._validate_github_url(url):
            messagebox.showwarning(
                "Invalid URL", "The provided URL is not a valid GitHub project URL."
            )
            self.project_url.set(self.default_project_url)

            return

        print(f"Getting Application project from: {self.project_url.get()}")

    @staticmethod
    def _validate_github_url(url: str) -> bool:
        github_url_pattern = re.compile(
            r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/)?$"
        )

        if github_url_pattern.match(url):
            return True
        else:
            return False


class ApplicationController(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window properties
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()
        self.set_main_page()

    def set_main_page(self):

        application_path_exists = True
        if application_path_exists:
            self.main_page = HasApplicationView(controller=self)
        else:
            self.main_page = DoesNotHaveApplicationView(controller=self)

        self.main_page.pack(side="top", fill="both", expand=True)
        self.main_page.grid_rowconfigure(0, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.tkraise()


def app_launcher():
    app = ApplicationController()
    app.mainloop()


if __name__ == "__main__":
    app_launcher()
