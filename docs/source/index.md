# Welcome to bc-configs's documentation!

*Let's make your configuration easy.*

## Introduction

`bc-configs` is a library that makes configuring your applications easier.

## Installation

To install, use pip:

```bash
pip install bc-configs
```

## Make your custom config class

You can create your custom config class by inheriting from `BaseConfig`:

```python
import os
from bc_configs import BaseConfig, define

define()

class MyConfig(BaseConfig):
    some_int: int
    some_string: str
    some_bool: bool

my_config = MyConfig()  # type: ignore[call-arg]

assert int(os.getenv("MY_SOME_INT")) == my_config.some_int  # True
assert os.getenv("MY_SOME_STRING") == my_config.some_string  # True
assert bool(os.getenv("MY_SOME_BOOL")) == my_config.some_bool  # True
```

The name of the environment variable is formed based on the names of the class and field.

## Features

- Load environment variables from `.env` files (using `python-dotenv`).
- Load environment variables from YAML files (e.g., `.env.yml` or custom path via `YAML_CONFIG_FILE` environment variable).
- Load secrets from HashiCorp Vault (using `hvac`).

## Error handling

When a required configuration field is missing, the library raises a `ValidationError` with an enriched error message that includes the environment variable name:

```
ValidationError: 1 validation error for MyConfig
some_int
  Field required  →  env var: 'MY_SOME_INT' [type=missing, input_value={}, input_type=dict]
```

If the field has a description, it will be included in the error message:

```python
class MyConfig(BaseConfig):
    some_int: int = Field(description="Database port number")
```

Error message:

```
ValidationError: 1 validation error for MyConfig
some_int
  Field required  →  env var: 'MY_SOME_INT' [type=missing, input_value={}, input_type=dict]
```

```{toctree}
:maxdepth: 2
:caption: Contents:

bc_configs.md
for_contributing.md
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
