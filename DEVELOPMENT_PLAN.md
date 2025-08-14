DEVELOPMENT PLAN

Purpose

This file distills the content of `.github/instructions/project.instructions.md` into a concise development plan for contributors and automated coding agents.

Project context

- Demo of using Pydantic for structured output in Python applications.
- Goal: showcase validation and serialization of complex data structures.

Tech stack

- Python 3.11+
- Pydantic
- Python Quart (HTTP API / demo server)
- pytest (unit tests, pytest-asyncio for async tests)
- docker-compose (containerization)
- Tailwind CSS frontend
- gpt-oss:20b (local model integration)

Key development workflows

1. Environment
- Use Python 3.11. Create a virtualenv or use your preferred environment manager.

2. Install dependencies
- No `requirements.txt` is present by default in the repo; add one or use `pyproject.toml` if present.

3. Running the app
- The project uses a modular Quart app factory in `webapp.create_app()`.
- Top-level `app.py` imports `create_app()` and exposes `/health`.
- Docker (development):

```bash
docker compose up --build
```

The service will be available on http://127.0.0.1:8001/ by default.

4. Tests
- Tests are located in `tests/` and run with `pytest` and `pytest-asyncio`.

Run tests locally (recommended inside venv):

```bash
pip install -r requirements.txt
pytest -q
```

Conventions and patterns

- Follow PEP 8 and use type annotations.
- Use Pydantic models for all input/output shapes and validation.
- Include docstrings for public APIs.

Files to check

- `.github/instructions/project.instructions.md` — canonical project instructions.
- `README.md` — repo-level info.
- `webapp/` — modular Quart package and templates.

Open questions

- Exact entrypoint for running the Quart app (file path).
- Whether dependency manifest (`requirements.txt`/`pyproject.toml`) exists or should be added.
- Any existing tests directory layout.

Next steps

- Run the app with `docker compose up --build` and visit `/` and `/health`.
- Add additional blueprints under `webapp/` (e.g. `api`, `admin`) with their own `templates/` and `static/` subfolders.
- Add CI to run `pytest` on each PR.

References

- See `.github/instructions/project.instructions.md` for the original instructions.
