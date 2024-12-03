# pylint: skip-file

import sqlite3
from collections.abc import Generator
from typing import Any

from fastapi import Depends, FastAPI, HTTPException

from pylocalize import (
    LocalizeManager,
    localize_database_response,
    localize_static_response,
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


@app.get("/users")
@localize_database_response(default_prefix="en", desired_prefix="es", fields=["field"])
async def get_users(
    conn: sqlite3.Connection = Depends(get_db),
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> list[Any]:
    """
    Fetch users from the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, field, field_es FROM users")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@app.get("/users/{user_id}")
@localize_database_response(default_prefix="en", desired_prefix="es", fields=["field"])
async def get_user_details(
    user_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    localizer: LocalizeManager = Depends(lambda: localizer),
) -> Any:
    """
    Fetch a user from the database by ID.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, field, field_es FROM users WHERE id = ?", (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(zip([column[0] for column in cursor.description], row))
