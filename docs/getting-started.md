# Getting Started

## Prerequisites

- **Docker** (recommended for all environments)
- **Docker Compose**
- **Node.js** (v18+)
- **npm** (v9+)
- **Python** (v3.11+, only if running backend outside Docker)
- **Poetry** (only if running backend outside Docker)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd blog
   ```
2. **Copy environment files:**
   ```sh
   cp .env.example .env
   cp api/.env.example api/.env
   cp ui/.env.example ui/.env
   # Edit these files as needed
   ```
3. **Install dependencies (if not using Docker):**
   - **Backend:**
     ```sh
     cd api
     poetry install
     ```
   - **Frontend:**
     ```sh
     cd ui
     npm install
     ```

## Running Locally

The recommended way is with Docker Compose:

```sh
task up
# or
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

## First-Time Setup

1. **Run database migrations:**
   ```sh
   task migrate
   # or
   docker compose exec django poetry run python manage.py migrate
   ```
2. **Create a superuser:**
   ```sh
   task create-super-user
   # or
   docker compose exec django poetry run python manage.py createsuperuser
   ```
3. **(Optional) Load fixtures:**
   ```sh
   task load-fixtures
   ```

You are now ready to start developing! See other docs for more details on workflows and conventions. 