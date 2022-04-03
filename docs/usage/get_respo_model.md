# Get respo model

## Load generated model in Python code

In previous section, we created `.respo_cache` folder and `respo_model.py` file for better autocompletion.
We assume your folder structure of your app look like that:

```bash
.
├── respo_model.yml
├── respo_model.py
|
├── .respo_cache
│   ├── __auto__respo_model.bin
│   └── __auto__respo_model.yml
|
├── main.py
|
...

```

`main.py` is a standard name for file with FastAPI app logic.

To load your respo model in the app and pass it around, use following code:

```python
{!./examples/usage/main.py!}

```

<br>
<br>
<br>
