#!/usr/bin/env python

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bn.models import Jugador


class BarcoMalUbicado(Exception):
    def __str__(self) -> str:
        return "Barco Mal Ubicado"


class SubmarinoSumergido(Exception):
    def __str__(self) -> str:
        return "El submarino a atacar esta sumergido"


class NoTieneMovimientoLargo(Exception):
    def __str__(self) -> str:
        return "El barco seleccionado no posee movimiento largo"


class RadarUsado2VecesContra(Exception):
    def __init__(self, desde: Jugador, contra: Jugador) -> None:
        self.desde = desde
        self.contra = contra

    def __str__(self) -> str:
        return f"{self.desde} uso dos veces el radar en {self.contra}"


class NoPuedeAtaquePotente(Exception):
    def __str__(self) -> str:
        return "No cumple las condiciones para hacer un ataque potente."


class AtaqueFueraDelTablero(Exception):
    def __str__(self) -> str:
        return "Ataque fuera del tablero"


class BarcoTocado(Exception):
    def __str__(self) -> str:
        return "El barco está dañado, no puede realizar defensa"


class EscudoFueraDeTablero(Exception):
    def __str__(self) -> str:
        return "El escudo excede el tablero"


class SumergidoTresVeces(Exception):
    def __str__(self) -> str:
        return "El submarino ha superado el limite de sumergimientos"


class BarcoNoSumergible(Exception):
    def __str__(self) -> str:
        return "El barco elegido no se puede sumergir"


class SubmarinoSinMovimiento(Exception):
    def __str__(self) -> str:
        return "El submarino sumergido no puede desplazarse"


class NoHayBarco(Exception):
    def __str__(self) -> str:
        return "En esa posicion no hay barco"


class EscudoYaUsado(Exception):
    def __str__(self) -> str:
        return "El escudo ha sido usado en las ultimas 4 rondas"
