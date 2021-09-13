# Overview

_respo_ states for **Resource Policy** and is tiny, user friendly tool for building RBAC systems based on single `yml` file, mainly with FastAPI framework in mind. In most cases – for even large set of roles and organizations – single file would be enough to provide restricting system access.

#### Note, every piece of code in the docs is a tested python/yml file, feel free to use it.

## 1. YML file with defined permissions, organizations and roles

```yaml
{!./examples/index/respo-example.yml!}
```

Note, this is very minimal showcase file, without (optional) **names** and **descriptions** fields for every object so it takes less space.

#### There are 4 sections:

- **metadata**, it will be automatically populated with things like `last_modify` datetime and `created_at` fields
- **permissions**, list of `permission "groups"` (only one – "user" above), where you specify all possible permission names in **resources** and custom rules (nested as you like) so stronger labels will force weaker
- **organizations**, list of predefined names and optionally – ensured permissions by default. You may choose to split such as "superadmins", "admins", "normal users", but also "company A", "company B" etc.
- **roles**, they belong strictly to one of organizations, with set of permissions. Not allowing one-to-many role to organization helps to avoid mistakes.

## 2. Parse YML file using respo CLI interface

Thanks to [Typer](https://typer.tiangolo.com/), _respo_ has powerful cli interface based on python annotations.

```sh
{!./examples/index/index002_cli.sh!}
```

And thats it, yml file got validated and pickled by default to `.respo_cache/__auto__respo_model.bin` file.

## 3. Using created respo model in dummy FastAPI app

```python
{!./examples/index/index001.py!}
```

#### Insights:

- Every endpoint has exactly and only exactly **ONE UNIQUE PERMISSION**
- Nested rules are resolved (note, no `user.read_basic` directly in foo role declaration from above, it was resolved by respo) so no need for complex if statements anywhere, any permission inheritance is done during build time using `respo create some_file`
- Every endpoint must have `organization` in path, so that different organizations are totally independent

<br>
<br>
<br>
<br>
