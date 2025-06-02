# Troubleshooting & FAQ

## Common Issues

- **Playwright tests in VSCode conflict with `npm run dev`**
  - Sometimes, running Playwright tests inside VSCode can be at odds with the development server (`npm run dev`). This may cause tests to fail or behave unexpectedly.
  - **Solution:** Run `npm run build` to generate a fresh production build of the frontend, then restart your development environment. This usually resolves the issue.

*List other common problems and their solutions (e.g., Docker not starting, migrations failing).* 

## Debugging Tips

- **Browser Console:**
  - Use your browser's developer tools (usually F12 or right-click → Inspect) to view console output, network requests, and errors from the frontend. The app is designed to provide clear error messages and warnings in the console.

- **UI Container Logs:**
  - To view logs from the frontend (UI) container, run:
    ```sh
    docker compose logs ui
    ```
  - These logs include build output, runtime errors, and server-side rendering (SSR) issues.

- **Backend Container Logs:**
  - To view logs from the backend (Django) container, run:
    ```sh
    docker compose logs django
    ```
  - These logs include API errors, stack traces, and structured logs from `structlog`.

All of these logging sources are optimized for debugging and should provide actionable information when issues arise.

*How to access logs, use verbose modes, and useful commands.* 