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