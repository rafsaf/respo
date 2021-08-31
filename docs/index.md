# Overview

_respo_ states for **Resource Policy** and is tiny, framework-agnostic, user friendly tool for building RBAC systems based on single yml or json file.

It was designed to provide simple black-box like api with minimum of boilerplate

```python
{!./examples/index/index001.py!}
```

There are fiew main concerns when switching from `is_admin`, `is_superuser` flags to complex authorization system:

- **permissions inheritance** (which may lead to thousands of `if` statements all over the codebase)
- **extensibility** (how hard is to add new role, organization, permission)
- **resistance** (will you trust the output without writing hundreds of tests)

_respo_ validate input yml or json file, resolve all inheritance problems, **pickle** generated pydantic model to binary file and provide function to read from it.

## Example yml file

```yaml
{!./examples/index/respo-tutorial.yml!}
```

## Parse yml files

Thanks to **Typer**, _respo_ has powerful cli interface based on python annotations.

```bash
respo --help  # prints all available commands

respo create --yml-file respo-tutorial.yml

# Processing respo-tutorial.yml
# Success!
```

And thats it!
Yml file got validated and compiled to binary format, by default in `__auto__respo_model.bin` file.

## Read and check permissions

```python
{!./examples/index/index002.py!}
```

And this is when magic happens: We didn't explicite gave neither role `user` nor `default` organization permission to `user.read_basic`, but during creation of binary form of yml file, it was understood by _respo_. Only by specifying single permission rule.

<br>
<br>
<br>
<br>
