# Application Launcher

This project focuses on creating an application launcher which will check for updates and dynamically create the application executable.


## Application Flow
This project will be using the Model-View-Controller (MVC) model for the application GUI. Despite this project being a simple application, the learnings of using the MVP model here will translate in improving any future complex applications. For a great visual explanation, see this [Stack Overflow response](https://stackoverflow.com/a/25816573).


# Program goals:
- Display launcher page:
  - Loading page while update checks are happening in the background
- The application launcher will be made and distributed for Windows and Unix based systems. 
- Desired application to launch will be stored online as a GitHub project with a `config.json` file.
- Desired application to launch will be stored locally in a hidden folder.
- The local and github config.json fields are compared and determined if an update is required. The project is downloaded and an executable is made & opened.
