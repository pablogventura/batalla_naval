#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.template.loader import render_to_string

class Celda(object):
    """
    Clase que para representar una celda del tablero.
    """
    def __init__(self, x, y, barco=None, hay_barco=False, hay_disparo=False,
                 hundido=False, hay_escudo=False, hay_radar=False,
                 sumergido=False, tocada=False):
        self.x = x
        self.y = y
        self.hay_barco = hay_barco
        self.hundido = hundido
        self.hay_escudo = hay_escudo
        self.hay_radar = hay_radar
        self.sumergido = sumergido
        self.tocada = tocada
        if hay_barco:
            self.tipo_barco, self.seccion_barco, self.horizontal = barco
        self.hay_disparo = hay_disparo

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    @property
    def texto(self):
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
    def render(self):
        """
        Devuelve la renderizacion en html de la celda usando un template
        especifico.
        """
        imagenes = []
        if self.hay_barco:
            path = 'images/' + self.tipo_barco[:3].lower()
            path += str(self.seccion_barco)
            if self.horizontal:
                path += 'h'
            else:
                path += 'v'
        else:
            path = 'images/agua'
        imagenes.append(path + ".png")
        
        if self.hay_radar:
            path = 'images/radar'
            imagenes.append(path + ".png")
            
        if self.sumergido:
            path = 'images/sumergido'
            imagenes.append(path + ".png")
            
        if self.hay_escudo and not self.hay_barco:
            path = 'images/escudo' # escudo opaco
            imagenes.append(path + ".png")
            
        if self.tocada and not self.hundido:
            path = 'images/tocado'
            imagenes.append(path + ".png")
            
        if self.hay_disparo and not self.tocada:
            path = 'images/disparo'
            imagenes.append(path + ".png")
            
        if self.hundido:
            path = 'images/hundido'
            imagenes.append(path + ".png")

        if self.hay_escudo and self.hay_barco:
            path = 'images/escudo_p' # escudo semitransparente
            imagenes.append(path + ".png")
        return render_to_string('celda.html',{'imagenes': imagenes})

    def __str__(self):
        return self.__unicode__()

    def es_vecino(self, other):
        """
        Devuelve true si la celda se toca con otra que venga en other.
        """
        a = abs(self.x - other.x)
        b = abs(self.y - other.y)
        return a <= 1 and b <= 1

    def __cmp__(self, other):
        s = (self.x, self.y)
        o = (other.x, other.y)
        if s > o:
            return 1
        elif s == o:
            return 0
        else:
            return - 1

    def __unicode__(self):
        return u"Celda en " + str(self.x) + "," + str(self.y)
