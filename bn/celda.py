#!/usr/bin/env python

from __future__ import annotations

from django.template.loader import render_to_string


class Celda:
    """
    Clase que representa una celda del tablero.
    """

    def __init__(
        self,
        x: int,
        y: int,
        barco: tuple[str, int, bool] | None = None,
        hay_barco: bool = False,
        hay_disparo: bool = False,
        hundido: bool = False,
        hay_escudo: bool = False,
        hay_radar: bool = False,
        sumergido: bool = False,
        tocada: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.hay_barco = hay_barco
        self.hundido = hundido
        self.hay_escudo = hay_escudo
        self.hay_radar = hay_radar
        self.sumergido = sumergido
        self.tocada = tocada
        if hay_barco and barco is not None:
            self.tipo_barco, self.seccion_barco, self.horizontal = barco
        else:
            self.tipo_barco = ""
            self.seccion_barco = 0
            self.horizontal = True
        self.hay_disparo = hay_disparo

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Celda):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    @property
    def texto(self) -> str:
        """
        Devuelve un texto para la renderizacion de la celda.
        """
        result = ""
        if self.hay_escudo:
            result += "X"
        if self.hay_radar:
            result += "R"
        if self.hay_barco:
            result = result + "B"
        if self.sumergido:
            result = result + "_"
        if self.tocada and not self.hundido:
            result = result + "*"
        if self.hay_disparo and not self.tocada:
            result = result + "#"
        if self.hundido:
            result = result + "+"
        return result

    @property
    def render(self) -> str:
        """
        Devuelve la renderizacion en html de la celda usando un template
        especifico.
        """
        imagenes: list[str] = []
        if self.hay_barco:
            path = "images/" + self.tipo_barco[:3].lower()
            path += str(self.seccion_barco)
            if self.horizontal:
                path += "h"
            else:
                path += "v"
        else:
            path = "images/agua"
        imagenes.append(path + ".png")

        if self.hay_radar:
            path = "images/radar"
            imagenes.append(path + ".png")

        if self.sumergido:
            path = "images/sumergido"
            imagenes.append(path + ".png")

        if self.hay_escudo and not self.hay_barco:
            path = "images/escudo"
            imagenes.append(path + ".png")

        if self.tocada and not self.hundido:
            path = "images/tocado"
            imagenes.append(path + ".png")

        if self.hay_disparo and not self.tocada:
            path = "images/disparo"
            imagenes.append(path + ".png")

        if self.hundido:
            path = "images/hundido"
            imagenes.append(path + ".png")

        if self.hay_escudo and self.hay_barco:
            path = "images/escudo_p"
            imagenes.append(path + ".png")
        return render_to_string("celda.html", {"imagenes": imagenes})

    def __str__(self) -> str:
        return "Celda en " + str(self.x) + "," + str(self.y)

    def es_vecino(self, other: Celda) -> bool:
        """
        Devuelve true si la celda se toca con otra que venga en other.
        """
        a = abs(self.x - other.x)
        b = abs(self.y - other.y)
        return a <= 1 and b <= 1
