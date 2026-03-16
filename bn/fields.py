#!/usr/bin/env python

from __future__ import annotations

import ast
from typing import Any

from django.db import models


class ListField(models.TextField):
    description = "Stores a python list"

    def from_db_value(
        self,
        value: Any,
        expression: Any,
        connection: Any,
    ) -> list[Any]:
        if value is None:
            return []
        return self.to_python(value)

    def to_python(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return value
        return str(value)


class TupleField(models.TextField):
    description = "Stores a python tuple"

    def from_db_value(
        self,
        value: Any,
        expression: Any,
        connection: Any,
    ) -> tuple[Any, ...]:
        if value is None:
            return ()
        return self.to_python(value)

    def to_python(self, value: Any) -> tuple[Any, ...]:
        if value is None:
            return ()
        if isinstance(value, tuple):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return value
        return str(value)
