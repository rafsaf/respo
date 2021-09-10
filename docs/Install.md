# Install

Installation is as simple as:

```
pip install pydantic
```

You can also customize some default settings using environment variables

```py
RESPO_BINARY_FILE_NAME=".respo_cache/__auto__respo_model.bin"
# Name of file where pickled model will be saved

RESPO_DEFAULT_EXPORT_FILE="__auto__respo_model"
# default name of exported model as a fiel after exporting

RESPO_CHECK_FORCE=false
# if True, no validation of "Client" will when using respo.check
```