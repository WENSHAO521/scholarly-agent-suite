"""Minimal structural JSON Schema (draft-07 subset) validator.

Deliberately not a full JSON Schema engine (rule 64) -- implements only the
keywords this Suite's protocols actually use: type, required, properties,
additionalProperties, enum, const, items, format(date, best-effort), and a
single-file local $ref (e.g. "provenance.schema.json#"). Good enough to catch
a producer emitting a shape a consumer's schema would reject; not a
general-purpose validator.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


class ValidationError(ValueError):
    def __init__(self, path: str, message: str):
        super().__init__(f"{path}: {message}")
        self.path = path
        self.message = message


def _resolve_ref(ref: str, schema_dir: Path) -> dict:
    file_part = ref.split("#", 1)[0]
    ref_path = schema_dir / file_part
    return json.loads(ref_path.read_text(encoding="utf-8"))


def validate(instance: Any, schema: dict, schema_dir: Path, path: str = "$") -> None:
    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], schema_dir)
        validate(instance, resolved, schema_dir, path)
        return

    if "const" in schema and instance != schema["const"]:
        raise ValidationError(path, f"expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(path, f"{instance!r} not in enum {schema['enum']}")

    schema_type = schema.get("type")
    if schema_type:
        expected = _TYPE_MAP[schema_type]
        # bool is a subclass of int in Python -- keep integer/number distinct from boolean.
        if schema_type in ("integer", "number") and isinstance(instance, bool):
            raise ValidationError(path, f"expected {schema_type}, got boolean")
        if not isinstance(instance, expected):
            raise ValidationError(path, f"expected {schema_type}, got {type(instance).__name__}")

    if schema.get("format") == "date" and isinstance(instance, str):
        if not _DATE_RE.match(instance):
            raise ValidationError(path, f"'{instance}' is not an ISO date")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise ValidationError(path, f"missing required field '{key}'")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], schema_dir, f"{path}.{key}")
            elif additional is False:
                raise ValidationError(path, f"unexpected additional property '{key}'")
            elif isinstance(additional, dict):
                validate(value, additional, schema_dir, f"{path}.{key}")

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            validate(item, schema["items"], schema_dir, f"{path}[{i}]")


def validate_file(instance: Any, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate(instance, schema, schema_path.parent)
