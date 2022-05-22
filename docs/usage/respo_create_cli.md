# Respo create CLI

## CLI

Respo CLI command is based on [click](https://click.palletsprojects.com/) library. It is not included in module by default, you can install it using `pip install respo[cli]` or the best in development, `pip install respo[all]`.

We will use `respo_model.yml` file generated in provious section.

## Respo create

Ok, we already declared resource policies in `yml` file. There are few steps before we can use it in Python code, we must:

- read
- validate
- resolve complex rules and nested roles
- save

!!! note

    To get option preview, use `respo --help` and `respo create --help`

    You can also change default folder paths of generated files below, using environment variables.

Every part will be covered in another section, now let's use respo create command.

```bash
$ respo create respo_model.yml

INFO: Validating respo model from respo_model.yml...
INFO: Saved binary file to .respo_cache/__auto__respo_model.bin
INFO: Saved python file to respo_model.py
INFO: Processed in 0.0239s. Bin file size: 0.0013 mb.
INFO: Success!
```

Your folder structure after success should look like:

```bash
.
├── respo_model.yml
├── respo_model.py # new Python file
|
├── .respo_cache # read-only, processed model files
│   ├── __auto__respo_model.bin

```

Pickled, resolved input file was saved by default to `.respo_cache` folder. It should not be included in `.gitignore`. It allows better performence when reading policy, no need to validate and resolve input yml file every time on app startup and prevents developer mistake.

But there is also another file, `respo_model.py` with following content:

```python
{!./examples/usage/respo_model.py!}


```

This auto-generated file provides best autocompletion support possible in your Python code, note whole logic is wrapped in `typing.TYPE_CHECKING`, it will be understood by your IDE, but generates no additional overhead on the runtime.

<br>
<br>
<br>
