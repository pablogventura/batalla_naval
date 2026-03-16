#!/usr/bin/env python

from django import template

register = template.Library()


@register.simple_tag(name="render_celda")
def render_celda(lista, x, y):
    x = ord(x) - 65
    y = y - 1
    return lista[(x, y)].render
