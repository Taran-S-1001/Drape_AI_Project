# Drape AI

Drape AI is a small app: you upload a photo of something you’re wearing or considering, choose a style and an occasion, and it returns five complementary pieces. The heavy lifting runs locally through [Ollama](https://ollama.com/) using the **llava** model—no cloud API for the vision part.

`main.py` is a FastAPI server (`/recommend` takes the image plus `style` and `occasion` as form fields). `index.html` is a plain static page that posts to `http://localhost:8000`; open it in a browser once the server is up.

---

You’ll need Python 3.10 or newer, Ollama installed and running, and the model pulled once:

```bash
ollama pull llava
```

Create a venv, install deps, start the API:

```bash
cd path/to/Clothing project
python -m venv .venv
```

On Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

On macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

That listens on **http://127.0.0.1:8000**. Swagger UI is at `/docs` if you want to try the endpoint without the HTML page.

For the UI, double-click `index.html` or open it from the file menu. If the browser complains about talking to the API, serve the folder instead:

```bash
python -m http.server 8080
```

…then go to `http://127.0.0.1:8080/index.html`. Keep `main.py` running in another terminal, and leave Ollama running in the background.

If you change where the API is hosted, edit the `fetch` URL near the bottom of `index.html`.
