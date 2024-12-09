from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)


class AbstractView(ABC, tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    @abstractmethod
    def load_widgets(self):
        """Abstract method to load the view's widgets"""

    @abstractmethod
    def reset_defaults(self):
        """Abstract method to reset the view's default values"""


class StartView(AbstractView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Define locals
        ...

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(
            self,
            text="Test: Loading Page.",
            command=lambda: self.controller.change_view(LoadingScreenView),
        )
        button1.pack()

        button2 = tk.Button(
            self,
            text="Test: Github Page.",
            command=lambda: self.controller.change_view(ApplicationGithubUrlView),
        )
        button2.pack()

    def reset_defaults(self):
        print(f"Resetting defaults for Start")


class ApplicationGithubUrlView(AbstractView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Define locals
        self.default_project_url = ""  # TODO: either config or init variable
        self.project_url = tk.StringVar(value=self.default_project_url)

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        text_label = tk.Label(self, text="Please provide application's GitHub URL:")
        text_label.pack(padx=20, pady=10)

        # Add user entry widget
        self.user_entry = tk.Entry(self, textvariable=self.project_url)
        self.user_entry.pack()

        # Define a callback for when the user hits return.
        self.user_entry.bind("<Key-Return>", self.get_github_project)

        submit_button = tk.Button(self, text="Submit", command=self.get_github_project)
        submit_button.pack(padx=20, pady=10)

        home_button = tk.Button(
            self,
            text="Back Home",
            command=lambda: self.controller.change_view(StartView),
        )
        home_button.pack(padx=20, pady=10)

        quit_button = tk.Button(self, text="Quit", command=self.controller.destroy)
        quit_button.pack(padx=20, pady=10)

        self.user_entry.focus()

    def get_github_project(self, event=None):
        url = self.project_url.get()
        print(f"Getting application from: {url}")

    def reset_defaults(self):
        print(f"Resetting defaults for URL")


class LoadingScreenView(AbstractView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Define locals
        self.application_title = "Classic Eyes WATI"

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        self.loading_title = tk.Label(
            self,
            text=f"Launching '{self.application_title}' application",
        )
        self.loading_title.pack(pady=20)

        self.loading_bar = ttk.Progressbar(self, mode="indeterminate")
        self.loading_bar.pack()

        home_button = tk.Button(
            self,
            text="Back Home",
            command=self.loading_home,
        )
        home_button.pack(padx=20, pady=10)

        self.quit_button = tk.Button(self, text="Quit", command=self.loading_quit)
        self.quit_button.pack(padx=20, pady=10)

        self.loading_bar.start()

    def loading_home(self):
        self.loading_bar.stop()
        self.controller.change_view(StartView)

    def loading_quit(self):
        self.loading_bar.stop()
        self.controller.destroy()

    def reset_defaults(self):
        print(f"Resetting defaults for Loading")
        self.loading_bar.start()


class ApplicationController(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Define defaults
        self.current_view_class = None

        # Add window properties
        self.set_window_properties()

        # Set 'main frame' to be parent of all application views
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Add all available views with dictionary comprehension
        self.available_views: dict[AbstractView, AbstractView] = {
            ViewClass: ViewClass(parent=self.main_frame, controller=self)
            for ViewClass in (
                StartView,
                ApplicationGithubUrlView,
                LoadingScreenView,
            )
        }

        for view in self.available_views.values():
            view.grid(row=0, column=0, sticky="nsew")

        # Show first page
        first_page = next(iter(self.available_views.values()))
        first_page.tkraise()

    def set_window_properties(self):
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()

    def change_view(
        self, view_class: tk.Frame | None = None, reset_defaults: bool = True
    ):
        new_view_obj: tk.Frame | None
        view_class_str = str(view_class.__name__)

        print(f"Changing View: {view_class_str}.")

        if not view_class:
            raise NotImplementedError(
                f"Attribute 'view_class' must be provided and expected to have a type of: {type(tk.Frame)}"
            )

        # Compare old and new views
        old_view_class = self.current_view_class
        if view_class == old_view_class:
            return

        # Update current view
        self.current_view_class = view_class

        new_view_obj = self.available_views.get(view_class, None)
        if not new_view_obj:
            available_views_list = [
                str(v.__class__.__name__) for v in self.available_views.keys()
            ]
            raise AttributeError(
                f"View '{view_class}' does not exist in available views list: {', '.join(available_views_list)}."
            )

        # Change views
        if reset_defaults:
            new_view_obj.reset_defaults()

        new_view_obj.tkraise()


def application_launcher():

    # Todo: Add in configuration capabilities for
    app = ApplicationController()
    app.mainloop()


if __name__ == "__main__":
    application_launcher()
