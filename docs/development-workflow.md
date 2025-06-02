# Development Workflow

## Branching Strategy

- Use feature branches for all new work: `feature/your-feature-name`.
- Bugfixes: `fix/your-bug-description`.
- **Main branch:**
  - `main` — the only long-lived branch; always production-ready and deployable.
  - Production deployments (see [`deploy_blog.sh`](../deploy_blog.sh)) always use `main`.
- Pull requests (PRs) should be opened against `main` and require code review before merging.

## Code Style & Linting

- **Frontend:**
  - Linting: ESLint with TypeScript, Vue, and Playwright plugins.
  - Formatting: Prettier and EditorConfig.
  - Run: `npm run lint` and `npm run format` in `ui/`.
- **Backend:**
  - Linting: Use Poetry-managed tools (e.g., `ruff`).
  - Formatting: Black, isort (if configured).
  - Run: `task lint` or `docker compose exec django poetry run ruff .` in `api/`.

## Testing

- **Frontend:**
  - Unit tests: Vitest (`npm run test:unit` in `ui/`).
  - E2E tests: Playwright (`npm run test:e2e` in `ui/`).
  - Type checking: `vue-tsc --noEmit`.
- **Backend:**
  - Unit/integration tests: Pytest (`task test` or `docker compose exec django poetry run pytest`).
- **CI:**
  - All tests and linters are run in CI (see `.github/workflows/ci.yml`).

## Common Tasks

- Use the `Taskfile.yml` for automation:
  - `task up` / `task down` — start/stop dev environment
  - `task migrate` — run migrations
  - `task create-super-user` — create Django superuser
  - `task export-schema` — export OpenAPI schema
  - `task generate-sdk` — regenerate frontend API client
  - `task build` — build frontend and collect static files
  - `task load-fixtures` — load all fixtures
- For backend management commands, always run them inside the running `django` Docker container.

See the [Getting Started](./getting-started.md) doc for setup, and the [Taskfile.yml](../Taskfile.yml) for all available tasks. 