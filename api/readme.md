# API

The Python API for my blog.

## Configuration

Configuration makes use of django-configurations. It works mostly the same as normal configuration but has some niceties to it. Setting the appropriate environment variable is important when working with ASGI as it defaults to the development configuration.

## Developing

Everything runs in a container with Docker Compose, volumes are mounted and the development mode is enabled. Workflows like `task migrate` leverage the local Python environment provided by Poetry but will talk directly to the container. the `Local` configuration is important for that.

## Technologies

- [Django](https://github.com/django/django) ([Docs](https://docs.djangoproject.com/en/5.1/))
- [Django-Ninja](https://github.com/vitalik/django-ninja) ([Docs](https://django-ninja.dev))
- [Django-Ninja-Extras](https://github.com/eadwinCode/django-ninja-extra) ([Docs](https://eadwincode.github.io/django-ninja-extra/))