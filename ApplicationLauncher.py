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
            command=lambda: self.controller.change_view(PageOneView),
        )
        button1.pack()

        button2 = tk.Button(
            self,
            text="Visit Page 2",
            command=lambda: self.controller.change_view(PageTwoView),
        )
        button2.pack()

    def reset_defaults(self):
        pass


class PageOneView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        # Define locals
        self.controller = controller

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(
            self,
            text="Back to Home",
            command=lambda: self.controller.change_view(StartView),
        )
        button1.pack()

        button2 = tk.Button(
            self,
            text="Page Two",
            command=lambda: self.controller.change_view(PageTwoView),
        )
        button2.pack()

    def reset_defaults(self):
        pass


class PageTwoView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        # Define locals
        self.controller = controller

        # Initialise Widgets
        self.load_widgets()

    def load_widgets(self):
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(
            self,
            text="Back to Home",
            command=lambda: self.controller.change_view(StartView),
        )
        button1.pack()

        button2 = tk.Button(
            self,
            text="Page One",
            command=lambda: self.controller.change_view(PageOneView),
        )
        button2.pack()

    def reset_defaults(self):
        pass


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
        self.available_views: dict = {
            ViewClass: ViewClass(parent=self.main_frame, controller=self)
            for ViewClass in (StartView, PageOneView, PageTwoView)
        }

        available_views_list = [str(v.__name__) for v in self.available_views.keys()]
        print(f"All views: {available_views_list}\n")

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

    def change_view(self, view_class: tk.Frame | None = None):
        new_view_obj: tk.Frame | None
        view_class_str = str(view_class.__name__)

        print(f"Starting: change_view({view_class_str}).")

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
        new_view_obj.tkraise()


def application_launcher():

    # Todo: Add in configuration capabilities for
    app = ApplicationController()
    app.mainloop()


if __name__ == "__main__":
    application_launcher()
