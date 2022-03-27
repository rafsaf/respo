# Install

For development purposes you'd better install **all** CLI and fields dependencies.

```bash
pip install respo[all]
```

Minimalistic module can be installed (Note you won't be able to use CLI commands, but this will be good for production usage where respo CLI commands are useles):

```bash
pip install respo
```

And there are also some other options:

```bash
pip install respo[cli]   # with modules for only CLI usage

pip install respo[sqlalchemy]   # with modules for sqlalchemy field usage

pip install respo[django]   # with modules for django field usage
```

<br>
<br>
<br>
