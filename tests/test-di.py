from attodi.core import ServiceCollection, ServiceProvider

class Person:
    def __init__(self, name:str):
        self.name = name

class ConcretePerson(Person):
    def __init__(self, name:str):
        super().__init__(f"{name}-from-concrete")

def buildit(name:str, name2:str) -> ConcretePerson:
    return ConcretePerson(f"{name},{name2}2")

sp = ServiceProvider(ServiceCollection()
                     .add_singleton(str, service="name")
                     .add_singleton(Person, ConcretePerson, buildit))

p:Person = sp.get_service(Person)
print(p.name)