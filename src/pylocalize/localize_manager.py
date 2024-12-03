import json
import re
from typing import Any


class LocalizeManager:
    """
    A manager for translating static and dynamic fields in objects using predefined translations.

    Attributes:
        static_data_path: Path to the JSON file containing static translations (optional).
        static_data: A dictionary holding static translations.
    """

    def __init__(self, static_data_path: str | None = None) -> None:
        """
        Initialize the localization manager with static translations.

        Args:
            static_data_path: Optional path to a JSON file containing static translation data.
        """
        self.static_data_path = static_data_path
        self.static_data: dict[str, dict[str, str]] = (
            self._load_static_data(static_data_path) if static_data_path else {}
        )

    def _load_static_data(self, path: str) -> dict[str, dict[str, str]]:
        """
        Load static translations from a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            A dictionary of translations loaded from the file.
        """
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)  # type: ignore

    def translate(self, value: str, prefix: str) -> str:
        """
        Translate placeholders in a string based on the specified language prefix.

        Args:
            value: The string containing placeholders to translate.
            prefix: The language prefix (e.g., "en" or "es").

        Returns:
            The string with placeholders replaced by their translations.
        """
        placeholder_pattern = re.compile(r"\{(.*?)\}")
        return placeholder_pattern.sub(
            lambda match: self.static_data.get(match.group(1), {}).get(
                prefix, match.group(0)
            ),
            value,
        )

    def translate_static(
        self, obj: dict[str, Any], default_prefix: str, desired_prefix: str
    ) -> dict[str, Any]:
        """
        Translate static fields in the object based on predefined translations.

        Args:
            obj: The dictionary containing static fields to translate.
            default_prefix: The default language prefix (e.g., "en").
            desired_prefix: The desired language prefix (e.g., "es").

        Returns:
            A new dictionary with translated static fields for both prefixes.
        """
        new_obj: dict[str, Any] = {}

        for key, value in obj.items():
            if isinstance(value, str):
                new_obj[f"{key}_{default_prefix}"] = self.translate(
                    value, default_prefix
                )
                new_obj[f"{key}_{desired_prefix}"] = self.translate(
                    value, desired_prefix
                )
            else:
                new_obj[key] = value

        return new_obj

    def translate_dynamic(
        self,
        obj: dict[str, Any],
        fields: list[str],
        default_prefix: str,
        desired_prefix: str,
    ) -> dict[str, Any]:
        """
        Translate dynamic fields in the object for the given prefixes.

        Args:
            obj: The dictionary containing dynamic fields to translate.
            fields: List of fields to translate.
            default_prefix: The default language prefix (e.g., "en").
            desired_prefix: The desired language prefix (e.g., "es").

        Returns:
            The dictionary with dynamically translated fields added.
        """
        for field in fields:
            obj[f"{field}_{default_prefix}"] = obj.get(field, "")
            obj[f"{field}_{desired_prefix}"] = obj.get(
                f"{field}_{desired_prefix}", obj.get(field, "")
            )
        return obj


if __name__ == "__main__":
    localizer = LocalizeManager()

    data = {"message": "{greeting} Mark test {test} {test3}"}
    result = localizer.translate_static(data, default_prefix="en", desired_prefix="es")
    print(result)
