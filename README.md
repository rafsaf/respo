<a href="https://codecov.io/gh/rafsaf/respo" target="_blank">
  <img src="https://img.shields.io/codecov/c/github/rafsaf/respo" alt="Coverage">
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

# Overview

_respo_ states for resource policy and is tiny, user friendly tool for building RBAC systems based on static `yml` file, mainly with FastAPI framework in mind. In most cases – for even large set of roles – single file would be enough to provide restricting system access.

Features:

- It provides custom fields for **SQLAlchemy** and **Django** to store users roles in database.

- Implements R. Sandhu Role-based access control [text](https://profsandhu.com/articles/advcom/adv_comp_rbac.pdf).

- Dead simple, fast and can be trusted – 100% coverage.

- **No issues** with mutlithreading and multiprocessing – you just pass around already prepared, compiled respo_model (from file) in your app that is **readonly**.

- Generates your roles, permissions offline and compile it to pickle file for superfast access in app.

- Detailed documentation and very detailed error messages in CLI command.

- 100% autocompletion and typing support with optional code generation for even better typing support.

# Documentation

**https://rafsaf.github.io/respo/**
