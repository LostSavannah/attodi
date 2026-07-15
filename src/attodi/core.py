from enum import IntEnum
from typing import Any, Callable
from collections.abc import Iterator
from inspect import signature
from functools import wraps

def inject(**values):
    def decorator(func):
        current_signature = signature(func)
        original_parameter_names = [p.name for p in current_signature.parameters.values()]
        parameters = [p for p in current_signature.parameters.values()
                      if p.name not in values]
        
        new_signature = current_signature.replace(parameters=parameters)
        @wraps(func)
        def wrapper(*args, **kwargs):
            rargs = [*args]
            rargs.reverse()
            new_args = []
            new_kwargs = {}
            for parameter_name in original_parameter_names:
                injected_value = values.get(parameter_name, None)
                if len(rargs) > 0:
                    new_args.append(injected_value if parameter_name in values else rargs.pop())
                else:
                    new_kwargs[parameter_name] = injected_value if parameter_name in values else kwargs.get(parameter_name, None)
            return func(*new_args, **new_kwargs)
        wrapper.__signature__ = new_signature
        return wrapper
    return decorator

class ServiceLifetime(IntEnum):
    Singleton = 1
    Scoped = 2
    Transient = 3

class ServiceDefinition[T, TConcrete]:
    def __init__(self, 
                 cls:type[T], 
                 concrete:type[TConcrete]|None = None, 
                 lifetime:ServiceLifetime = ServiceLifetime.Singleton, 
                 service:T|Callable[[], T]|None = None):
        self.lifetime = lifetime
        self.cls = cls
        self.concrete = concrete
        self.service = service

class ServiceCollection:
    def __init__(self):
        self.services:list[ServiceDefinition] = []
    
    def add_singleton[T, TConcrete:T](self, cls:type[T], concrete:type[TConcrete]|None = None, service:T|None = None) -> "ServiceCollection":
        self.services.append(ServiceDefinition(cls, concrete, ServiceLifetime.Singleton, service))
        return self
    
    def add_scoped[T, TConcrete:T](self, cls:type[T], concrete:type[TConcrete]|None = None) -> "ServiceCollection":
        self.services.append(ServiceDefinition(cls, concrete, ServiceLifetime.Scoped, None))
        return self
    
    def add_transient[T, TConcrete:T](self, cls:type[T], concrete:type[TConcrete]|None = None) -> "ServiceCollection":
        self.services.append(ServiceDefinition(cls, concrete, ServiceLifetime.Transient, None))
        return self

class ServiceProvider:
    def __init__(self, services:ServiceCollection):
        self.services = services
        self.singleton_instances:dict[ServiceDefinition, Any] = {}
        self.scoped_instances:dict[ServiceDefinition, Any] = {}

    def create_scope(self) -> "ServiceProvider":
        new_scope = ServiceProvider(self.services)
        new_scope.singleton_instances = self.singleton_instances
        return new_scope

    def get_optional_service[T](self, cls:type[T]) -> T|None:
        return next(self.get_services(cls), None)

    def get_service[T](self, cls:type[T]) -> T:
        try:
            return next(self.get_services(cls))
        except StopIteration:
            raise Exception(f"No service registered for {cls!r}") from None

    def get_services[T](self, cls:type[T]) -> Iterator[T]:
        if issubclass(cls, ServiceProvider):
            yield self
            return
        definitions = [srv for srv in self.services.services 
                       if issubclass(srv.cls, cls) 
                       or (srv.concrete != None and issubclass(srv.concrete, cls))]
        for d in definitions:
            if d.lifetime == ServiceLifetime.Singleton:
                if isinstance(d.service, cls):
                    yield d.service
                    continue
                if d in self.singleton_instances:
                    yield self.singleton_instances[d]
                    continue
            elif d.lifetime == ServiceLifetime.Scoped:
                if d in self.scoped_instances:
                    yield self.scoped_instances[d]
                    continue 
            constructor = d.service if callable(d.service) else d.concrete if d.concrete else d.cls
            method = constructor if callable(d.service) else constructor.__init__
            arguments = list(signature(method).parameters.keys())
            annotations = {
                arg:method.__annotations__[arg]
                for arg in arguments if arg in method.__annotations__
            }
            arguments = {
                a:self.get_service(annotations[a]) for a in annotations
            }
            instance = constructor(**arguments)
            if d.lifetime == ServiceLifetime.Singleton:
                self.singleton_instances[d] = instance
            elif d.lifetime == ServiceLifetime.Scoped:
                self.scoped_instances[d] = instance
            yield instance

    def inject(self, func):
        ann = func.__annotations__
        services = {arg:self.get_optional_service(ann[arg]) for arg in ann}
        return inject(**{
            arg: services[arg] for arg in services if services[arg] != None
        })(func)
