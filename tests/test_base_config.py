import os
import unittest
from unittest.mock import patch

from pydantic import Field, ValidationError

from bc_configs.configurator.base_config import BaseConfig


class TestBaseConfig(unittest.TestCase):
    def test_change_from_env_if_none(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            field1: str
            field2: int
            field3: float
            field4: bool

        # Mock the os.environ dictionary with the desired values
        with patch.dict(
            os.environ,
            {
                "CUSTOM_FIELD1": "value1",
                "CUSTOM_FIELD2": "42",
                "CUSTOM_FIELD3": "3.14",
                "CUSTOM_FIELD4": "True",
            },
        ):
            # Create an instance of the custom configuration class
            config = CustomConfig()  # type: ignore[call-arg]

            # Check if the values are retrieved from the environment variables correctly
            self.assertEqual(config.field1, "value1")
            self.assertEqual(config.field2, 42)
            self.assertAlmostEqual(config.field3, 3.14)
            self.assertTrue(config.field4)

    def test_missing_field_error(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            field1: str
            field2: int

        # Mock the os.environ dictionary with a subset of the required fields
        with patch.dict(os.environ, {"CUSTOM_FIELD1": "value1"}):
            # Create an instance of the custom configuration class
            with self.assertRaises(ValidationError) as context:
                _ = CustomConfig()  # type: ignore[call-arg]

            # Check if the error message includes the environment variable name
            error_msg = str(context.exception)
            self.assertIn("CUSTOM_FIELD2", error_msg)
            self.assertIn("field2", error_msg)

    def test_missing_field_error_with_description(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            field1: str
            field2: int = Field(description="Описание поля field2")

        # Mock the os.environ dictionary with a subset of the required fields
        with patch.dict(os.environ, {"CUSTOM_FIELD1": "value1"}):
            # Create an instance of the custom configuration class
            with self.assertRaises(ValidationError) as context:
                _ = CustomConfig()  # type: ignore[call-arg]

            # Check if the error message includes the environment variable name
            error_msg = str(context.exception)
            self.assertIn("CUSTOM_FIELD2", error_msg)
            self.assertIn("field2", error_msg)

    def test_custom_env_var_name(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            my_field: str = Field(json_schema_extra={"env_name": "CUSTOM_ENV_NAME"})

        # Mock the os.environ dictionary with the desired values
        with patch.dict(os.environ, {"CUSTOM_ENV_NAME": "value1"}):
            # Create an instance of the custom configuration class
            config = CustomConfig()  # type: ignore[call-arg]

        # Check if the values are retrieved from the environment variables correctly
        self.assertEqual(config.my_field, "value1")

    def test_custom_env_var_name_missing(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            my_field: str = Field(json_schema_extra={"env_name": "CUSTOM_ENV_NAME"})

        # Mock the os.environ dictionary without the required field
        with patch.dict(os.environ, {}, clear=True):
            # Create an instance of the custom configuration class
            with self.assertRaises(ValidationError) as context:
                _ = CustomConfig()  # type: ignore[call-arg]

            # Check if the error message includes the environment variable name
            error_msg = str(context.exception)
            self.assertIn("CUSTOM_ENV_NAME", error_msg)
            self.assertIn("my_field", error_msg)

    def test_multiple_missing_fields_error(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            field1: str
            field2: int
            field3: float

        # Mock the os.environ dictionary without the required fields
        with patch.dict(os.environ, {}, clear=True):
            # Create an instance of the custom configuration class
            with self.assertRaises(ValidationError) as context:
                _ = CustomConfig()  # type: ignore[call-arg]

            # Check if the error message includes all environment variable names
            error_msg = str(context.exception)
            self.assertIn("CUSTOM_FIELD1", error_msg)
            self.assertIn("CUSTOM_FIELD2", error_msg)
            self.assertIn("CUSTOM_FIELD3", error_msg)
            self.assertIn("field1", error_msg)
            self.assertIn("field2", error_msg)
            self.assertIn("field3", error_msg)

    def test_missing_field_error_without_description(self) -> None:
        # Create an instance of the custom configuration class that extends BaseConfig
        class CustomConfig(BaseConfig):
            field1: str  # No description

        # Mock the os.environ dictionary without the required field
        with patch.dict(os.environ, {}, clear=True):
            # Create an instance of the custom configuration class
            with self.assertRaises(ValidationError) as context:
                _ = CustomConfig()  # type: ignore[call-arg]

            # Check if the error message includes the environment variable name but no description
            error_msg = str(context.exception)
            self.assertIn("CUSTOM_FIELD1", error_msg)
            self.assertIn("field1", error_msg)
            self.assertNotIn("description:", error_msg)


if __name__ == "__main__":
    unittest.main()
