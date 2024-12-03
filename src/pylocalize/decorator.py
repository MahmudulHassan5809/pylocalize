from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from .localize_manager import LocalizeManager


def localize_static_response(
    default_prefix: str, desired_prefix: str, fields: list[str] | None = None
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    Functional decorator to localize static response fields.

    :param default_prefix: The default language prefix (e.g., "en").
    :param desired_prefix: The desired language prefix (e.g., "es").
    :param fields: Specify the list of static fields to localize.
    :return: A wrapped async function that applies static localization to its response.
    """

    def wrapper(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            localizer: LocalizeManager | None = kwargs.get("localizer")
            if not localizer:
                raise ValueError(
                    "Localizer instance must be passed as a keyword argument."
                )

            result = await func(*args, **kwargs)

            if isinstance(result, dict):
                filtered_result = {
                    key: result[key] for key in result if fields and key not in fields
                }
                if fields:
                    result = localizer.translate_static(
                        {key: result[key] for key in fields if key in result},
                        default_prefix,
                        desired_prefix,
                    )
                    return {**filtered_result, **result}
                result = localizer.translate_static(
                    result, default_prefix, desired_prefix
                )
            elif isinstance(result, list):
                if fields:
                    return [
                        {
                            **{key: obj[key] for key in obj if key not in fields},
                            **localizer.translate_static(
                                {key: obj[key] for key in fields if key in obj},
                                default_prefix,
                                desired_prefix,
                            ),
                        }
                        for obj in result
                    ]
                return [
                    localizer.translate_static(obj, default_prefix, desired_prefix)
                    for obj in result
                ]
            return result

        return inner

    return wrapper


def localize_database_response(
    default_prefix: str, desired_prefix: str, fields: list[str]
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    Decorator to localize dynamic fields in the response.

    :param default_prefix: Default language prefix (e.g., "en").
    :param desired_prefix: Desired language prefix (e.g., "es").
    :param fields: List of dynamic fields to localize.
    :return: A wrapped async function with localized fields.
    """

    def wrapper(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            # Ensure the localizer instance is provided
            localizer: LocalizeManager | None = kwargs.get("localizer")
            if not localizer:
                raise ValueError(
                    "Localizer instance must be passed as a keyword argument."
                )

            # Call the endpoint function
            result = await func(*args, **kwargs)

            # Handle dict and list responses and localize specified dynamic fields
            if isinstance(result, dict):
                # Use LocalizeManager's translate_dynamic directly
                return localizer.translate_dynamic(
                    result, fields, default_prefix, desired_prefix
                )
            if isinstance(result, list):
                return [
                    localizer.translate_dynamic(
                        record, fields, default_prefix, desired_prefix
                    )
                    for record in result
                ]

            return result

        return inner

    return wrapper
