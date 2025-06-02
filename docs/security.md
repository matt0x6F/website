# Security

## Secrets Management

Secrets and sensitive configuration (such as database credentials, Django secret key, and third-party API keys) are stored in **.env files**. These files are loaded and managed by [`api/core/config.py`](../api/core/config.py) and [`api/core/settings.py`](../api/core/settings.py), which use Pydantic and environment variable parsing to inject configuration into the application.

- **Never commit .env files to version control, except for those specifically used for testing (such as `.env.ci`).**
- Use `.env`, `.env.docker`, or `.env.ci` for local development, Docker, and CI environments, respectively.
- In production, secrets should be provided via a secure `.env` file or injected as environment variables by your deployment platform.
- The application will not start without required secrets (such as the Django secret key).

For more details, see the configuration logic in [`api/core/config.py`](../api/core/config.py) and [`api/core/settings.py`](../api/core/settings.py).

## Vulnerabilities

If you discover a security vulnerability in this project, please report it through GitHub's security advisory or issue tracker. Do not disclose security issues publicly until they have been reviewed and addressed by the maintainer.

## User Data

This project is a small, personal blog and does not currently have a formal GDPR compliance plan. User data is handled with care and is not shared with third parties. If the project grows or begins to process significant personal data from users in the EU or other regulated regions, GDPR and other privacy requirements will be reviewed and addressed as needed.

**Password Storage:**
- User passwords are **never stored or transmitted in plaintext**.
- The custom `User` model in [`api/accounts/models.py`](../api/accounts/models.py) inherits from Django's `AbstractUser`, which securely manages password storage.
- Passwords are stored in the database as salted, one-way hashes. By default, Django uses **PBKDF2 with SHA256** (configurable to use Argon2, bcrypt, or scrypt).
- Each password is hashed with a unique, per-user salt, making precomputed attacks (like rainbow tables) ineffective.
- Password verification uses Django's built-in authentication system, which performs constant-time comparison to prevent timing attacks.
- All password management (setting, changing, checking) is handled by Django's well-tested authentication framework.

If you have privacy concerns or questions about your data, please open an issue or contact the maintainer. 