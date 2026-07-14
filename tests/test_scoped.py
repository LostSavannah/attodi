from attodi.core import ServiceCollection, ServiceProvider

class Person:
    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age

class ConcretePerson(Person):
    def __init__(self, name:str, age:int):
        super().__init__(name, age)

def _make_provider_with_scoped_person():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_scoped(Person)
    return ServiceProvider(services)

def test_scoped_when_only_class_defined_builds_instance():
    provider = _make_provider_with_scoped_person()
    p = provider.get_service(Person)
    assert p.name == "person"
    assert p.age == 28

def test_scoped_returns_same_instance_within_same_scope():
    provider = _make_provider_with_scoped_person()
    p1 = provider.get_service(Person)
    p2 = provider.get_service(Person)
    assert p1 is p2

def test_scoped_returns_different_instance_across_scopes():
    provider = _make_provider_with_scoped_person()
    scope1 = provider.create_scope()
    scope2 = provider.create_scope()
    p1 = scope1.get_service(Person)
    p2 = scope2.get_service(Person)
    assert p1 is not p2

def test_scoped_instances_not_shared_between_root_and_child_scope():
    provider = _make_provider_with_scoped_person()
    p_root = provider.get_service(Person)
    scope = provider.create_scope()
    p_scope = scope.get_service(Person)
    assert p_root is not p_scope

def test_scoped_with_concrete_type_builds_concrete_instance():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_scoped(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    p = provider.get_service(Person)
    assert isinstance(p, ConcretePerson)
    assert p.name == "person"
    assert p.age == 28

def test_get_optional_service_returns_none_when_not_registered():
    services = ServiceCollection()
    provider = ServiceProvider(services)
    assert provider.get_optional_service(Person) is None

def test_get_services_returns_all_matching_registrations():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_scoped(Person)
    services.add_scoped(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    results = list(provider.get_services(Person))
    assert len(results) == 2
    assert any(type(r) is Person for r in results)
    assert any(isinstance(r, ConcretePerson) for r in results)
