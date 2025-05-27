# confng-py

A simple configuration management tool for python.
You can use it to manage your python application's configuration in a simple and flexible way.

### Install

```
pip install confng-py
```

### Usage

```python
from confng import Conf

# create a new Conf instance with a config object and MergeEnvOptions
# If you don't want to merge environment variables, you can omit the merge_env_options option.
# The value of `config` is JSON. You can parse it from json/toml/yaml/... file, or directly pass an object.
# The logic should be implemented in your own code.
conf = Conf(
    ConfOptions(
        config={
            "name": "foo",
            "server": {
                "port": 3000,
                "host": "localhost",
            },
            "logs": [
                {
                    "level": "info",
                    "output": "console",
                },
            ],
            "nums": [1, 2, 3],
        },
        merge_env_options=MergeEnvOptions(prefix="FOO", separator="__"),
    )
)

print(conf.get('name')); # foo
print(conf.get('server.port')); # 3000
print(conf.get('server.host')); # localhost

# The inner of Conf will guess the type of the value automatically from the initial config object.
# So the inital config object should be in full form, and the value of each key should be in the correct type.

# if the following environment variables setted 
# FOO__SERVER__PORT=4000 
# FOO__SERVER__HOST=example.com
print(conf.get('server.port')); # here will return 4000 and the data type is number.
print(conf.get('server.host')); # example.com
```

### Load config from file

```python
import os
import json

from confng import Conf

# read config from conifg/default.json
config_path = os.path.join('config', 'default.json')
with open(config_path, 'r') as f:
    config = json.load(f)

conf = Conf(ConfOptions(config=config))

print(conf.get('name'));
```

### Thanks

This package is inspired by the following packages:

- [config of Node.js](https://www.npmjs.com/package/config)
- [config of rust](https://crates.io/crates/config)