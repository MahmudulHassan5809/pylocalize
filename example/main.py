# main.py
from typing import Any
from fastapi import FastAPI, Depends
from pylocalize import LocalizeManager, localize_static_response

app = FastAPI()

localizer = LocalizeManager(static_data_path="static/static_data.json")


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
