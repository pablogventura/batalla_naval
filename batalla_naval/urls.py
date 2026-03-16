#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from bn import views as bn_views

admin.autodiscover()

urlpatterns = [
    path('menu/', bn_views.menu_principal, name='menu_principal'),
    path('registrarse/', bn_views.nuevo_usuario, name='nuevo_usuario'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('nueva_partida/', bn_views.nueva_partida, name='nueva_partida'),
    path('partida/<int:partida_id>/ubicar_barcos/', bn_views.ubicar_barcos, name='ubicar_barcos'),
    path('partida/<int:partida_id>/esperando_jugadores/', bn_views.esperando_jugadores, name='esperando_jugadores'),
    path('partida/<int:partida_id>/esperando_turno/', bn_views.esperando_turno, name='esperando_turno'),
    path('partida/<int:partida_id>/ataque/', bn_views.elegir_enemigo, name='elegir_enemigo'),
    path('partida/<int:partida_id>/ataque/<int:jugador_id>/', bn_views.ataque, name='ataque'),
    path('partida/<int:partida_id>/defensa/', bn_views.defensa, name='defensa'),
    path('partida/<int:partida_id>/ganador/', bn_views.ganador, name='ganador'),
    path('partida/<int:partida_id>/derrotado/', bn_views.derrotado, name='derrotado'),
    path('partida/<int:partida_id>/rendirse/', bn_views.rendirse, name='rendirse'),
    path('partida/<int:partida_id>/abandonar/', bn_views.abandonar, name='abandonar'),
    path('partida/<int:partida_id>/resultados/', bn_views.resultados, name='resultados'),
    path('admin/', admin.site.urls),
]
