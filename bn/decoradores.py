#!/usr/bin/env python

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from bn.models import Partida

_ViewResult = HttpResponse | HttpResponseRedirect
_ViewFunc = Callable[..., _ViewResult]
F = TypeVar("F", bound=_ViewFunc)


def requiere_turno(vista: F) -> F:
    """
    Requiere para pasar a la vista que el jugador tenga el turno, sino lo lleva
    a esperar turno.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        request = args[0]
        partida_id = kwargs["partida_id"]
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if jugador.es_su_turno:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("esperando_turno", args=(p.id,)))

    return result  # type: ignore[return-value]


def requiere_haber_atacado(vista: F) -> F:
    """
    Requiere para pasar a la vista que el jugador haya atacado, sino lo lleva
    a elegir enemigo para atacar.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        request = args[0]
        partida_id = kwargs["partida_id"]
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if jugador.ya_ataco:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("elegir_enemigo", args=(p.id,)))

    return result  # type: ignore[return-value]


def requiere_no_haber_atacado(vista: F) -> F:
    """
    Requiere para pasar a la vista que el jugador tenga no haya atacado, sino
    lo lleva a defender.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        request = args[0]
        partida_id = kwargs["partida_id"]
        usuario = request.user
        p = get_object_or_404(Partida, pk=partida_id)
        jugador = get_object_or_404(p.jugador_set, usuario=usuario)
        if not jugador.ya_ataco:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("defensa", args=(p.id,)))

    return result  # type: ignore[return-value]


def requiere_partida_iniciada(vista: F) -> F:
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    haya terminado sino lo lleva al menu principal.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        partida_id = kwargs["partida_id"]
        p = Partida.objects.get(pk=partida_id)
        if p.iniciada:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("ubicar_barcos", args=(p.id,)))

    return result  # type: ignore[return-value]


def requiere_que_la_partida_exista(vista: F) -> F:
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    exista, sino lo lleva al menu principal.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        partida_id = kwargs["partida_id"]
        if Partida.objects.filter(pk=partida_id).exists():
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("menu_principal"))

    return result  # type: ignore[return-value]


def requiere_partida_no_terminada(vista: F) -> F:
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    no haya terminado, sino lleva a los resultados.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        partida_id = kwargs["partida_id"]
        p = Partida.objects.get(pk=partida_id)
        if not p.terminada:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("resultados", args=(p.id,)))

    return result  # type: ignore[return-value]


def requiere_partida_terminada(vista: F) -> F:
    """
    Requiere para pasar a la vista que la partida que viene como argumento
    haya terminado sino lo lleva al menu principal.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        partida_id = kwargs["partida_id"]
        p = Partida.objects.get(pk=partida_id)
        if p.terminada:
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("menu_principal"))

    return result  # type: ignore[return-value]


def requiere_que_el_enemigo_exista(vista: F) -> F:
    """
    Requiere para pasar a la vista que el enemigo que viene como argumento
    exista y no este ya derrotado, sino lo lleva a elegir otro enemigo.
    """

    def result(*args: object, **kwargs: object) -> _ViewResult:
        partida_id = kwargs["partida_id"]
        enemigo_id = kwargs["jugador_id"]
        p = get_object_or_404(Partida, pk=partida_id)
        if p.jugador_set.filter(pk=enemigo_id, derrotado=False).exists():
            return vista(*args, **kwargs)
        return HttpResponseRedirect(reverse("elegir_enemigo", args=(p.id,)))

    return result  # type: ignore[return-value]
