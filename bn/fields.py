#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import ast


class ListField(models.TextField):
    description = "Stores a python list"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)


class TupleField(models.TextField):
    description = "Stores a python tuple"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return ()
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return ()
        if isinstance(value, tuple):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)
