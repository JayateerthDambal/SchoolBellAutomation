# School Bell Automatiom

## Installation
```
pyinstaller  --add-data "templates;templates" --add-data "static;static" --add-data "sounds;sounds" --add-data "static;static" --add-data "bell.ico;."  --hidden-import=flask --onefile app.py
```