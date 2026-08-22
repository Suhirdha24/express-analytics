# FastAPI Documentation – Dependency Injection

In software engineering, **Dependency Injection** is a design pattern where a function or object receives other objects or functions that it depends on, rather than creating them internally. FastAPI features an extremely powerful yet simple Dependency Injection system.

## Key Concepts

FastAPI's dependency injection system allows developers to:
- Share common logic across multiple route handlers (e.g. database sessions, authentication, security).
- Enforce security and permissions dynamically.
- Minimize code duplication across API endpoints.
- Easily write unit tests by overriding dependencies.

## Using `Depends`

To inject a dependency, import `Depends` from `fastapi` and declare it in your route path operation function.

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

When a request arrives at `/items/`, FastAPI will automatically:
1. Extract parameters matching `common_parameters` (such as `q`, `skip`, `limit`) from the incoming request.
2. Execute `common_parameters`.
3. Pass the return value as the `commons` argument to `read_items`.

## Class-based Dependencies

Dependencies can also be classes instead of functions. FastAPI automatically instantiates the class:

```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/users/")
async def read_users(commons: CommonQueryParams = Depends()):
    return {"q": commons.q, "skip": commons.skip, "limit": commons.limit}
```

Notice that writing `Depends()` without arguments inside `commons: CommonQueryParams = Depends()` tells FastAPI to infer the dependency class directly from the type annotation.

## Sub-dependencies

Dependencies can depend on other dependencies, forming a dependency graph. FastAPI resolves sub-dependencies recursively in the correct order.

```python
def query_extractor(q: str | None = None):
    return q

def query_checker(q: str = Depends(query_extractor)):
    if not q:
        return "No query provided"
    return f"Query: {q}"

@app.get("/search/")
async def search(query_res: str = Depends(query_checker)):
    return {"result": query_res}
```

## Overriding Dependencies in Testing

During testing with `TestClient`, you can override any dependency using `app.dependency_overrides`:

```python
def mock_db():
    return "Mock Database Session"

app.dependency_overrides[get_db] = mock_db
```
