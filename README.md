# securebank-gh500

## Run locally (Windows PowerShell)

Create a project environment and install the dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe app.py
```

In VS Code, select `.venv\Scripts\python.exe` using **Python: Select Interpreter**.
Open http://127.0.0.1:5000/health to check the application.

Flask and Werkzeug 2.2.2 are incompatible with Python 3.14 because they use
removed standard-library APIs, including `pkgutil.get_loader` and `ast.Str`.
Use the versions pinned in `requirements.txt`; do not patch the standard library.

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_app.py -q
```