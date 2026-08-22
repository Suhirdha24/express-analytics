# FastAPI Documentation – Path and Query Parameters

FastAPI makes handling path parameters and query parameters intuitive, type-safe, and self-documenting via OpenAPI standards.

## Path Parameters

Path parameters are part of the URL path and are declared using Python format string syntax.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

FastAPI automatically parses `item_id` to an integer, validates the data type, and returns an HTTP 422 Unprocessable Entity error if conversion fails (e.g. if `/items/foo` is requested).

### Path Precedence

Because path operations are evaluated sequentially, specific routes must be declared before dynamic path parameter routes:

```python
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "current_user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

If `/users/me` were placed after `/users/{user_id}`, FastAPI would interpret `"me"` as the `user_id` string parameter.

## Query Parameters

Function parameters that are not part of the URL path template are automatically recognized as Query Parameters.

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10, q: str | None = None):
    return {"skip": skip, "limit": limit, "q": q}
```

- Default values make query parameters optional (`skip=0`, `limit=10`).
- Setting a parameter to `None` makes it an optional query parameter (`q: str | None = None`).
- Omission of default values makes the query parameter required.

## Combining Path and Query Parameters

You can declare both path parameters and query parameters simultaneously in the same route handler:

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Full item description goes here."})
    return item
```

FastAPI handles string-to-boolean conversions automatically (`short=1`, `short=true`, `short=on` all convert to `True`).
