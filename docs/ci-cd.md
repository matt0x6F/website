# CI/CD & Deployment

## CI Pipeline

The project uses **GitHub Actions** for continuous integration, defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml):

- **Runs on:** Ubuntu-latest.
- **Services:** PostgreSQL (for backend tests).
- **Workflow Steps:**
  1. **Checkout code**: Clones the repository.
  2. **Set up Python and Node.js**: Installs the required versions for backend and frontend.
  3. **Cache dependencies**: Caches Poetry and npm dependencies for faster builds.
  4. **Install backend dependencies**: Uses Poetry to install Python packages.
  5. **Run migrations**: Applies Django migrations to the test database.
  6. **Run backend tests**: Executes Pytest (with pytest-django) for backend code.
  7. **Install frontend dependencies**: Installs npm packages.
  8. **Run frontend unit tests**: Runs Vitest for Vue components and logic.
  9. **Build frontend**: Runs the Vite build for production assets.
  10. **Run E2E tests**: Uses Playwright to test user flows and UI.
- **Environment:** Uses `.env.ci` for backend tests, ensuring test isolation and no secrets leakage.
- **Required Checks:** All tests (backend, frontend, E2E) must pass before merging to `main`.

### Parallelized Testing

To speed up feedback and reduce CI run times, backend and frontend tests are run in parallel where possible. This means:
- Backend (Pytest) and frontend (Vitest, Playwright) tests execute concurrently after their respective dependencies are installed.
- Parallelization leverages GitHub Actions' ability to run multiple jobs or steps at the same time, making the CI pipeline more efficient.
- This approach ensures that issues in one part of the stack do not block testing of the other, and developers get faster results on their pull requests.

**Tip:** The workflow is designed to catch integration issues early and ensure both backend and frontend are always deployable.

## Deployment Process

Production deployment is fully automated using the [`deploy_blog.sh`](../deploy_blog.sh) script. This script should be considered the canonical source for all production deployment steps.

**What the script does:**
- Ensures the correct user context for deployment.
- Pulls the latest code from the repository.
- Installs backend dependencies and runs Django migrations.
- Collects static files for Django.
- Installs frontend dependencies and builds the production frontend assets.
- Copies the built frontend to the appropriate directory for serving.
- Restarts the necessary backend and frontend services to apply changes.

For full details and the exact sequence of commands, see [`deploy_blog.sh`](../deploy_blog.sh).

> **Note:** All environment variables and secrets for production should be managed securely outside of version control, as referenced in the script and environment files.

## Production vs. Development

| Aspect                | Development (`.env.docker`) | CI (`.env.ci`) | Production (`.env`)         |
|-----------------------|-----------------------------|----------------|-----------------------------|
| **Debug**             | `True`                      | `False`        | `False`                     |
| **Database**          | Local/Postgres              | Test/Postgres  | Production/Postgres         |
| **Static files**      | Served by Django            | N/A            | Served by web server/CDN    |
| **Frontend**          | Dev server (`npm run dev`)  | Built & tested | Built, served as static     |
| **Secrets**           | Dummy/test values           | Dummy          | Real secrets (never commit) |
| **Allowed hosts**     | `localhost`, `127.0.0.1`    | `*`            | Production domain(s)        |

**Key differences:**
- **Production:**
  - Both the UI (frontend) and backend (Django) run as systemd units and are served behind an **nginx** reverse proxy for performance, security, and static asset handling.
  - Hot code reloading is disabled; only built, production-ready assets are served.
- **Development:**
  - Both services run with **hot code reloading** for rapid feedback and development convenience.
  - Managed via [`docker-compose.yaml`](../docker-compose.yaml), which orchestrates the Django backend, Vue frontend, and PostgreSQL database as containers.
  - Static files and frontend assets are served directly by the dev servers.

Environment files:
- `.env.docker`: Used for local dev with Docker Compose.
- `.env.ci`: Used in CI for isolated, non-secret testing.
- `.env`: Used for production (never commit this file). 