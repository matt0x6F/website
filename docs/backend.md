# Backend Documentation

## API Overview

- The backend is built with **Django** and **Django Ninja** (see `api/` directory).
- All API endpoints are documented and validated via an **OpenAPI v3 schema**.
- The OpenAPI schema is exported with `task export-schema` and used to auto-generate the frontend TypeScript client (`ui/lib/api`).
- To update the schema and SDK after changing endpoints, run:
  ```sh
  task export-schema
  task generate-sdk
  ```
- API endpoints are organized by resource (accounts, posts, series, comments, files, etc.).
- See the [Authentication & Authorization](./authentication-authorization.md) doc for security details.

## Database Schema

- Uses **PostgreSQL** as the primary database.
- Models are defined in Django apps within `api/` (e.g., `blog/models/`, `accounts/models/').
- Migrations are managed with Django's migration system:
  ```sh
  task migrate
  # or
  docker compose exec django poetry run python manage.py migrate
  ```
- For a visual schema, use tools like [django-extensions](https://django-extensions.readthedocs.io/en/latest/graph_models.html) or inspect the models in code.

## Custom Management Commands

- Custom Django management commands can be added in any app's `management/commands/` directory.
- Common commands are automated in the [Taskfile.yml](../Taskfile.yml):
  - `task migrate`, `task create-super-user`, `task export-schema`, `task load-fixtures`, etc.
- Always run management commands inside the running `django` Docker container.

## Error Handling

- API errors are returned as JSON with appropriate HTTP status codes (e.g., 400, 403, 404, 500).
- Validation errors follow the OpenAPI schema and are handled by Django Ninja.
- Logging is managed with `structlog` for structured, context-rich logs.
- For debugging, check logs in the Docker container or use Django's debug mode in development.

For more details, see the code in the `api/` directory and the [Getting Started](./getting-started.md) and [Development Workflow](./development-workflow.md) docs. 