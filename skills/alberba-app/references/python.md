# Python

- `pyproject.toml` y `uv.lock` se versionan. Dependencias con `uv add`; las de desarrollo con `uv add --dev ruff pytest`.
- Control de edad: `[tool.uv]` con `exclude-newer = "1 day"` en `pyproject.toml`. uv acepta duraciones relativas.
- Dependabot: bloque [assets/dependabot/uv.yml](../assets/dependabot/uv.yml) (ecosistema `uv`) y, si hay `Dockerfile`, [docker.yml](../assets/dependabot/docker.yml); siempre [actions.yml](../assets/dependabot/actions.yml).
- Auditoría: [assets/audit.uv.yml](../assets/audit.uv.yml), con `uv audit`.
- CI: [assets/ci.uv.yml](../assets/ci.uv.yml), con `uv sync --locked`, `ruff check`, `ruff format --check` y `pytest`.
- Docker: imagen `python:{{python}}-slim` e instalación con `uv sync --locked --no-dev`.
