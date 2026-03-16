#!/usr/bin/env python

from __future__ import annotations

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from bn.decoradores import (
    requiere_haber_atacado,
    requiere_no_haber_atacado,
    requiere_partida_iniciada,
    requiere_partida_no_terminada,
    requiere_partida_terminada,
    requiere_que_el_enemigo_exista,
    requiere_que_la_partida_exista,
    requiere_turno,
)
from bn.excepciones import (
    AtaqueFueraDelTablero,
    BarcoMalUbicado,
    BarcoNoSumergible,
    BarcoTocado,
    EscudoFueraDeTablero,
    EscudoYaUsado,
    NoHayBarco,
    NoPuedeAtaquePotente,
    NoTieneMovimientoLargo,
    RadarUsado2VecesContra,
    SubmarinoSinMovimiento,
    SumergidoTresVeces,
)
from bn.forms import (
    AtaqueForm,
    DefensaForm,
    NuevaPartidaForm,
    NuevoUsuarioForm,
    UbicarBarcoForm,
)
from bn.models import (
    Jugador,
    Partida,
    Tablero,
)


@login_required
def menu_principal(request: HttpRequest) -> HttpResponse:
    """
    Vista que muestra el menu principal con las partidas que esperan jugadores
    y las que ya estan en curso.
    """
    partidas_actuales = Partida.objects.filter(terminada=False)
    return render(
        request,
        "menu_principal.html",
        {
            "partidas_actuales": partidas_actuales,
            "usuario": request.user,
        },
    )


