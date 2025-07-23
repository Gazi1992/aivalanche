Here are some general remarks:
1. This is a visualization app which has a backend and a frontend. In addition it has the electron folder, which is responsible for making it a desktop app.
2. The basic idea is that there exists a json config file, ex. sample_config.json, which is the input to this app. In this config file, all the details for all the plots are specified.
3. There exists a config_schema.py, where all the properties of all types of plots are listed.
4. There is a config_loader.py, which makes sure to read and validate all the config data.
5. There is also a data_handler.py, which is reponsible for reading the data from files and converting them to the required format, ex. pandas dataframes.
6. Then there is the plot_factory.py and the dashboard_builder.py, where the plots are actually created.
7. On the frontend side, there is a themes.css file, which is responsible for the centralized theming of the app.
8. There are log files, backend_debug.log, frontend_payload.log, which are the places to check any errors in case of problems.
9. There is also a docs folder, where info about the app is written. Changes in the config_schema should also be reflected into the config_reference.md.
10. Please do not try to run the frontend or backend code, because i have them already running from other terminals and the moment you do any changes, they are automatically reflected into the opend app, so no need to run or build anything.