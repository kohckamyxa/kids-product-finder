# Repository Guidelines

## Project Structure & Module Organization
- `backend/` houses the Flask API in `app.py`; Selenium-based scrapers live here alongside the service registry in `STORES`.
- Python dependencies are pinned in `backend/requirements.txt`; keep browser-driver notes close to that file when updating.
- `extension/` contains the Chrome MV3 extension: background messaging (`background.js`), DOM scraping (`content.js`), popup UI assets, and `icons/`.
- No dedicated test directory exists yet; create `backend/tests/` or `extension/__tests__/` when adding automation to keep scopes separated.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create and enter an isolated environment before backend work.
- `pip install -r backend/requirements.txt` — install Flask, Selenium, and other backend dependencies.
- `python backend/app.py` — run the API locally on port 5000; verify logs for translation and scraping output.
- `curl -X POST http://localhost:5000/api/search -H 'Content-Type: application/json' -d '{"productName":"stroller"}'` — smoke test the endpoint before wiring the extension.
- Load the `extension/` folder as an unpacked extension in Chrome; use the popup to trigger calls against the running backend.

## Coding Style & Naming Conventions
- Python: follow PEP 8, 4-space indents, and descriptive helper names (e.g. `scrape_product_with_selenium`); prefer double quotes for strings to match current files.
- JavaScript: keep two-space indents, camelCase function names, and inline comments only where the flow is non-obvious.
- Centralize new store metadata inside `STORES`; mirror the dict shape so the generic scraper keeps working.

## Testing Guidelines
- Add unit tests for pure helpers (e.g. translation utilities) under a new `backend/tests/` using `pytest`; aim to cover store config edge cases.
- For DOM changes, document manual test steps in the PR (URL tested, product name captured, expected affiliate link).
- Record extension smoke tests after every change touching messaging: popup interaction, background fetch, content script scrape.

## Commit & Pull Request Guidelines
- Recent commits favor concise, present-tense summaries (e.g. "Update app.py"); keep messages under ~50 chars and expand context in the body if needed.
- Reference related work with `Refs #issue` in the body, and group backend vs extension updates clearly.
- Pull requests should include: 1) short problem statement, 2) screenshots or console output for manual tests, 3) callouts for new store configs or Selenium options.
