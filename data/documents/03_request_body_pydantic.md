# FastAPI Documentation – Request Body and Pydantic Models

When sending data from a client (e.g. frontend app or HTTP client) to your API, you send it as a **Request Body**. FastAPI uses **Pydantic** models to define, validate, and document JSON request bodies.

## Creating Pydantic Data Models

To declare a request body, define a model class inheriting from `pydantic.BaseModel`:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, max_length=300)
    price: float = Field(gt=0, description="Price must be strictly greater than zero")
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
```

When receiving a POST request at `/items/`, FastAPI will:
1. Read the JSON body from the request.
2. Convert and validate the data against `Item` types (returning automatic 422 errors for invalid fields).
3. Pass the validated `item` model instance to the endpoint function.
4. Generate JSON Schema for OpenAPI interactive documentation (`/docs`).

## Nested Pydantic Models

Pydantic models can be deeply nested to handle complex hierarchical JSON payload structures:

```python
from pydantic import BaseModel, HttpUrl

class Image(BaseModel):
    url: HttpUrl
    name: str

class ItemWithImages(BaseModel):
    name: str
    description: str | None = None
    price: float
    tags: list[str] = []
    images: list[Image] | None = None
```

## Mixing Path Parameters, Query Parameters, and Request Bodies

FastAPI automatically distinguishes between parameters:
- If a parameter is declared in the path template -> **Path Parameter**.
- If a parameter is a singular type (`int`, `str`, `bool`) -> **Query Parameter**.
- If a parameter is annotated as a `BaseModel` -> **Request Body**.

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    return {"item_id": item_id, "item": item, "q": q}
```
