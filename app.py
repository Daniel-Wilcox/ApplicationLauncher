import platform
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
import json
import PyInstaller.__main__
import requests


# APPLICATION_DIR = ".app"
APPLICATION_DIR = ".temp_github_app"
DEFAULT_CONFIG_FILENAME = "config.json"
REQUIRED_CONFIG_FIELDS = ["version", "app_file", "github_url"]


#! --- VIEWS ---
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

        self.user_entry.focus()

    def get_github_project(self, event=None):

        url = self.project_url.get()

        if not validate_github_url(url):
            messagebox.showwarning(
                parent=self.controller,
                title="Invalid URL",
                message="The provided URL is not a valid GitHub project URL.",
            )
            # self.project_url.set(self.default_project_url)
            return

        print(f"Getting Application project from: {self.project_url.get()}")

        # Download Github to '.app' folder

        # Check if

    # @staticmethod
    # def _validate_github_url(url: str) -> bool:
    #     github_url_pattern = re.compile(
    #         r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/)?$"
    #     )
    #     # https://github.com/username/projectname

    #     if github_url_pattern.match(url):
    #         return True
    #     else:
    #         return False


class LoadingScreenView(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller)

        self.controller = controller

        application_title = self.winfo_toplevel().title()

        self.loading_title = tk.Label(
            master=controller,
            text=f"Launching '{application_title}' application",
        )
        self.loading_title.pack(pady=20)

        self.loading_bar = ttk.Progressbar(master=controller, mode="indeterminate")
        self.loading_bar.pack()

        self.quit_button = tk.Button(
            master=self, text="Quit", command=self.controller.destroy
        )
        self.quit_button.pack(padx=20, pady=10)

        self.loading_bar.start()

    # TODO add in the callback somehow
    def stop_loading_callback(self):
        self.loading_bar.stop()


