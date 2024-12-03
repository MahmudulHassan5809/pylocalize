from functools import wraps
from typing import Callable, Awaitable, Any
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
            # Ensure the localizer instance is provided
            localizer: LocalizeManager | None = kwargs.get("localizer")
            if not localizer:
                raise ValueError(
                    "Localizer instance must be passed as a keyword argument."
                )

            # Call the endpoint function (await if it's async)
            result = await func(*args, **kwargs)
            print(result, fields, "----sss")

            # Handle static translation for dict and list responses
            if isinstance(result, dict):
                filtered_result = {
                    key: result[key] for key in result if fields and key not in fields
                }
                if fields:
                    # Static translation for specified fields only
                    result = localizer.translate_static(
                        {key: result[key] for key in fields if key in result},
                        default_prefix,
                        desired_prefix,
                    )
                    return {**filtered_result, **result}
                else:
                    # If no fields are specified, localize all static fields
                    result = localizer.translate_static(
                        result, default_prefix, desired_prefix
                    )
            elif isinstance(result, list):
                # Handle lists of dicts (static translation for each item)
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
                else:
                    return [
                        localizer.translate_static(obj, default_prefix, desired_prefix)
                        for obj in result
                    ]
            return result

        return inner

    return wrapper
