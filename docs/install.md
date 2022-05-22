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
pip install respo[cli]   # with PyYAML and click

pip install respo[sqlalchemy]   # with sqlalchemy

pip install respo[django]   # with django
```

<br>
<br>
<br>
