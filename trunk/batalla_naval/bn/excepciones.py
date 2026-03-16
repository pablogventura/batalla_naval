#!/usr/bin/env python
# -*- coding: utf8 -*-


class BarcoMalUbicado(Exception):
    def __str__(self):
        return "Barco Mal Ubicado"


class SubmarinoSumergido(Exception):
    def __str__(self):
        return "El submarino a atacar esta sumergido"


class NoTieneMovimientoLargo(Exception):
    def __str__(self):
        return "El barco seleccionado no posee movimiento largo"


class RadarUsado2VecesContra(Exception):
    def __init__(self, desde, contra):
        self.desde = desde
        self.contra = contra

    def __str__(self):
        return "%s uso dos veces el radar en %s" % (self.desde, self.contra)


class NoPuedeAtaquePotente(Exception):
    def __str__(self):
        return "No cumple las condiciones para hacer un ataque potente."


class AtaqueFueraDelTablero(Exception):
    def __str__(self):
        return "Ataque fuera del tablero"


class BarcoTocado(Exception):
    def __str__(self):
        return "El barco está dañado, no puede realizar defensa"


class EscudoFueraDeTablero(Exception):
    def __str__(self):
        return "El escudo excede el tablero"


class SumergidoTresVeces(Exception):
    def __str__(self):
        return "El submarino ha superado el limite de sumergimientos"


class BarcoNoSumergible(Exception):
    def __str__(self):
        return "El barco elegido no se puede sumergir"


class SubmarinoSinMovimiento(Exception):
    def __str__(self):
        return "El submarino sumergido no puede desplazarse"


class NoHayBarco(Exception):
    def __str__(self):
        return "En esa posicion no hay barco"


class EscudoYaUsado(Exception):
    def __str__(self):
        return "El escudo ha sido usado en las ultimas 4 rondas"
