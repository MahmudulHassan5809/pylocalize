# pylocalize

A flexible localization package for FastAPI that supports both static and dynamic field translations. Easily localize your application’s response data based on predefined static translations or dynamic database fields.

---

## Features

- **Static Localization:** Translate static fields in your response based on predefined translation data (from a JSON file).
- **Dynamic Localization:** Automatically localize dynamic database fields (e.g., `field`, `field_es`).
- **Integration with FastAPI:** Simple decorators to localize response data in FastAPI routes.

---

## Installation

You can install `pylocalize` using pip:

```bash
pip install pylocalize
```

---

## Usage

### Step 1: Prepare your static translation data

Create a `static_data.json` file with translations in the following format:

```json
{
    "greeting": {
        "en": "Hello",
        "es": "Hola"
    },
    "test": {
        "en": "Test",
        "es": "Prueba"
    }
}
```

### Step 2: Integrate localization into your FastAPI app

Import the necessary classes and decorators from `pylocalize` and set up your `FastAPI` routes.

---

### Example

Below is an example of how to use the `LocalizeManager` and the decorators `localize_static_response` and `localize_database_response` for both static and dynamic translations.

```python
from typing import Any, Generator
import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from pylocalize import (
    LocalizeManager,
    localize_static_response,
    localize_database_response,
)

DATABASE = "example.db"

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

app = FastAPI()

# Initialize LocalizeManager with your static translations JSON
localizer = LocalizeManager(static_data_path="static/static_data.json")

# Static localization route
@app.get("/static")
@localize_static_response(default_prefix="en", desired_prefix="es", fields=["message"])
async def get_static_response(
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> Any:
    data = {
        "message": "{greeting} Mark {test}",
        "example_with_only_string": localizer.translate("{greeting} Mark", "es"),
    }
    return data

# Static localization for a list
@app.get("/static/list")
@localize_static_response(default_prefix="en", desired_prefix="es", fields=["message"])
async def get_static_response_list(
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> Any:
    data = [
        {
            "message": "{greeting} Mark {test}",
            "example_with_only_string": localizer.translate("{greeting} Mark", "es"),
        }
    ]
    return data

# Database dynamic localization route
@app.get("/users")
@localize_database_response(default_prefix="en", desired_prefix="es", fields=["field"])
async def get_users(
    conn: sqlite3.Connection = Depends(get_db),
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> list[Any]:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, field, field_es FROM users")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

# Dynamic localization for a single user
@app.get("/users/{user_id}")
@localize_database_response(default_prefix="en", desired_prefix="es", fields=["field"])
async def get_user_details(
    user_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> Any:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, field, field_es FROM users WHERE id = ?", (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(zip([column[0] for column in cursor.description], row))
```

### Step 3: Use in Your FastAPI Routes

- **Static Localization:** Decorate your route with `@localize_static_response` to automatically translate the specified fields (`message` in this case) based on the provided language prefixes.
- **Dynamic Localization:** Decorate your route with `@localize_database_response` to translate dynamic fields (e.g., `field`, `field_es`) fetched from the database.

---

## Decorators

### `localize_static_response`

Decorates FastAPI routes to localize static fields.

**Parameters:**
- `default_prefix`: The default language prefix (e.g., `"en"`).
- `desired_prefix`: The language you want to translate to (e.g., `"es"`).
- `fields`: A list of fields in the response that should be localized.

### `localize_database_response`

Decorates FastAPI routes to localize dynamic database fields.

**Parameters:**
- `default_prefix`: The default language prefix (e.g., `"en"`).
- `desired_prefix`: The language you want to translate to (e.g., `"es"`).
- `fields`: A list of dynamic fields in the response that should be localized.

---

## How It Works

1. **Static Localization:** The `LocalizeManager` class loads translations from a JSON file and provides a `translate` method for localizing placeholders within string values.
2. **Dynamic Localization:** When retrieving records from the database, the `localize_database_response` decorator translates fields dynamically (e.g., `field`, `field_es`) based on the language prefixes.

---

## Contributing

We welcome contributions to `pylocalize`. If you'd like to help improve the package, please fork the repository and submit a pull request.

---

## License

`pylocalize` is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

---

This README provides an easy-to-follow guide for integrating your localization package into FastAPI applications, ensuring users can quickly get started.
