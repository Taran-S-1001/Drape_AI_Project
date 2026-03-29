# Fashion Recommendation Studio

Upload a clothing photo, pick a style and occasion, and get five complementary outfit recommendations powered by a local vision model ([Ollama](https://ollama.com/) + **llava**).

## What’s included

- **`main.py`** — FastAPI backend: `/health`, `/recommend` (multipart: image, style, occasion).
- **`index.html`** — Static frontend that calls the API at `http://localhost:8000`.

## Prerequisites

- **Python 3.10+** (recommended)
- **[Ollama](https://ollama.com/download)** installed and running
- Vision model pulled once:

  ```bash
  ollama pull llava
  ```

## Setup

```bash
cd "Clothing project"
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the backend

```bash
python main.py
```

API base: **http://127.0.0.1:8000**

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Keep this terminal open while you use the app.

## Run the frontend

**Option A — open the file**

Double-click `index.html` or open it from your browser.

**Option B — local server (if the browser blocks requests from `file://`)**

In a **second** terminal, from the project folder:

```bash
python -m http.server 8080
```

Then open [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html).

The UI expects the backend on **port 8000** (see `fetch` in `index.html`). Change that URL if you host the API elsewhere.

## Push to GitHub

From the project folder (after [installing Git](https://git-scm.com/downloads)):

```bash
git init
git add .
git commit -m "Initial commit"
```

Create a new repository on GitHub, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

The `.gitignore` excludes `.venv/`, caches, editor files, and common secrets so you don’t upload your virtual environment or junk.

## License

Add a license file if you plan to open-source the project.
