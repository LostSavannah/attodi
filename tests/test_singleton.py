import pytest
from attodi.core import ServiceCollection, ServiceProvider

class Person:
    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age

class ConcretePerson(Person):
    def __init__(self, name:str, age:int):
        super().__init__(name, age)

def test_singleton_when_only_class_defined_builds_instance():
    services = ServiceCollection()
    person_name = "person"
    person_age = 28
    services.add_singleton(str, service=person_name)
    services.add_singleton(int, service=person_age)
    services.add_singleton(Person)
    servicesProvider = ServiceProvider(services)
    p = servicesProvider.get_service(Person)
    assert person_name == p.name
    assert person_age == p.age

def test_singleton_returns_same_instance_on_repeated_resolution():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_singleton(Person)
    provider = ServiceProvider(services)
    p1 = provider.get_service(Person)
    p2 = provider.get_service(Person)
    assert p1 is p2

def test_singleton_with_prebuilt_instance_returns_it_directly():
    services = ServiceCollection()
    person = Person("person", 28)
    services.add_singleton(Person, service=person)
    provider = ServiceProvider(services)
    resolved = provider.get_service(Person)
    assert resolved is person

def test_singleton_with_concrete_type_builds_concrete_instance():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_singleton(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    p = provider.get_service(Person)
    assert isinstance(p, ConcretePerson)
    assert p.name == "person"
    assert p.age == 28

def test_singleton_instances_not_shared_across_providers():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_singleton(Person)
    provider1 = ServiceProvider(services)
    provider2 = ServiceProvider(services)
    p1 = provider1.get_service(Person)
    p2 = provider2.get_service(Person)
    assert p1 is not p2

def test_get_optional_service_returns_none_when_not_registered():
    services = ServiceCollection()
    provider = ServiceProvider(services)
    assert provider.get_optional_service(Person) is None

def test_get_services_returns_all_matching_registrations():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(int, service=28)
    services.add_singleton(Person)
    services.add_singleton(Person, concrete=ConcretePerson)
    provider = ServiceProvider(services)
    results = list(provider.get_services(Person))
    assert len(results) == 2
    assert any(type(r) is Person for r in results)
    assert any(isinstance(r, ConcretePerson) for r in results)

def test_get_service_raises_exception_when_type_not_registered():
    services = ServiceCollection()
    provider = ServiceProvider(services)
    with pytest.raises(Exception):
        provider.get_service(Person)

def test_get_service_raises_exception_when_dependency_not_registered():
    services = ServiceCollection()
    services.add_singleton(str, service="person")
    services.add_singleton(Person)  # int (age) is never registered
    provider = ServiceProvider(services)
    with pytest.raises(Exception):
        provider.get_service(Person)
