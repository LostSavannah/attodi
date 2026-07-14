# Attodi

[![Deploy Release](https://github.com/LostSavannah/attodi/actions/workflows/deploy.yaml/badge.svg)](https://github.com/LostSavannah/attodi/actions/workflows/deploy.yaml)

#### Minimalistic DI library for python

Attodi is a small dependency-injection container for Python. You register
types (and optionally concrete implementations or pre-built instances) on a
`ServiceCollection`, then resolve fully-constructed instances from a
`ServiceProvider`, which builds constructor arguments automatically from
type hints.

## Requirements

- Python >= 3.12

## Installation

```bash
pip install attodi
```

## Usage

```python
from attodi.core import ServiceCollection, ServiceProvider

class Greeter:
    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}!"

services = ServiceCollection()
services.add_singleton(str, service="World")
services.add_singleton(Greeter)

provider = ServiceProvider(services)
greeter = provider.get_service(Greeter)
print(greeter.greet())  # Hello, World!
```

`ServiceProvider` inspects the constructor of the class being resolved,
matches its parameter type hints against registered services, resolves them
recursively, and instantiates the class with the results.

### Service lifetimes

Register services with one of three lifetimes:

| Method | Lifetime | Behavior |
| --- | --- | --- |
| `add_singleton(cls, concrete=None, service=None)` | `Singleton` | One shared instance per `ServiceProvider` (or a pre-built `service` value). |
| `add_scoped(cls, concrete=None)` | `Scoped` | One shared instance per scope (see `create_scope`). |
| `add_transient(cls, concrete=None)` | `Transient` | A new instance every time it is resolved. |

```python
services = ServiceCollection()
services.add_scoped(Database)

provider = ServiceProvider(services)
scope = provider.create_scope()
db = scope.get_service(Database)
```

### Resolving multiple registrations

`get_service` returns the first matching registration; `get_services`
returns an iterator over every registration that matches a type (including
subclasses).

```python
for service in provider.get_services(Person):
    ...
```

## Development

```bash
pip install -e .
pip install -r requirements.txt
python -m pytest
```

## License

GPL-3.0
