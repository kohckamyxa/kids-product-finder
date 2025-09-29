# kids-product-finder
A browser extension that finds local purchasing options for baby and children's products for families living abroad.

## Deployment
1. Create a Render Web Service pointing at this repository and choose a Python environment.
2. Set the Build Command to `./deploy.sh build` so Render installs backend dependencies listed in `backend/requirements.txt`.
3. Set the Start Command to `./deploy.sh start`; the script ensures Chromium is available and launches Gunicorn bound to `$PORT`.
4. Keep `PORT` provided by Render and add any other env vars (e.g., proxies) via the Render dashboard.
5. After the service is live, reload the browser extension pointing to the new Render URL so background fetches hit the deployed backend.

For other hosts, adapt `deploy.sh` to the platform's package manager (the backend expects headless Chrome and the packages from `backend/requirements.txt`).
