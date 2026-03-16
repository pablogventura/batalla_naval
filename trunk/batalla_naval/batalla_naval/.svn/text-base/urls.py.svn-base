#!/usr/bin/env python
# -*- coding: utf8 -*- 

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from bn.models import Partida
admin.autodiscover()

urlpatterns = patterns('',
    (r'^menu/$', 'bn.views.menu_principal'),
    (r'^registrarse/$', 'bn.views.nuevo_usuario'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^nueva_partida/$', 'bn.views.nueva_partida'),
    (r'^partida/(?P<partida_id>\d+)/ubicar_barcos/$', 'bn.views.ubicar_barcos'),
    (r'^partida/(?P<partida_id>\d+)/esperando_jugadores/$', 'bn.views.esperando_jugadores'),
    (r'^partida/(?P<partida_id>\d+)/esperando_turno/$', 'bn.views.esperando_turno'),
    (r'^partida/(?P<partida_id>\d+)/ataque/$', 'bn.views.elegir_enemigo'),
    (r'^partida/(?P<partida_id>\d+)/ataque/(?P<jugador_id>\d+)$', 'bn.views.ataque'),
    (r'^partida/(?P<partida_id>\d+)/defensa/$', 'bn.views.defensa'),
    (r'^partida/(?P<partida_id>\d+)/ganador/$', 'bn.views.ganador'),
    (r'^partida/(?P<partida_id>\d+)/derrotado/$', 'bn.views.derrotado'),
    (r'^partida/(?P<partida_id>\d+)/rendirse/$', 'bn.views.rendirse'),
    (r'^partida/(?P<partida_id>\d+)/abandonar/$', 'bn.views.abandonar'),
    (r'^partida/(?P<partida_id>\d+)/resultados/$', 'bn.views.resultados'),
    # Example:
    # (r'^batalla_naval/', include('batalla_naval.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
