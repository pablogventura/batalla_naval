#!/usr/bin/env python
# -*- coding: utf8 -*-

from bn.models import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404


def requiere_turno(vista):
    """
    Requiere para pasar a la vista que el jugador tenga el turno, sino lo lleva
    a esperar turno.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if jugador.es_su_turno:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.esperando_turno', args=(p.id,)))
    return result


def requiere_haber_atacado(vista):
    """
    Requiere para pasar a la vista que el jugador haya atacado, sino lo lleva
    a elegir enemigo para atacar.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if jugador.ya_ataco:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.elegir_enemigo', args=(p.id,)))
    return result


def requiere_no_haber_atacado(vista):
    """
    Requiere para pasar a la vista que el jugador tenga no haya atacado, sino
    lo lleva a defender.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if not jugador.ya_ataco:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.defensa', args=(p.id,)))
    return result
    
def requiere_partida_iniciada(vista):
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    haya terminado sino lo lleva al menu principal.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = Partida.objects.get(pk=partida_id)
        if p.iniciada:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.ubicar_barcos', args=(p.id,)))
    return result

def requiere_que_la_partida_exista(vista):
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    exista, sino lo lleva al menu principal.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        if Partida.objects.filter(pk=partida_id).exists():
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.menu_principal'))
    return result

def requiere_partida_no_terminada(vista):
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    no haya terminado, sino lleva a los resultados.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = Partida.objects.get(pk=partida_id)
        if not p.terminada:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.resultados', args=(p.id,)))
    return result

def requiere_partida_terminada(vista):
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    haya terminado sino lo lleva al menu principal.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        usuario = request.user
        p = Partida.objects.get(pk=partida_id)
        if p.terminada:
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.menu_principal'))
    return result

def requiere_que_el_enemigo_exista(vista):
    """
    Requiere para pasar a la vista que el enemigo que viene como argumento
    exista y no este ya derrotado, sino lo lleva a elegir otro enemigo.
    """
    def result(*args, **kwargs):
        request = args[0]
        partida_id = kwargs['partida_id']
        enemigo_id = kwargs['jugador_id']
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        if p.jugador_set.filter(pk=enemigo_id, derrotado=False).exists():
            return vista(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('bn.views.elegir_enemigo', args=(p.id,)))
    return result
