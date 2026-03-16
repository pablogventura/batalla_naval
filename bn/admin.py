#!/usr/bin/env python

from django.contrib import admin

from bn.models import (
    Acorazado,
    Fragata,
    Jugador,
    Partida,
    Patrulla,
    Portaaviones,
    Radar,
    Submarino,
    Tablero,
    TableroVisible,
)

admin.site.register(Partida)
admin.site.register(Tablero)
admin.site.register(Jugador)
admin.site.register(Acorazado)
admin.site.register(Patrulla)
admin.site.register(Portaaviones)
admin.site.register(Submarino)
admin.site.register(Fragata)
admin.site.register(Radar)
admin.site.register(TableroVisible)
