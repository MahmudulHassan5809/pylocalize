import unittest
from typing import Any
from unittest.mock import MagicMock

from pylocalize import (
    LocalizeManager,
    localize_database_response,
    localize_static_response,
)


class TestLocalizeManager(unittest.TestCase):
    def setUp(self) -> None:
        """Set up the LocalizeManager with some mock data."""
        self.localizer = LocalizeManager()
        self.localizer.static_data = {
            "greeting": {"en": "Hello", "es": "Hola"},
            "test": {"en": "Test", "es": "Prueba"},
        }

    def test_translate(self) -> None:
        """Test translation of a string."""
        translated = self.localizer.translate("{greeting} {test}", "es")
        self.assertEqual(translated, "Hola Prueba")

    def test_translate_static(self) -> None:
        """Test translation of static fields in a dictionary."""
        obj = {"message": "{greeting} {test}"}
        translated_obj = self.localizer.translate_static(obj, "en", "es")
        self.assertEqual(translated_obj["message_en"], "Hello Test")
        self.assertEqual(translated_obj["message_es"], "Hola Prueba")

    def test_translate_dynamic(self) -> None:
        """Test translation of dynamic fields in a dictionary."""
        obj = {"field": "value", "field_es": "valor"}
        fields = ["field"]
        translated_obj = self.localizer.translate_dynamic(obj, fields, "en", "es")
        self.assertEqual(translated_obj["field_en"], "value")
        self.assertEqual(translated_obj["field_es"], "valor")


class TestDecorators(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        """Set up a mock LocalizeManager."""
        self.localizer = MagicMock(spec=LocalizeManager)
        self.localizer.translate_static.return_value = {
            "message_en": "Hello Test",
            "message_es": "Hola Prueba",
        }
        # Mock translate_dynamic to return the expected dictionary when called
        self.localizer.translate_dynamic.return_value = {
            "field_en": "value",
            "field_es": "valor",
        }

    async def test_localize_static_response(self) -> None:
        """Test the localize_static_response decorator."""

        @localize_static_response(
            default_prefix="en", desired_prefix="es", fields=["message"]
        )
        async def mock_func(localizer: LocalizeManager) -> dict[str, Any]:
            return {"message": "{greeting} {test}"}

        result = await mock_func(localizer=self.localizer)
        self.assertEqual(result["message_en"], "Hello Test")
        self.assertEqual(result["message_es"], "Hola Prueba")

    async def test_localize_database_response(self) -> None:
        """Test the localize_database_response decorator."""

        @localize_database_response(
            default_prefix="en", desired_prefix="es", fields=["field"]
        )
        async def mock_func(localizer: LocalizeManager) -> dict[str, Any]:
            return {"field": "value", "field_es": "valor"}

        result = await mock_func(localizer=self.localizer)
        self.assertEqual(result["field_en"], "value")
        self.assertEqual(result["field_es"], "valor")


if __name__ == "__main__":
    unittest.main()
