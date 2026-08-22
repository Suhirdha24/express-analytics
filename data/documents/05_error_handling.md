# FastAPI Documentation – Error Handling

Error handling in web APIs is critical to providing actionable feedback to clients. FastAPI simplifies error handling with `HTTPException` and custom exception handlers.

## Throwing HTTP Exceptions

To return HTTP error responses with status codes (e.g. 404 Not Found, 400 Bad Request, 403 Forbidden), raise `HTTPException`:

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

items = {"foo": "The Foo Item"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_id}' was not found in the inventory.",
            headers={"X-Error": "Item Missing"},
        )
    return {"item": items[item_id]}
```

Raising `HTTPException` immediately terminates execution and sends a structured JSON error response:

```json
{
  "detail": "Item 'bar' was not found in the inventory."
}
```

## Adding Custom Exception Handlers

You can define custom global exception handlers using `@app.exception_handler`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

app = FastAPI()

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something unexpected. There is a unicorn error!"},
    )

@app.get("/unicorns/{name}")
async def get_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn": name}
```

## Overriding Standard Request Validation Errors

When client request bodies or query parameters fail validation, FastAPI raises an internal `RequestValidationError`. You can override how validation errors are formatted:

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "invalid_payload", "errors": exc.errors()},
    )
```
