Here’s a `README.md` file focusing on the static localization functionality of your project:

```markdown
# Static Localization with `LocalizeManager`

This project provides a mechanism for localizing static fields in a given data set. The `LocalizeManager` handles the translation of placeholders in strings, which are defined in static translation files. This is particularly useful for translating content like UI strings, messages, and labels in different languages.

## Features

- **Static Field Translation**: Translate specific fields in an object or list based on predefined static translations.
- **Customizable Language Prefixes**: Allows the use of different language prefixes for the translations (e.g., `en` for English, `es` for Spanish).
- **Supports JSON Files**: The static translation data can be loaded from a JSON file for easy management.

## Setup

### 1. Install the Required Libraries

If you haven't already, make sure to install the necessary dependencies for your project. This includes FastAPI and any other relevant dependencies:

```bash
pip install fastapi
```

### 2. Prepare the Static Translation Data

Static translation data should be in the form of a JSON file, where each key is a placeholder and each value is a dictionary containing translations for different languages.

Example of `static_data.json`:

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

### 3. Initialize the `LocalizeManager`

The `LocalizeManager` is responsible for loading the static data and providing translation methods. It is initialized with the path to the JSON file that contains the translations.

```python
from pylocalize import LocalizeManager

localizer = LocalizeManager(static_data_path="static/static_data.json")
```

### 4. Using `localize_static_response` Decorator

The decorator `localize_static_response` applies static translations to the response fields of your FastAPI endpoints. It accepts the following parameters:
- `default_prefix`: The default language prefix (e.g., `"en"`).
- `desired_prefix`: The desired language prefix (e.g., `"es"`).
- `fields`: A list of fields to be localized.

#### Example Usage in FastAPI

Here is an example FastAPI endpoint using the `localize_static_response` decorator to localize static fields:

```python
from fastapi import FastAPI, Depends
from pylocalize import LocalizeManager, localize_static_response

app = FastAPI()

localizer = LocalizeManager(static_data_path="static/static_data.json")

@app.get("/static")
@localize_static_response(default_prefix="en", desired_prefix="es", fields=["message"])
async def get_static_response(
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> dict:
    data = {
        "message": "{greeting} Mark {test}",
        "example_with_only_string": localizer.translate("{greeting} Mark", "es"),
    }
    return data
```

In this example, the field `message` is localized for both English (`en`) and Spanish (`es`) based on the static translation data.

### 5. Output Example

For the request to `/static`, the translated response might look like:

```json
{
  "message_en": "Hello Mark Test",
  "message_es": "Hola Mark Prueba",
  "example_with_only_string": "Hola Mark"
}
```

### 6. Localize Lists of Dictionaries

The `localize_static_response` decorator can also be applied to list responses, where each item in the list is a dictionary. Static translations are applied to the specified fields in each dictionary within the list.

Example for list response:

```python
@app.get("/static/list")
@localize_static_response(default_prefix="en", desired_prefix="es", fields=["message"])
async def get_static_response_list(
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> list:
    data = [
        {
            "message": "{greeting} Mark {test}",
            "example_with_only_string": localizer.translate("{greeting} Mark", "es"),
        }
    ]
    return data
```

The response will contain the localized fields for each item in the list, similar to the example above.

## Notes

- The static translation data file (`static_data.json`) should be structured properly to include all necessary translations.
- You can extend the `LocalizeManager` to handle more complex use cases, such as nested translations or integrating with external translation services.

## Contributing

Feel free to contribute by adding new features, improving documentation, or fixing bugs. Please fork the repository and submit pull requests for any changes.