@login_required
@requiere_que_la_partida_exista
def ubicar_barcos(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja la ubicacion de barcos en el tablero.
    Si vienen datos Post es que viene la ubicacion de un barco y si no muestra
    el formulario para ubicar, y las ubicaciones actuales en el tablero.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    usuario = request.user
    jugador = p.jugador_set.filter(usuario=request.user)
    assert len(jugador) <= 1  # no puede tener mas de un jugador por partida!
    if len(jugador) == 0:
        if not p.iniciada:
            jugador = p.jugador_set.create(usuario=request.user)
            jugador.tablero = Tablero(
                ancho=p.ancho_tablero,
                cant_acorazados=p.cant_acorazados,
                cant_patrullas=p.cant_patrullas,
                cant_portaaviones=p.cant_portaaviones,
                cant_submarinos=p.cant_submarinos,
                cant_fragatas=p.cant_fragatas,
            )
            jugador.tablero.save()
            jugador.tablero.crear_barcos()
        else:
            return HttpResponseRedirect(reverse("menu_principal"))
    else:
        jugador = jugador[0]
    tablero = jugador.tablero
    barco = tablero.barco_sin_ubicar()
    error = ""
    if barco is None:
        # ya estan ubicados todos los barcos
        jugador.ubicaciones_confirmadas = True
        jugador.save()
        if p.debe_iniciarse():
            p.iniciar()
        return HttpResponseRedirect(reverse("esperando_jugadores", args=(p.id,)))
    if request.method == "POST":  # me fijo si vienen datos
        form = UbicarBarcoForm(request.POST)

        if form.is_valid():
            x = form.cleaned_data["x"]
            y = form.cleaned_data["y"]
            horizontal = form.cleaned_data["horizontal"]
            barco.x = x
            barco.y = y
            barco.horizontal = horizontal

            if barco.estoy_bien_ubicado():
                barco.save()
                return HttpResponseRedirect(reverse("ubicar_barcos", args=(p.id,)))
            else:
                error = "El barco no esta bien ubicado. Por favor reubiquelo."

    else:
        form = UbicarBarcoForm()
    return render(
        request,
        "ubicacion_barcos.html",
        {
            "partida": p,
            "error": error,
            "usuario": usuario,
            "form": form,
            "tablero": tablero,
            "celdas": tablero.celdas,
            "barco": barco,
        },
    )


def nuevo_usuario(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja la registracion de usuarios.
    Si vienen datos Post es que vienen los datos de un nuevo usuario y responde
    registrandolo e iniciando sesion para el. En caso contrario muestra el
    formulario para registrarse.
    """
    if request.method == "POST":  # me fijo si vienen datos
        form = NuevoUsuarioForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            contrasena = form.cleaned_data["password2"]

            user = User.objects.create_user(nombre, email, contrasena)
            user = authenticate(username=nombre, password=contrasena)
            login(request, user)
            return HttpResponseRedirect(reverse("menu_principal"))
    else:
        form = NuevoUsuarioForm()
    return render(request, "nuevo_usuario.html", {"form": form})


@login_required
def nueva_partida(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja la creacion de partidas.
    Si vienen datos Post crea la partida con esos datos. Caso contrario muestra
    el formulario para crearla.
    """
    if request.method == "POST":  # me fijo si vienen datos
        form = NuevaPartidaForm(request.POST)
        if form.is_valid():
            p = form.save()
            return HttpResponseRedirect(reverse("ubicar_barcos", args=(p.id,)))
    else:
        form = NuevaPartidaForm()

    return render(request, "nueva_partida.html", {"form": form})


@login_required
@requiere_que_la_partida_exista
def esperando_jugadores(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    p = get_object_or_404(Partida, pk=partida_id)
    if not p.iniciada:
        faltan = p.cant_jugadores - p.jugador_set.count()
        return render(
            request,
            "esperando_jugadores.html",
            {
                "partida": p,
                "jugadores_faltantes": faltan,
                "usuario": request.user,
            },
        )
    else:
        return HttpResponseRedirect(reverse("esperando_turno", args=(p.id,)))


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_partida_no_terminada
def esperando_turno(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja la espera del turno.
    Controla que el jugador gane o pierda, y lo lleva a vistas especificas.
    Si es el turno del jugador, lo lleva a elegir enemigo para atacar.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    no_derrotados = p.jugador_set.exclude(derrotado=True)
    if no_derrotados.count() == 1 and jugador in no_derrotados:
        return HttpResponseRedirect(reverse("ganador", args=(p.id,)))
    if jugador.derrotado:
        return HttpResponseRedirect(reverse("derrotado", args=(p.id,)))
    if jugador.es_su_turno:
        return HttpResponseRedirect(reverse("elegir_enemigo", args=(p.id,)))
    else:
        return render(
            request,
            "esperando_turno.html",
            {
                "partida": p,
                "tablero": jugador.tablero,
                "celdas": jugador.tablero.celdas,
                "usuario": request.user,
            },
        )


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_turno
@requiere_no_haber_atacado
@requiere_partida_no_terminada
def elegir_enemigo(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja la eleccion de un enemigo para atacar.
    Si no hay mas de dos jugadores, lleva al usuario directamente a atacar
    al enemigo contrario.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    if len(p.jugador_set.exclude(derrotado=True)) > 2:
        jugadores = p.jugador_set.exclude(derrotado=True)
        return render(
            request,
            "elegir_enemigo.html",
            {
                "partida": p,
                "jugadores": jugadores,
                "usuario": request.user,
            },
        )
    else:
        assert len(p.jugador_set.exclude(pk=jugador.id).exclude(derrotado=True)) == 1
        jugador_enemigo = p.jugador_set.exclude(pk=jugador.id).exclude(derrotado=True)[
            0
        ]
        return HttpResponseRedirect(reverse("ataque", args=(p.id, jugador_enemigo.id)))


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_turno
@requiere_no_haber_atacado
@requiere_que_el_enemigo_exista
@requiere_partida_no_terminada
def ataque(
    request: HttpRequest, partida_id: int, jugador_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja un ataque.
    Recibe la partida y el jugador al que atacar.
    Muestra el tablero visible del jugador enemigo con los ataques anteriores
    y demas.
    Permite al jugador atacante elegir el tipo de ataque y la ubicacion.
    Si vienen datos post, hace el ataque y muestra al jugador los resultados.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    mijugador = get_object_or_404(p.jugador_set, usuario=request.user)
    enemigo = get_object_or_404(Jugador, pk=jugador_id)
    tablero_enemigo = get_object_or_404(
        mijugador.tableros_visibles, tablero_atacado=enemigo.tablero
    )
    error = ""
    mijugador.tablero.sacar_escudo()
    mijugador.tablero.emerger_submarino()
    if request.method == "POST":  # me fijo si vienen datos
        form = AtaqueForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data["tipo"]
            x = form.cleaned_data["x"]
            y = form.cleaned_data["y"]
            try:
                if tipo == "N":
                    tablero_enemigo.ataque_normal((x, y))
                elif tipo == "P":
                    tablero_enemigo.ataque_potente((x, y))
                elif tipo == "R":
                    tablero_enemigo.ataque_radar((x, y))
            except NoPuedeAtaquePotente:
                error = "No posee ataque potente"
            except AtaqueFueraDelTablero:
                error = "Ataque fuera del tablero"
            except RadarUsado2VecesContra:
                error = "Ya uso dos veces el radar contra este jugador"

            if error:
                jugadores = p.jugador_set.exclude(derrotado=True)
                return render(
                    request,
                    "atacar.html",
                    {
                        "form": form,
                        "usuario": request.user,
                        "partida": p,
                        "error": error,
                        "jugadores": jugadores,
                        "enemigo": enemigo,
                        "tablero": tablero_enemigo,
                        "celdas": tablero_enemigo.celdas,
                    },
                )
            mijugador.ya_ataco = True
            mijugador.save()
            if p.jugador_set.exclude(derrotado=True).count() == 1:
                return HttpResponseRedirect(reverse("ganador", args=(p.id,)))

            return render(
                request,
                "resultados_ataque.html",
                {
                    "form": form,
                    "usuario": request.user,
                    "partida": p,
                    "enemigo": enemigo,
                    "error": error,
                    "tablero": tablero_enemigo,
                    "celdas": tablero_enemigo.celdas,
                },
            )

    else:
        form = AtaqueForm()
    jugadores = p.jugador_set.exclude(derrotado=True)
    return render(
        request,
        "atacar.html",
        {
            "form": form,
            "usuario": request.user,
            "partida": p,
            "error": error,
            "jugadores": jugadores,
            "enemigo": enemigo,
            "tablero": tablero_enemigo,
            "celdas": tablero_enemigo.celdas,
        },
    )


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_turno
@requiere_haber_atacado
@requiere_partida_no_terminada
def defensa(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista que maneja las defensas.
    Muestra al jugador su propio tablero y le permite elegir la defensa
    y la ubicacion para su defensa.
    Si vienen datos post, realiza la defensa, avanza el turno y lleva al
    jugador a la vista de esperar turno.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    mijugador = get_object_or_404(p.jugador_set, usuario=request.user)
    error = ""
    if request.method == "POST":  # me fijo si vienen datos
        form = DefensaForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data["tipo"]
            hacia_proa = form.cleaned_data["hacia_proa"]
            x = form.cleaned_data["x"]
            y = form.cleaned_data["y"]
            try:
                if not tipo == "SD":
                    if tipo == "E":
                        mijugador.tablero.poner_escudo((x, y))
                    else:
                        barco = mijugador.tablero.devolver_barco((x, y))
                        if tipo == "MC":
                            mijugador.tablero.movimiento_corto(barco, hacia_proa)

                        elif tipo == "ML":
                            mijugador.tablero.movimiento_largo(barco, hacia_proa)

                        elif tipo == "SS":
                            barco.sumergimiento()

            except BarcoTocado:
                error = "El barco está dañado, elija otro barco"
            except BarcoMalUbicado:
                error = "El movimiento coloca al barco en posicion invalida"
            except SubmarinoSinMovimiento:
                error = "El submarino esta sumergido y no puede desplazarse"
            except NoTieneMovimientoLargo:
                error = "El barco seleccionado no tiene movimiento largo"
            except EscudoFueraDeTablero:
                error = "El escudo excede el tablero"
            except EscudoYaUsado:
                error = "No han pasado 4 rondas desde el ultimo escudo"
            except BarcoNoSumergible:
                error = "El barco elegido no es un submarino"
            except SumergidoTresVeces:
                error = "El submarino ha superado el limite de sumergimientos"
            except NoHayBarco:
                error = "En esa posicion no hay barco"

            if error:
                return render(
                    request,
                    "defender.html",
                    {
                        "form": form,
                        "usuario": request.user,
                        "error": error,
                        "partida": p,
                        "tablero": mijugador.tablero,
                        "celdas": mijugador.tablero.celdas,
                    },
                )
            p.avanzar_turno()
            return HttpResponseRedirect(reverse("esperando_turno", args=(p.id,)))
    else:
        form = DefensaForm()
    return render(
        request,
        "defender.html",
        {
            "form": form,
            "usuario": request.user,
            "error": error,
            "partida": p,
            "tablero": mijugador.tablero,
            "celdas": mijugador.tablero.celdas,
        },
    )


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_partida_no_terminada
def ganador(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista para informar al ganador de la partida
    """
    p = get_object_or_404(Partida, pk=partida_id)
    usuario = request.user
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    aciertos, celdas_mias_tocadas = jugador.puntos()
    no_derrotados = p.jugador_set.exclude(derrotado=True)
    if no_derrotados.count() == 1 and jugador in no_derrotados:
        p.terminada = True
        p.save()
        return render(
            request,
            "ganador.html",
            {
                "usuario": usuario,
                "partida": p,
                "aciertos": aciertos,
                "celdas_tocadas": celdas_mias_tocadas,
            },
        )
    return HttpResponseRedirect(reverse("esperando_turno", args=(p.id,)))


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_partida_no_terminada
def derrotado(
    request: HttpRequest, partida_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Vista para informar al jugador que ha sido derrotado.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    usuario = request.user
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    aciertos, celdas_mias_tocadas = jugador.puntos()
    if jugador.derrotado:
        return render(
            request,
            "derrotado.html",
            {
                "usuario": usuario,
                "partida": p,
                "aciertos": aciertos,
                "celdas_tocadas": celdas_mias_tocadas,
            },
        )
    return HttpResponseRedirect(reverse("esperando_turno", args=(p.id,)))


@login_required
@requiere_que_la_partida_exista
@requiere_partida_iniciada
@requiere_turno
@requiere_partida_no_terminada
def rendirse(request: HttpRequest, partida_id: int) -> HttpResponseRedirect:
    """
    Vista para rendirse durante una partida ya iniciada.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    p.avanzar_turno()
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    jugador.derrotado = True
    jugador.save()
    return HttpResponseRedirect(reverse("menu_principal"))


@login_required
@requiere_que_la_partida_exista
@requiere_partida_terminada
def resultados(request: HttpRequest, partida_id: int) -> HttpResponse:
    """
    Vista para mostrar los resultados de una partida.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    usuario = request.user
    ganador_jugador = get_object_or_404(p.jugador_set, derrotado=False)
    perdedores = p.jugador_set.filter(derrotado=True)

    return render(
        request,
        "resultados.html",
        {
            "usuario": usuario,
            "partida": p,
            "ganador": ganador_jugador,
            "perdedores": perdedores,
        },
    )  # 'ganador' en contexto para el template


@login_required
@requiere_que_la_partida_exista
@requiere_partida_no_terminada
def abandonar(request: HttpRequest, partida_id: int) -> HttpResponseRedirect:
    """
    Vista para abandonar una partida antes de que se inicie.
    """
    p = get_object_or_404(Partida, pk=partida_id)
    usuario = request.user
    jugador = get_object_or_404(p.jugador_set, usuario=request.user)
    if p.iniciada:
        return HttpResponseRedirect(reverse("rendirse", args=(p.id,)))
    jugador.delete()
    if len(p.jugador_set.exclude(usuario=usuario)) == 0:
        p.delete()
    return HttpResponseRedirect(reverse("menu_principal"))
