# Glossary

**API**  
Application Programming Interface. In this project, refers to the HTTP endpoints provided by the Django backend (documented via OpenAPI).

**Backend**  
The server-side application, built with Django and Django Ninja, located in the `api/` directory.

**CI/CD**  
Continuous Integration / Continuous Deployment. Automated processes for testing and deploying code, managed via GitHub Actions.

**Docker Compose**  
A tool for defining and running multi-container Docker applications. Used for local development to orchestrate the backend, frontend, and database.

**E2E (End-to-End) Tests**  
Tests that simulate real user interactions across the full stack, implemented with Playwright in the `ui/e2e/` directory.

**Frontend**  
The client-side application, built with Vue 3, located in the `ui/` directory.

**Hot Code Reloading**  
A development feature where code changes are automatically reflected in the running app without restarting the server or refreshing the browser.

**OpenAPI**  
A specification for describing RESTful APIs. Used to auto-generate the TypeScript client for the frontend.

**Pinia**  
The state management library used in the Vue frontend.

**Playwright**  
A framework for end-to-end testing of web applications.

**Poetry**  
A Python dependency management tool used for the backend.

**PR (Pull Request)**  
A request to merge code changes into the main branch, subject to review and automated checks.

**SDK**  
Software Development Kit. In this project, refers to the auto-generated TypeScript API client in `ui/lib/api`.

**SSR (Server-Side Rendering)**  
Rendering Vue components on the server before sending HTML to the client, improving performance and SEO.

**Static Files**  
Assets like images, CSS, and JavaScript that are served directly to clients, often collected and served by Django or nginx.

**Systemd Unit**  
A service definition for systemd, used to manage backend and frontend processes in production.

**Taskfile**  
A YAML file (`Taskfile.yml`) defining common development and automation tasks. 