# Configuration - environment variables

You can set different values for paths of respo generated files using environment variables below. Note, `config` settings instance is created on import, you don't have to set env variables, but also

```python

from respo import config

config.RESPO_AUTO_FOLDER_NAME = "/opt/some_folder"

(...)
# other respo code after it

```

::: respo.settings
