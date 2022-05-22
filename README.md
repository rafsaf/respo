<a href="https://codecov.io/gh/rafsaf/respo" target="_blank">
  <img src="https://img.shields.io/codecov/c/github/rafsaf/respo" alt="Coverage">
</a>

<a href="https://github.com/psf/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-lightgrey" alt="Black">
</a>

<a href="https://github.com/rafsaf/respo/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/rafsaf/respo/workflows/Test/badge.svg" alt="Test">
</a>

<a href="https://github.com/rafsaf/respo/actions?query=workflow%3APublish" target="_blank">
  <img src="https://github.com/rafsaf/respo/workflows/Publish/badge.svg" alt="Publish">
</a>

<a href="https://github.com/rafsaf/respo/actions?query=workflow%3AGh-Pages" target="_blank">
  <img src="https://github.com/rafsaf/respo/workflows/Gh-Pages/badge.svg" alt="Gh-Pages">
</a>

<a href="https://github.com/rafsaf/respo/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/rafsaf/respo" alt="License">
</a>

<a href="https://pypi.org/project/respo/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/respo" alt="Python version">
</a>

## Documentation

**https://rafsaf.github.io/respo/**

## Installation

```
pip install respo[all]
```

## Introduction

_respo_ states for resource policy and is tiny, user friendly tool for building RBAC systems based on static `yml` file, mainly with FastAPI framework in mind. In most cases – for even large set of roles – single file would be enough to provide restricting system access.

Features:

- It provides custom fields for **SQLAlchemy** and **Django** to store users roles in database.

- Implements R. Sandhu Role-based access control [text](https://profsandhu.com/articles/advcom/adv_comp_rbac.pdf).

- Dead simple, fast and can be trusted – 100% coverage.

- **No issues** with mutlithreading and multiprocessing – you just pass around already prepared, compiled respo_model (from file) in your app that is **readonly**.

- Generates your roles, permissions offline and compile it to pickle file for superfast access in an app.

- Detailed documentation and error messages in CLI command.

- 100% autocompletion and typing support with optional code generation for even better typing support.

---

_Note, every piece of code in the docs is a tested python/yml file, feel free to use it._

## Usage in FastAPI

The goal is to use simple and reusable dependency factory `user_have_permission("some permission")` that will verify just having `User` database instance if user have access to resoruce. Single endpoint must have single permission for it, and thanks to respo compilation step, every "stronger" permissions and roles would include "weaker" so **we don't need to have the if statements everywhere around application**.

```python
from .dependencies import user_have_permission

...


@router.get("/users/read_all/")
def users_read_all(user = Depends(user_have_permission("users.read_all"))):
    return user

```