#! --- Controller ---
class ApplicationController(tk.Tk):

    def __init__(self):
        super().__init__()

        # Define default values
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.application_dir = os.path.join(self.root_dir, APPLICATION_DIR)
        self.exec_path = None
        self.update_status = False

        # Window properties
        self.set_window_properties()

        # Store pages # todo store pages in page list
        ...

        # Set main page #todo assign mainpage name here
        self.set_main_page()

        # Check if app updates are required
        self.update_status = self.check_app_updates()
        if self.update_status:
            self.perform_app_updates()
            self.build_application_executable()
        else:
            # If no updates are required, check if executable or dist folder exists
            # Only remake executable if either dont exist
            self.exec_path = self.get_executable_path()
            dist_path = os.path.join(self.application_dir, "dist")

            if not os.path.exists(self.exec_path) or not os.path.isdir(dist_path):
                self.build_application_executable()

        # Get executable path abd close launcher
        self.exec_path = self.get_executable_path()
        self.destroy()

    def build_application_executable(self):
        print(f"Building executable!")

        # Application folder
        if not os.path.exists(self.application_dir):
            os.mkdir(self.application_dir)

        # Application file
        local_app_file = getattr(self, "local_app_file", None)
        if not local_app_file:
            raise AttributeError(f"The attribute 'local_app_file' does not exist.")

        self.make_app_file = os.path.join(self.application_dir, local_app_file)
        if not os.path.exists(self.make_app_file):
            raise FileNotFoundError(
                f"App file named '{local_app_file}' does not exist in folder: {self.application_dir}"
            )

        # Make executable
        self.dist_path = os.path.join(self.application_dir, "dist")
        self.build_path = os.path.join(self.application_dir, "build")

        pi_command = [
            self.make_app_file,
            "--onedir",
            "--windowed",
            "--distpath",
            self.dist_path,
            "--workpath",
            self.build_path,
            "-y",
        ]
        PyInstaller.__main__.run(pi_command)

    def perform_app_updates(self):

        save_dir = self.application_dir
        app_url = getattr(self, "local_github_url", None)

        # Check if application directory exist:
        if not os.path.exists(save_dir):
            print(f"1. Clone from Github.")
            os.mkdir(save_dir)
            self._clone_github_repo(url=app_url, save_dir=save_dir)  #! New view
            return

        app_dir_empty = not os.listdir(save_dir)
        if app_dir_empty:
            print(f"2. Clone from Github.")
            self._clone_github_repo(url=app_url, save_dir=save_dir)  #! New view
            return

        app_git_filepath = os.path.join(save_dir, ".git")
        if os.path.exists(app_git_filepath):
            print(f"3. Pull from Github.")
            self._pull_github_repo(url=app_url, save_dir=save_dir)
            return

        # Start from scratch
        print("4. Delete all and start from scratch.")
        shutil.rmtree(save_dir, ignore_errors=True)
        os.mkdir(save_dir)
        self._clone_github_repo(url=app_url, save_dir=save_dir)  #! New view
        return

    @staticmethod
    def _clone_github_repo(url: str, save_dir: str):
        subprocess.call(["git", "clone", url, save_dir])

    @staticmethod
    def _pull_github_repo(url: str, save_dir: str):
        subprocess.call(["git", "-C", save_dir, "fetch"])
        subprocess.call(["git", "-C", save_dir, "reset", "--hard", "origin/master"])
        subprocess.call(["git", "-C", save_dir, "pull"])

    def set_window_properties(self):
        # TODO add in config capabilities
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()

    def set_main_page(self):
        # TODO add in ability to pass in View
        self.main_page = LoadingScreenView(controller=self)
        self.main_page.pack(side="top", fill="both", expand=True)
        self.main_page.grid_rowconfigure(0, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.tkraise()

    def check_app_updates(self) -> bool:
        """Check whether the application needs to be updated based on the conditions set in this method.

        Returns:
            bool: Returns a boolean value indicating whether the application needs to be updates (git clone or git pull).
            True = Does require an update
            False = Does not require an update
        """

        # 1. App dir doesn't exist:
        if not os.path.isdir(self.application_dir):
            os.mkdir(self.application_dir)
            return True  # ! Needs update -> clone fresh: New View

        # 2. App dir empty:
        app_dir_files = os.listdir(self.application_dir)
        if not app_dir_files:
            return True  # ! Needs update -> clone fresh: New View

        # 3. No config in app dir
        if DEFAULT_CONFIG_FILENAME not in app_dir_files:
            return True  # ! Needs update -> clone fresh: New View

        # ? Config exists -> get field values
        # 4. Config file is empty or error reading
        self.local_config = self.get_local_config(dir_path=self.application_dir)
        if not self.local_config:
            return True  # ! Needs update -> clone fresh: New View

        # ? Get fields from config
        # 5. missing required fields from config (version, app_file, github_url)
        if not self.config_has_required_fields(config=self.local_config):
            return True  # ! Needs update -> clone fresh: New View

        # Assign local required fields to class
        self.assign_config_fields(config=self.local_config, prefix="local_")

        # ? Get config from github
        # 6. Failed to download config file
        # 7. Download config file is empty
        gh_url = getattr(self, f"local_github_url", None)
        if not gh_url:
            return True

        self.github_config = self.get_github_config(url=gh_url)
        if not self.github_config:
            #! Failed to download JSON or JSON empty
            print(f"github_config failed to load or is empty: {self.github_config = }")
            return True

        # 8. Config file is missing required fields
        if not self.config_has_required_fields(config=self.github_config):
            # ! Needs update -> clone fresh
            print(
                f"github_config missing fields to load or is empty: {self.github_config = }"
            )
            return True

        # Assign github required fields to class
        self.assign_config_fields(config=self.github_config, prefix="github_")

        # ? Compare versions for update
        return self.compare_app_version()

    @staticmethod
    def get_local_config(
        dir_path: str, config_filename: str = DEFAULT_CONFIG_FILENAME
    ) -> dict:
        """Static method which reads and returns the local `config.json` file as a dictionary.

        Args:
            dir_path (str): Folder path where the `config.json` file resides locally.
            config_filename (str, optional): The name of the `config.json` file which defaults to "config.json".

        Returns:
            dict: Returns a dictionary containing all fields read from JSON file. Returns empty dict if unable to read or when any other errors occur.
        """

        config_path = os.path.join(dir_path, config_filename)
        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        return {}

    @staticmethod
    def config_has_required_fields(
        config: dict, fields: list[str] = REQUIRED_CONFIG_FIELDS
    ) -> bool:
        """Static method which check that provided config dict contains all required attributes/fields.

        Args:
            config (dict): Contents of `config.json` read into a non-empty dictionary.
            fields (list[str], optional): The list of fields/attributes expected to appear in the supplied dict which defaults to REQUIRED_CONFIG_FIELDS if no field list is supplied.

        Returns:
            bool: The returned boolean indicates whether all the required fields appear in the supplied dict. The following conditions determine the returned bool:
                - Returns `True` when all required fields/attributes appear in supplied dict.
                - Returns `False` when supplied dict is empty as assumed that there should be a non-empty dict.
                - Returns `True` when the required fields list is empty as assuming all fields are accounted for.
        """

        # Empty config dict or empty fields
        if not config:
            return False

        if not fields:
            return True

        return all(field in config for field in fields)

    def assign_config_fields(
        self,
        config: dict,
        prefix: str = "local_",
        fields: list[str] = REQUIRED_CONFIG_FIELDS,
    ):
        """Assign local class attributes values from the supplied config dictionary and fields list.

        Args:
            config (dict): A dictionary containing fields extracted from a `config.json` file.
            prefix (str, optional): Provides the prefix for local class attribute names which defaults to "local_".
            fields (list[str], optional): List of fields which exist in the which defaults to REQUIRED_CONFIG_FIELDS.
        """

        available_fields = [f for f in fields if f in config]
        for field in available_fields:
            provided_config_field = config.get(field, None)
            class_attr = f"{prefix}{field}"  # i.e version becomes f"local_version
            setattr(self, class_attr, provided_config_field)

    def compare_app_version(self) -> bool:
        """Comparing the local app version to the version of the app on the remote version.

        Returns:
            bool: True if the app requires an update and False if the local app version is up to date. Currently the version check is just comparing int and see if the following is true: (local_version < github_version)
        """
        # Currently the version check is just comparing int and see if:
        # local_version < github_version
        local_version = getattr(self, "local_version", None)
        github_version = getattr(self, "github_version", None)

        if not local_version:
            return True

        if not github_version:
            return True

        if int(local_version) < int(github_version):
            return True

        return False

    @staticmethod
    def get_github_config(
        url: str, config_filename: str = DEFAULT_CONFIG_FILENAME
    ) -> dict:
        """Static method which downloads and returns the `config.json` file from the supplied Github Project URL as a dictionary.

        Args:
            url (str): The Github project URL where the desired `config.json` file resides. The structure of the URL should look something like this: "https://github.com/username/project_name"
            config_filename (str, optional): The list of fields/attributes expected to appear in the supplied dict which defaults to "config.json".

        Returns:
            dict: Returns a dictionary containing all fields read from JSON file at provided URL. Returns empty dict if unable to read or when any other errors occur.
        """

        # Validate Github URL:
        # TODO possibly add more validations
        if not validate_github_url(url):
            # if not "github.com/" in url:
            return {}

        # Get the config.json URL
        split_url = url.rstrip("/").split("/")
        if len(split_url) < 2:
            return {}

        username, project_name = split_url[-2:]
        config_url = f"https://raw.githubusercontent.com/{username}/{project_name}/refs/heads/master/{config_filename}"

        # Try to get the config.json file
        try:
            response = requests.get(
                url=config_url, headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                return response.json()
            return {}

        except Exception as e:
            return {}

    # --------------------------------------------------------------------------------------------------------

    # def check_app_updates(self):

    #     if self.github_version > self.local_version:
    #         print(f"needed to update functions")
    #         # Clone or Pull github
    #         print("getting app")
    #         # self.get_github_app()

    #         # validate application files
    #         # ...

    #         # Build executable with pyinstaller
    #         # self.build_app_executable()

    #         return

    #     # No need to update
    #     self.dist_dir = os.path.join(self.application_dir, "dist")
    #     if not os.path.exists(self.dist_dir):
    #         print(f"Error #10: Dist folder doesn't exist.")
    #         # ! make executable

    #         pyinstaller_command = ...

    #         self.make_app_path = os.path.join(self.application_dir, self.app_file)
    #         # print(rf"pyinstaller {self.make_app_path} --onedir --windowed")
    #         PyInstaller.__main__.run(
    #             [
    #                 self.make_app_path,
    #                 "--onedir",
    #                 "--windowed",
    #                 "--distpath",
    #                 f"{os.path.join(self.application_dir, "dist")}",
    #                 "--workpath",
    #                 f"{os.path.join(self.application_dir, "build")}",
    #                 "-y",
    #             ]
    #         )
    #         # subprocess.call(rf"Pyinstaller {self.make_app_path} --onedir --windowed")

    #     exec_dir = os.path.join(self.dist_dir, "app")
    #     if not os.path.exists(exec_dir):
    #         print(f"Error #11: Application executable doesn't exist.")
    #         # ! make executable

    #         self.make_app_path = os.path.join(self.application_dir, self.app_file)
    #         # print(rf"pyinstaller {self.make_app_path} --onedir --windowed")
    #         PyInstaller.__main__.run(
    #             [
    #                 self.make_app_path,
    #                 "--onedir",
    #                 "--windowed",
    #                 "--distpath",
    #                 f"{os.path.join(self.application_dir, "dist")}",
    #                 "--workpath",
    #                 f"{os.path.join(self.application_dir, "build")}",
    #                 "-y",
    #             ]
    #         )

    #     # Launch app and close launcher
    #     print(f"Success #12: Launching app.")
    #     self.exec_path = self.get_executable_path(self.application_dir, self.app_file)

    # --------------------------------------------------------------------------------------------------------

    # @staticmethod
    # def get_executable_path(application_dir: str, app_filename: str) -> str:
    def get_executable_path(self) -> str:

        # Define variables
        application_dir = self.application_dir
        app_filename = getattr(self, "local_app_file", None)

        if not app_filename:
            raise ValueError(f"Invalid application filename provided: {app_filename}")
        app_name = app_filename.split(".")[0]  # remove .py

        # Get executable name with extension based on platform
        sys_platform = platform.system()
        match sys_platform:
            case "Windows":
                executable_name = f"{app_name}.exe"
            case _:
                executable_name = f"{app_name}"

        # Return executable path: #! may not exist
        return os.path.join(application_dir, "dist", app_name, executable_name)


#! --- Main Logic ---


def validate_github_url(url: str) -> bool:

    # Check if url is not empty
    if not url:
        print(f"Invalid empty URL provided.")
        return False

    # Match Github URL to this pattern
    # https://github.com/username/projectname
    github_url_pattern = re.compile(
        r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/)?$"
    )

    if github_url_pattern.match(url):
        return True
    else:
        return False


def launch_app_from_path(exec_path: str):
    subprocess.Popen([exec_path])


def app_launcher():
    # Init Application Launcher
    app = ApplicationController()
    app.mainloop()

    # Extract execution path and launch new application
    #! NOTE: The code below only runs once the application above is closed.
    exec_path = getattr(app, "exec_path", None)

    # print(f"{'-'*20}\n{exec_path = }\n{'-'*20}\n")

    if not exec_path:
        raise Exception(f"Failed to launch app")
    else:
        app.quit()
        launch_app_from_path(exec_path)


if __name__ == "__main__":
    app_launcher()
