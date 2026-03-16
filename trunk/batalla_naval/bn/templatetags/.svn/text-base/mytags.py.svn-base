#!/usr/bin/env python
# -*- coding: utf8 -*-

from django import template
from bn.models import Tablero
from bn.celda import Celda

register = template.Library()


@register.simple_tag(name='render_celda')
def render_celda(lista, x, y):
    x = ord(x) - 65
    y = y - 1
    return lista[(x, y)].render
