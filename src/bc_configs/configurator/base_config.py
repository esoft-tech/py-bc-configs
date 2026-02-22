import logging
import os
import re
from abc import ABC
from typing import Any, LiteralString, cast

from pydantic import BaseModel, ValidationError, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError


def _get_env_name_by_field_name(class_name: str, field_name: str) -> str:
    """
    Generate the environment variable name based on the class name and field name.

    This function is used when defining a custom configuration class that extends BaseConfig
    or any other BaseConfig extended class, in order to use different names for environment
    variables for them.

    :param class_name: The name of the class.
    :type class_name: str
    :param field_name: The name of the field.
    :type field_name: str
    :return: The environment variable name generated based on the class name and field name.
    :rtype: str
    """
    return "_".join(
        [
            i.replace("_", "").upper()
            for i in re.findall(
                r"[A-ZА-Я_][a-zа-я\d]*",
                f"{class_name.replace('Config', '')}_{field_name}",
            )  # noqa: RUF001
        ],
    )


def _get_field_form_env(
    *,
    class_name: str | None = None,
    field_name: str | None = None,
    env_name: str | None = None,
) -> Any:
    """
    Get the value of a field from the environment variables.

    If the `env_name` parameter is provided, it returns the value of the corresponding
    environment variable.
    If the `class_name` and `field_name` parameters are provided, it generates the
    environment variable name using
    `_get_env_name_by_field_name` function and returns the value of the corresponding
    environment variable.

    :param class_name: The name of the class.
    :type class_name: str, optional
    :param field_name: The name of the field.
    :type field_name: str, optional
    :param env_name: The name of the environment variable.
    :type env_name: str, optional
    :return: The value of the field from the environment variables.
    :rtype: Any
    :raises TypeError: If the key type for the variable is invalid.
    """
    result = None
    if isinstance(env_name, str):
        result = os.getenv(env_name)
    elif isinstance(class_name, str) and isinstance(field_name, str):
        result = os.getenv(_get_env_name_by_field_name(class_name, field_name))
    else:
        raise TypeError("Invalid key type for variable")

    return result


class BaseConfig(BaseModel, ABC):
    """
    Provides to receive values from the environment variables on the validation step of
    pydantic model.

    When a required field is missing, the error message will include the environment
    variable name that should be set, making it easier to debug configuration issues.

    Example:

    .. code:: python

        class MyConfig(BaseConfig):
            db_host: str
            db_port: int

        # If MY_DB_HOST or MY_DB_PORT are not set, the error will show:
        # db_host: Field required  →  env var: 'MY_DB_HOST'
        # db_port: Field required  →  env var: 'MY_DB_PORT'
    """

    @model_validator(mode="before")
    @classmethod
    def _populate_from_env(cls, data: dict) -> Any:
        """
        This function checks if any value in the input `data` dictionary is None.
        If a value is None, it retrieves the value from the environment variables
        based on the class name and field name.

        :param cls: The class that the function is called on.
        :type cls: type
        :param data: The dictionary of values to check and update.
        :type data: dict
        :return: The updated dictionary of values that will be stored in config instance.
        :rtype: dict
        """
        for field_name, field_info in cls.model_fields.items():
            if data.get(field_name) is None:
                if isinstance(field_info.json_schema_extra, dict):
                    env_name = cast(
                        str | None, field_info.json_schema_extra.get("env_name")
                    )
                elif field_info.json_schema_extra is None:
                    env_name = None
                else:
                    logging.warning(
                        f"Unexpected json_schema_extra type for {cls.__name__}.{field_name}: {type(field_info.json_schema_extra)}"
                    )
                    env_name = None

                value = _get_field_form_env(
                    class_name=cls.__name__,
                    field_name=field_name,
                    env_name=env_name,
                )
                if value is not None:
                    data[field_name] = value

        return data

    @model_validator(mode="wrap")
    @classmethod
    def _enrich_errors(cls, values: Any, handler):
        """
        Intercept ValidationError and enrich error messages with environment variable names.

        This makes it easier for users to understand which environment variable they
        need to set when a required field is missing.

        :param values: Input data
        :type values: Any
        :param handler: Handler function (standard Pydantic validation)
        :type handler: Callable
        :return: Validated data
        :rtype: Any
        :raises ValidationError: If required fields are missing
        """
        try:
            return handler(values)
        except ValidationError as exc:
            # Enrich each error with environment variable name
            original_errors = exc.errors(include_url=False)
            enriched_errors: list[InitErrorDetails] = []

            for err in original_errors:
                field = cast(str, err["loc"][0]) if err["loc"] else None
                cfg_key = None

                # Try to generate env var name
                if field:
                    field_info = cls.model_fields.get(field)
                    if field_info:
                        if isinstance(field_info.json_schema_extra, dict):
                            env_name = cast(
                                str | None, field_info.json_schema_extra.get("env_name")
                            )
                        elif field_info.json_schema_extra is None:
                            env_name = None
                        else:
                            logging.warning(
                                f"Unexpected json_schema_extra type for {cls.__name__}.{field}: {type(field_info.json_schema_extra)}"
                            )
                            env_name = None
                        if env_name is None:
                            cfg_key = _get_env_name_by_field_name(cls.__name__, field)
                        else:
                            cfg_key = env_name

                # Build enriched message
                msg = err["msg"]
                if cfg_key:
                    msg = f"{msg}  →  env var: '{cfg_key}'"
                # Include field description if available
                if field and field_info and field_info.description:
                    msg = f"{msg} (description: {field_info.description})"

                enriched_errors.append(
                    InitErrorDetails(
                        type=PydanticCustomError(
                            cast(LiteralString, err["type"]),
                            "{enriched_msg}",
                            {"enriched_msg": msg},
                        ),
                        loc=err["loc"],
                        input=err.get("input"),
                    )
                )

            raise ValidationError.from_exception_data(
                cls.__name__,
                enriched_errors,  # type: ignore[arg-type]
            ) from exc
