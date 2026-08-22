# FastAPI Documentation – Background Tasks

FastAPI provides a simple mechanism to define tasks that should be run **after** returning an HTTP response. This is useful for operations that take noticeable time to execute but don't require the client to wait for completion (e.g. sending email notifications, processing analytical logs, or writing audit records).

## Defining Background Tasks

To use background tasks, import `BackgroundTasks` from `fastapi` and declare it as a parameter in your path operation function:

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def write_notification(email: str, message: str = ""):
    with open("log.txt", mode="a") as email_file:
        content = f"notification for {email}: {message}\n"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Welcome to DocuMind!")
    return {"message": "Notification scheduled in background"}
```

In this example:
1. `background_tasks.add_task(...)` accepts the target function (`write_notification`) and positional arguments (`email`, `message`).
2. FastAPI returns `{"message": "Notification scheduled in background"}` immediately to the client.
3. FastAPI executes `write_notification` asynchronously after sending the HTTP response.

## Background Tasks with Dependency Injection

You can also inject `BackgroundTasks` inside sub-dependencies. FastAPI handles sharing the background tasks object across dependencies:

```python
from fastapi import Depends, FastAPI, BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message + "\n")

def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"Found query: {q}"
        background_tasks.add_task(write_log, message)
    return q

@app.post("/send-log/")
async def send_log(query_str: str = Depends(get_query)):
    return {"status": "Logged successfully"}
```

## Caveats and Celery Comparison

FastAPI's built-in `BackgroundTasks` executes within the same process event loop.
- **Use `BackgroundTasks` for**: Small tasks (email sending, simple file appends, quick database updates).
- **Use Celery / RabbitMQ / Redis for**: Heavy compute workloads, long-running data processing pipelines, or distributed queue processing requiring task persistence and worker horizontal scaling.
