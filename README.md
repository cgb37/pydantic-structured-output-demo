# pydantic-structured-output-demo

Demo project showing how to use Pydantic with a modular Quart app for structured output.

Run locally with Docker (development):

```bash
docker compose up --build
```

Visit http://127.0.0.1:8001/ for the UI and http://127.0.0.1:8001/health for a health check.

Run tests:

```bash
pip install -r requirements.txt
pytest -q
```

Project layout (key files):

- `app.py` - entrypoint that creates the app via `webapp.create_app()` and exposes `/health`
- `webapp/` - package containing blueprints and module-specific templates/static
- `docker-compose.yml`, `Dockerfile`, `requirements.txt` - dev infra
# pydantic-structured-output-demo
