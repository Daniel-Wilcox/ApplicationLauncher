import platform
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
import json
import PyInstaller.__main__
import requests
import threading
import asyncio


# APPLICATION_DIR = ".app"
APPLICATION_DIR = ".temp_github_app"
CONFIG_FILE = "config.json"


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

        if not self._validate_github_url(url):
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

    @staticmethod
    def _validate_github_url(url: str) -> bool:
        github_url_pattern = re.compile(
            r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/)?$"
        )
        # https://github.com/username/projectname

        if github_url_pattern.match(url):
            return True
        else:
            return False


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


class ApplicationController(tk.Tk):

    def __init__(self):
        super().__init__()

        # Define default values
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.application_dir = os.path.join(self.root_dir, APPLICATION_DIR)

        # Window properties
        self.title("Application Launcher")
        self.geometry("600x200")
        self.eval("tk::PlaceWindow . center")
        self.focus_force()

        # Set main page
        self.set_main_page()

        # Check if app updates are required
        self.check_app_updates()

        # Launch app and close launcher
        self.destroy()
        self.run_executable(self.application_dir, self.app_file)
        # self.destroy()

    def check_app_updates(self):

        # Check .app exists
        if not os.path.isdir(self.application_dir):
            print(f"Error #1: no {self.application_dir} folder")

            # os.mkdir(self.application_dir)
            # ! NEW VIEW ! Ask user for URL
            return

        # Check if .app is empty
        app_files = os.listdir(self.application_dir)
        if not app_files:
            print(f"Error #2: {self.application_dir} folder is empty")

            # App files are empty
            # ! NEW VIEW ! Ask user for URL
            return

        # Check config file exists (check versions)
        if CONFIG_FILE not in app_files:
            print(
                f"Error #3: {self.application_dir} folder doesn't have 'config.json'."
            )
            # Need to download git
            # ! NEW VIEW ! Ask user for URL
            return

        # Check local config.json values
        self.config_path = os.path.join(self.application_dir, CONFIG_FILE)
        try:
            with open(self.config_path, "r") as f:
                self.local_config = json.load(f)
        except json.JSONDecodeError as e:
            self.local_config = {}

        if not self.local_config:
            print(f"Error #4: Local config.json file is empty or doesn't exist.")

            # Create config file
            # ! NEW VIEW ! Ask user for URL
            return

        # Check local application version
        self.local_version = self.local_config.get("version", None)
        if not self.local_version:
            print(f"Error #5: Local config.json doesn't have 'version' field.")

            # no app version
            # ! NEW VIEW ! Ask user for URL

            return

        self.app_file = self.local_config.get("app_file", None)
        if not self.app_file:
            print(f"Error #6: Local config.json doesn't have 'app_file' field.")

            # no app version
            # ! NEW VIEW ! Ask user for URL
            return

        self.github_url = self.local_config.get("github_url", None)
        if not self.github_url:
            print(f"Error #7: Local config.json doesn't have 'github_url' field.")

            # no app version
            # ! NEW VIEW ! Ask user for URL
            return

        # Get config from Github
        self.gh_username = self.github_url.split("/")[-2]
        self.gh_project_name = self.github_url.split("/")[-1]
        self.github_config_url = f"https://raw.githubusercontent.com/{self.gh_username}/{self.gh_project_name}/refs/heads/master/config.json"

        try:
            r = requests.get(
                url=self.github_config_url, headers={"Accept": "application/json"}
            )
            self.github_config = r.json()
        except Exception as e:
            print(
                f"Error #8: Couldn't read config.json file from URL: {self.github_config_url}"
            )
            self.github_config = {}

        if not self.github_config:
            # Failed to download config
            print(
                f"Error #9: Couldn't read config.json file from URL: {self.github_config_url}"
            )
            return

        # Compare local and github versions
        self.github_version = self.github_config.get("version", None)
        print(f"{self.local_version = }")
        print(f"{self.github_version = }")

        if self.github_version > self.local_version:
            print(f"needed to update functions")
            # Clone or Pull github
            self.get_github_app()

            # validate application files
            ...

            # Build executable with pyinstaller
            self.build_app_executable()

            return

        # No need to update
        self.dist_dir = os.path.join(self.application_dir, "dist")
        if not os.path.exists(self.dist_dir):
            print(f"Error #10: Dist folder doesn't exist.")
            # ! make executable

            pyinstaller_command = ...

            self.make_app_path = os.path.join(self.application_dir, self.app_file)
            # print(rf"pyinstaller {self.make_app_path} --onedir --windowed")
            PyInstaller.__main__.run(
                [
                    self.make_app_path,
                    "--onedir",
                    "--windowed",
                    "--distpath",
                    f"{os.path.join(self.application_dir, "dist")}",
                    "--workpath",
                    f"{os.path.join(self.application_dir, "build")}",
                    "-y",
                ]
            )
            # subprocess.call(rf"Pyinstaller {self.make_app_path} --onedir --windowed")

        exec_dir = os.path.join(self.dist_dir, "app")
        if not os.path.exists(exec_dir):
            print(f"Error #11: Application executable doesn't exist.")
            # ! make executable

            self.make_app_path = os.path.join(self.application_dir, self.app_file)
            # print(rf"pyinstaller {self.make_app_path} --onedir --windowed")
            PyInstaller.__main__.run(
                [
                    self.make_app_path,
                    "--onedir",
                    "--windowed",
                    "--distpath",
                    f"{os.path.join(self.application_dir, "dist")}",
                    "--workpath",
                    f"{os.path.join(self.application_dir, "build")}",
                    "-y",
                ]
            )
            # subprocess.call(rf"Pyinstaller {self.make_app_path} --onedir --windowed")

        # Launch app and close launcher
        print(f"Success #12: Launching app.")
        # self.run_executable(self.application_dir, self.app_file)
        # self.destroy()

        return

    @staticmethod
    def run_executable(application_dir: str, app_filename: str):
        sys_platform = platform.system()

        app_name = app_filename.split(".")[0]

        match sys_platform:
            case "Windows":
                executable_name = f"{app_name}.exe"
            case _:
                executable_name = f"{app_name}"

        #  "/Users/daniel/Desktop/PythonProjects/ApplicationLauncher/.temp_github_app/dist/app/app"
        exec_path = os.path.join(application_dir, "dist", app_name, executable_name)
        os.system(exec_path)
        return

    def set_main_page(self):

        self.main_page = LoadingScreenView(controller=self)

        self.main_page.pack(side="top", fill="both", expand=True)
        self.main_page.grid_rowconfigure(0, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.tkraise()


def app_launcher():
    app = ApplicationController()
    app.mainloop()


if __name__ == "__main__":
    app_launcher()
