# Blog Project

This is the codebase for my personal website—a modern, full-stack blog platform featuring a Django-Ninja API backend and a Vue 3 + Vite frontend, containerized for easy local development.

---

## Project Structure

- **api/**: Django backend (Django-Ninja, Django-Ninja-Extra, JWT, PostgreSQL)
- **ui/**: Vue 3 frontend (Vite, TailwindCSS, PrimeVue)
- **docker-compose.yaml**: Orchestrates backend, frontend, and database for local development
- **Taskfile.yml**: Common development tasks (start, stop, migrate, build, etc.)

---

## Technologies

### Backend
- [Django](https://www.djangoproject.com/)
- [Django-Ninja](https://django-ninja.dev/)
- [Django-Ninja-Extra](https://eadwincode.github.io/django-ninja-extra/)
- [PostgreSQL](https://www.postgresql.org/)
- [Poetry](https://python-poetry.org/) for dependency management

### Frontend
- [Vue 3](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- [TailwindCSS](https://tailwindcss.com/)
- [PrimeVue](https://www.primefaces.org/primevue/)

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Task](https://taskfile.dev/) (optional, for easier workflow)
- [Poetry](https://python-poetry.org/) (for direct backend work)
- [Node.js](https://nodejs.org/) (for direct frontend work)

---

### Quick Start (Recommended)

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd blog
   ```

2. **Start the development environment**
   ```sh
   task up
   ```
   This will build and start all services (backend, frontend, database) using Docker Compose.

3. **Access the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)

4. **Stop the environment**
   ```sh
   task down
   ```

---

## Common Development Tasks

You can see all available development tasks and their descriptions by running:

```sh
task
```

This will display a list of commands for migrations, superuser creation, building, and more.

---

## Frontend Development

For direct frontend work (optional, outside Docker):

```sh
cd ui
npm install
npm run dev
```

- Unit tests: `npm run test:unit`
- E2E tests: `npm run test:e2e`
- Lint: `npm run lint`

---

## Backend Development

For direct backend work (optional, outside Docker):

```sh
cd api
poetry install
poetry run python manage.py runserver
```

- Run tests: `pytest`
- Export OpenAPI schema: `task export-schema`

---

## Configuration

To run the backend, you'll need a `.env` file in the `api/` directory (or project root, depending on your setup). By default, the project looks for a file named `.env`, but you can supply a file of any name by setting the `ENV_FILE` environment variable.

Here's a minimal example for local development:

```env
# .env (example)
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE__NAME=blog
DATABASE__USER=postgres
DATABASE__PASSWORD=postgres
DATABASE__HOST=localhost
DATABASE__PORT=5432

# S3 storage (optional, for media uploads)
S3__ACCESS_KEY_ID=your-access-key
S3__SECRET_ACCESS_KEY=your-secret-access-key
S3__BUCKET_NAME=your-bucket
S3__REGION=your-region
S3__ENDPOINT_URL=
S3__PREFIX=
S3__CDN_ENDPOINT=
```

- The S3 section is only needed if you want to use S3-compatible storage for media files.
- Adjust values as needed for your environment.
- See `docker-compose.yaml` for service configuration.
