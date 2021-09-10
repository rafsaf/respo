# Overview

_respo_ states for **Resource Policy** and is tiny, user friendly tool for building RBAC systems based on single yml file, mainly with FastAPI framework in mind.

```python
{!./examples/index/index001.py!}
```

I wanted to have simple RBAC in backend app but couldn't find any solution which satisfied me - i had just fiew concepts in mind:

- **separation of organizations** (If "A" is superuser in _foo_ organization, it has no access to _bar_ organization at all)
- **permissions inheritance** (It may lead to thousands of `if` statements all over the codebase, i wanted every endpoint with only ONE permission for it (and the logic do the rest))
- **simplicity** Which means predefined file-based RBAC - it's not for every usecase, only when have predefined number of organization in app, where adding new roles, permissions and organization manually
- **speed** Parsing yml file, validate it and then pickle - so it can be read instantly

_respo_ validate input yml or json file, resolve all inheritance problems, **pickle** generated pydantic model to binary file and provide function to read from it.

## Example yml file

```yaml
{!./examples/index/respo-example.yml!}
```

## Parse yml files

Thanks to **Typer**, _respo_ has powerful cli interface based on python annotations.

```sh
respo --help  # prints all available commands

respo create --yml-file respo-example.yml  # create model from file

```

And thats it!
Yml file got validated and compiled to binary format, by default in `__auto__respo_model.bin` file.
You can now
<br>
<br>
<br>
<br>
