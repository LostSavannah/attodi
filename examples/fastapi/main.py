import uvicorn
from fastapi import FastAPI
from attodi.core import ServiceCollection, ServiceProvider

class Dependency:
    def __init__(self):
        self.usage:int = 0

    def use(self, message: str) -> int:
        self.usage += 1
        print(message)
        return self.usage

app = FastAPI()
sp = ServiceProvider(ServiceCollection().add_singleton(Dependency))

@app.get("/test/injection")
@sp.inject
def test_injection(dep:Dependency):
    return {
        "Usage": dep.use("Message")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4554)