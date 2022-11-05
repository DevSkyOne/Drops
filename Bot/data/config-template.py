import sys

# TODO: Erstelle eine neue Datei `config.py` in diesem Ordner und füge dort den Token ein. Nachdem du den Token
#  eingefügt hast, pushe den file NICHT auf GitHub (zur Sicherheit ist er in der .gitignore eingetragen)
TOKEN = ""  # Kann natürlich auch über envs, einen secrets server o.ä. geregelt werden
IS_LOCAL = sys.platform == 'win32'  # Wenn ihr Linux nutzt, müsst ihr das natürlich anpassen/manuel auf True setzen

if IS_LOCAL:
    MAIN_GUILD = 829654827859836971  # https://discord.gg/YecvKa8aUv
else:
    MAIN_GUILD = 443790920576532490  # https://discord.gg/devsky


# Database connection
DB_HOST = "localhost:3306"
DB_USER = "root"
DB_PASS = "root"
DB_NAME = "dropbot"
