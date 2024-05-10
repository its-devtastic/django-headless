# Django Headless
Turn your [Django](https://www.djangoproject.com) app into a headless CMS

## Installation

```shell
pip install django-headless
```

```python
INSTALLED_APPS = [
    # ...other apps
    'headless',
    'headless.rest',
    'headless.user',
    'headless.admin',
    'headless.auth.api_token',
]
```