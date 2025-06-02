# Reference

## Links to Key Files

- **Backend**
  - [`api/`](../api/) — Django backend source code
  - [`api/blog/models/`](../api/blog/models/) — Blog models
  - [`api/accounts/models/`](../api/accounts/models/) — User/account models
  - [`api/blog/api/`](../api/blog/api/) — API endpoint definitions
  - [`api/core/`](../api/core/) — Core utilities and base classes
  - [`api/blog/fixtures/`](../api/blog/fixtures/) — Example data for development/testing
  - [`api/blog/tests/`](../api/blog/tests/) — Backend tests

- **Frontend**
  - [`ui/`](../ui/) — Vue 3 frontend source code
  - [`ui/components/`](../ui/components/) — Vue components
  - [`ui/stores/`](../ui/stores/) — Pinia stores (state management)
  - [`ui/lib/api/`](../ui/lib/api/) — Auto-generated TypeScript API client
  - [`ui/services/MarkdownParser.ts`](../ui/services/MarkdownParser.ts) — Markdown parser
  - [`ui/components/MarkdownEditor.vue`](../ui/components/MarkdownEditor.vue) — Markdown editor component
  - [`ui/e2e/`](../ui/e2e/) — Playwright E2E tests

- **Configuration & Tooling**
  - [`docker-compose.yaml`](../docker-compose.yaml) — Local development orchestration
  - [`Taskfile.yml`](../Taskfile.yml) — Common development tasks
  - [`pyproject.toml`](../api/pyproject.toml) — Python/Poetry config
  - [`package.json`](../ui/package.json) — Frontend dependencies and scripts
  - [`deploy_blog.sh`](../deploy_blog.sh) — Production deployment script
  - [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — CI pipeline definition

---

## External Resources

- **Django**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Django Ninja**: [https://django-ninja.rest-framework.com/](https://django-ninja.rest-framework.com/)
- **Poetry**: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)
- **Vue 3**: [https://vuejs.org/](https://vuejs.org/)
- **Vite**: [https://vitejs.dev/](https://vitejs.dev/)
- **Pinia**: [https://pinia.vuejs.org/](https://pinia.vuejs.org/)
- **PrimeVue**: [https://primevue.org/](https://primevue.org/)
- **TailwindCSS**: [https://tailwindcss.com/](https://tailwindcss.com/)
- **Playwright**: [https://playwright.dev/](https://playwright.dev/)
- **Vitest**: [https://vitest.dev/](https://vitest.dev/)
- **OpenAPI**: [https://swagger.io/specification/](https://swagger.io/specification/)
- **Docker Compose**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- **GitHub Actions**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions) 