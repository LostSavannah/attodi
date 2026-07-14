from attodi.core import ServiceCollection, ServiceProvider

class Person:
    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age

class ConcretePerson(Person):
    def __init__(self, name:str, age:int):
        super().__init__(name, age)

class Counter:
    _next_value = 0
    def __init__(self):
        Counter._next_value += 1
        self.value = Counter._next_value

class Wrapper:
    def __init__(self, counter:Counter):
        self.counter = counter

def _make_provider_with_transient_person():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_transient(Person)
    return ServiceProvider(services)

def test_transient_when_only_class_defined_builds_instance():
    provider = _make_provider_with_transient_person()
    p = provider.get_service(Person)
    assert p.name == "person"
    assert p.age == 28

def test_transient_returns_new_instance_on_each_resolution():
    provider = _make_provider_with_transient_person()
    p1 = provider.get_service(Person)
    p2 = provider.get_service(Person)
    assert p1 is not p2
    assert p1.name == p2.name
    assert p1.age == p2.age

def test_transient_with_concrete_type_builds_concrete_instance():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_transient(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    p = provider.get_service(Person)
    assert isinstance(p, ConcretePerson)
    assert p.name == "person"
    assert p.age == 28

def test_transient_reuses_singleton_dependency_across_instances():
    services = ServiceCollection()
    services.add_singleton(Counter)
    services.add_transient(Wrapper)
    provider = ServiceProvider(services)
    w1 = provider.get_service(Wrapper)
    w2 = provider.get_service(Wrapper)
    assert w1 is not w2
    assert w1.counter is w2.counter

def test_get_optional_service_returns_none_when_not_registered():
    services = ServiceCollection()
    provider = ServiceProvider(services)
    assert provider.get_optional_service(Person) is None

def test_get_services_returns_all_matching_registrations():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_transient(Person)
    services.add_transient(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    results = list(provider.get_services(Person))
    assert len(results) == 2
    assert any(type(r) is Person for r in results)
    assert any(isinstance(r, ConcretePerson) for r in results)
