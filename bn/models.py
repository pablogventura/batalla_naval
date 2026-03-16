#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from . import fields
from .celda import Celda
from .excepciones import *

CELDAS_SUBMARINO = 3
CELDAS_PORTAAVIONES = 5
CELDAS_FRAGATA = 3
CELDAS_PATRULLA = 2
CELDAS_ACORAZADO = 4


class Partida(models.Model):
    """
    Modelo que representa a una partida.
    """
    nombre = models.CharField(
        default='Nombre de la Partida', max_length=200)
    cant_jugadores = models.PositiveIntegerField(default=2)
    cant_acorazados = models.PositiveIntegerField(default=1)
    cant_patrullas = models.PositiveIntegerField(default=1)
    cant_portaaviones = models.PositiveIntegerField(default=1)
    cant_submarinos = models.PositiveIntegerField(default=1)
    cant_fragatas = models.PositiveIntegerField(default=1)
    cant_turnos_totales = models.PositiveIntegerField(default=0)
    cant_turnos_de_la_ronda = models.PositiveIntegerField(default=0)
    ancho_tablero = models.PositiveIntegerField(default=9)
    numero_ronda_actual = models.PositiveIntegerField(default=0)
    iniciada = models.BooleanField(default=False)
    terminada = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jugador_actual = None
        if self.pk is not None:
            try:
                self.jugador_actual = self.jugador_set.get(es_su_turno=True)
            except ObjectDoesNotExist:
                pass

    def debe_iniciarse(self):
        """
        Devuelve un booleano que indica que la partida esta en condiciones
        de iniciarse.
        """
        if self.iniciada:
            return False
        if self.cant_jugadores > self.jugador_set.count():
            return False
        elif self.cant_jugadores == self.jugador_set.count():
            for j in self.jugador_set.all():
                if not j.ubicaciones_confirmadas:
                    return False
            return True

    def iniciar(self):
        """
        Inicia la partida y da el primer turno.
        """
        assert self.debe_iniciarse()
        self.iniciada = True
        for i in self.jugador_set.all():
            for j in self.jugador_set.all():
                if i != j:
                    t = TableroVisible(jugador_atacante=i,
                                       tablero_atacado=j.tablero)
                    t.save()

        self.jugador_actual = self.jugador_set.all(
        ).order_by('usuario__username', 'color')[0]
        self.jugador_actual.es_su_turno = True
        self.jugador_actual.ya_ataco = False
        self.jugador_actual.save()
        self.cant_turnos_totales = 1
        self.cant_turnos_de_la_ronda = 1
        self.numero_ronda_actual = 1
        self.save()

    def agregar_jugador(self, usuario):
        """
        Agrega un jugador a la partida.
        """
        self.jugador_set.create(usuario=usuario, color=None, es_su_turno=False,
                                tablero=None, ubicaciones_confirmadas=False)

    def eliminar_jugador(self, jugador):
        # las vistas ya nos dan el jugador entero
        jugador.delete()

    def avanzar_turno(self):
        """
        Avanza el turno, y aumenta el contador de rondas y el contador de
        turnos.
        """
        self.jugador_actual.es_su_turno = False
        self.jugador_actual.save()

        #doble guion bajo va a los atributos del foregin key
        jugadores = list(
            self.jugador_set.filter(derrotado=False).order_by('usuario__username', 'color'))

        # buscar el jugador actual en la lista y elegir el siguiente?
        jugador_siguiente = jugadores[(jugadores.index(
            self.jugador_actual) + 1) % len(jugadores)]

        jugador_siguiente.es_su_turno = True
        jugador_siguiente.ya_ataco = False
        jugador_siguiente.save()

        self.jugador_actual = jugador_siguiente
        turnos = self.cant_turnos_de_la_ronda
        if turnos / self.jugador_set.exclude(derrotado=True).count() == 1:
            # para poder avanzar de ronda
            self.cant_turnos_de_la_ronda = 0
            self.numero_ronda_actual += 1

        self.cant_turnos_totales = self.cant_turnos_totales + 1
        self.cant_turnos_de_la_ronda += 1
        self.save()

    def __str__(self):
        return self.nombre


class Jugador(models.Model):
    """
    Modelo que representa a un jugador, de un usuario, para alguna partida.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    color = models.PositiveIntegerField(default=0)
    es_su_turno = models.BooleanField(
        default=False)  # preguntar si hay que guardarlo en la base de datos
    ya_ataco = models.BooleanField(
        default=False)  # guarda si en su turno el jugador ya ataco
    ubicaciones_confirmadas = models.BooleanField(default=False)
    derrotado = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username

    def puntos(self):
        """
        Devuelve una tupla con la cantidad de celdas enemigas atacadas y las
        celdas propias atacadas.
        """
        celdas_tocadas_por_mi = 0
        celdas_mias_tocadas = 0
        for t in self.tableros_visibles.all():
            celdas_tocadas_por_mi += len(t.puntos_atacados)
        for i in self.tablero.acorazado_set.all():
            celdas_mias_tocadas += len(i.puntos_tocados)
        for i in self.tablero.patrulla_set.all():
            celdas_mias_tocadas += len(i.puntos_tocados)
        for i in self.tablero.portaaviones_set.all():
            celdas_mias_tocadas += len(i.puntos_tocados)
        for i in self.tablero.submarino_set.all():
            celdas_mias_tocadas += len(i.puntos_tocados)
        for i in self.tablero.fragata_set.all():
            celdas_mias_tocadas += len(i.puntos_tocados)

        return (celdas_tocadas_por_mi, celdas_mias_tocadas)


class Tablero(models.Model):
    """
    Modelo que representa a un tablero de un jugador.
    """
    ancho = models.PositiveIntegerField()
    cant_acorazados = models.PositiveIntegerField()
    cant_patrullas = models.PositiveIntegerField()
    cant_portaaviones = models.PositiveIntegerField()
    cant_submarinos = models.PositiveIntegerField()
    cant_fragatas = models.PositiveIntegerField()
    hay_escudo = models.BooleanField(default=False)
    posicion_escudo = fields.TupleField(blank=True, null=True)
    # en vez de veces_radar va radar en jugador
    ronda_ultimo_escudo = models.IntegerField(
        default=-4)  # para que pueda al principio
    jugador = models.OneToOneField(Jugador, on_delete=models.CASCADE)

    @property
    def lista_alto(self):
        """
        Devuelve una lista de numeros correspondiente al alto. Sirve para
        renderizar el tablero.
        """
        return [" "] + list(range(1, self.ancho + 1))

    @property
    def lista_ancho(self):
        """
        Devuelve una lista de letras correspondiente al ancho. Sirve para
        renderizar
        """
        return [chr(64 + x) for x in range(1, self.ancho + 1)]

    @property
    def celdas(self):
        """
        Devuelve un diccionario de Celda, donde la clave (x,y) lleva a la celda
        ubicada en x,y.
        """
        tiros_agua = []
        tiros_escudo = []
        for t in self.visibles.all():
            tiros_agua += t.tiros_agua
            tiros_escudo += t.tiros_escudo
        result = {}
        for y in range(self.ancho):
            for x in range(self.ancho):
                result[(x, y)] = Celda(x, y)
                if self._en_escudo((x, y)):
                    result[(x, y)].hay_escudo = True
        for i in self.acorazado_set.all():
            c = i.celdas()
            for j in c.keys():
                result[j] = c[j]
                if self._en_escudo(j):
                    result[j].hay_escudo = True
        for i in self.patrulla_set.all():
            c = i.celdas()
            for j in c.keys():
                result[j] = c[j]
                if self._en_escudo(j):
                    result[j].hay_escudo = True
        for i in self.portaaviones_set.all():
            c = i.celdas()
            for j in c.keys():
                result[j] = c[j]
                if self._en_escudo(j):
                    result[j].hay_escudo = True
        for i in self.submarino_set.all():
            c = i.celdas()
            for j in c.keys():
                result[j] = c[j]
                if self._en_escudo(j):
                    result[j].hay_escudo = True
        for i in self.fragata_set.all():
            c = i.celdas()
            for j in c.keys():
                result[j] = c[j]
                if self._en_escudo(j):
                    result[j].hay_escudo = True
        for (x, y) in result.keys():
            if (x, y) in tiros_agua:
                result[(x, y)].hay_disparo = True
            if (x, y) in tiros_escudo:
                result[(x, y)].hay_disparo = True
        return result

    def crear_barcos(self):
        """
        Crea los barcos segun lo establecido.
        """
        assert not self.acorazado_set.all().exists()
        assert not self.fragata_set.all().exists()
        assert not self.patrulla_set.all().exists()
        assert not self.portaaviones_set.all().exists()
        assert not self.submarino_set.all().exists()

        for i in range(self.cant_acorazados):
            self.acorazado_set.create()
        for i in range(self.cant_fragatas):
            self.fragata_set.create()
        for i in range(self.cant_patrullas):
            self.patrulla_set.create()
        for i in range(self.cant_portaaviones):
            self.portaaviones_set.create()
        for i in range(self.cant_submarinos):
            self.submarino_set.create()

    def barco_sin_ubicar(self):
        """
        Devuelve un barco sin ubicar para la vista de ubicacion de barcos.
        """
        b = self.acorazado_set.filter(x=None)
        if len(b):
            return b[0]
        b = self.fragata_set.filter(x=None)
        if len(b):
            return b[0]
        b = self.portaaviones_set.filter(x=None)
        if len(b):
            return b[0]
        b = self.patrulla_set.filter(x=None)
        if len(b):
            return b[0]
        b = self.submarino_set.filter(x=None)
        if len(b):
            return b[0]
        return None

    def _en_escudo(self, posicion):
        """
        Devuelve un booleano indicando si la tupla en posicion esta dentro del
        escudo.
        """
        if self.hay_escudo:
            x, y = posicion
            xe, ye = self.posicion_escudo
            return max(abs(x - xe), abs(y - ye)) <= 1
        return False

    def ataque_normal(self, posicion):
        """
        Devuelve un diccionario de una unica celda, con el efecto de haber
        hecho un ataque normal en posicion.
        """
        x, y = posicion
        if not (0 <= x < self.ancho and 0 <= y < self.ancho):
            raise AtaqueFueraDelTablero()
        if not self._en_escudo(posicion):
            for barco in self.acorazado_set.all():
                if barco.estoy_en(posicion):
                    barco.tocar(posicion)
            for barco in self.patrulla_set.all():
                if barco.estoy_en(posicion):
                    barco.tocar(posicion)
            for barco in self.portaaviones_set.all():
                if barco.estoy_en(posicion):
                    barco.tocar(posicion)
            for barco in self.submarino_set.all():
                if barco.estoy_en(posicion):
                    barco.tocar(posicion)
            for barco in self.fragata_set.all():
                if barco.estoy_en(posicion):
                    barco.tocar(posicion)
            if self.cant_barcos_sin_hundir() == 0:
                self.jugador.derrotado = True
                self.jugador.save()
            return {posicion: self.celdas[posicion]}
        else:
            return {posicion: Celda(x, y, hay_escudo=True)}

    def ataque_radar(self, posicion):
        """
        Devuelve un diccionario de celdas con el resultado de haber hecho un
        ataque de radar de 3x3 donde posicion es el centro.
        """
        x, y = posicion
        if not (1 <= x < self.ancho - 1 and 1 <= y < self.ancho - 1):
            raise AtaqueFueraDelTablero()
        result = {}
        for yi in range(y - 1, y + 2):
            for xi in range(x - 1, x + 2):
                posi = (xi, yi)
                result[posi] = self.celdas[posi]
                if result[posi].sumergido:
                    result[posi] = Celda(xi, yi)  # muestro agua nomas
                result[posi].hay_radar = True
        return result

    def ataque_potente(self, posicion):
        """
        Devuelve un diccionario de celdas con el resultado de haber hecho un
        ataque potente de 2x2 donde posicion es el extremo superior derecho.
        """
        x, y = posicion
        result = {}
        if not (0 <= x < self.ancho - 1 and 0 <= y < self.ancho - 1):
            raise AtaqueFueraDelTablero()

        for yi in range(y, y + 2):
            for xi in range(x, x + 2):
                posi = (xi, yi)
                if not self._en_escudo(posi):
                    for barco in self.acorazado_set.all():
                        if barco.estoy_en(posi):
                            barco.tocar(posi)
                    for barco in self.patrulla_set.all():
                        if barco.estoy_en(posi):
                            barco.tocar(posi)
                    for barco in self.portaaviones_set.all():
                        if barco.estoy_en(posi):
                            barco.tocar(posi)
                    for barco in self.submarino_set.all():
                        if barco.estoy_en(posi):
                            barco.tocar(posi)
                    for barco in self.fragata_set.all():
                        if barco.estoy_en(posi):
                            barco.tocar(posi)
                    result[posi] = self.celdas[posi]
                else:
                    result[posi] = Celda(xi, yi, hay_escudo=True)
        if self.cant_barcos_sin_hundir() == 0:
            self.jugador.derrotado = True
            self.jugador.save()
        return result

    def radar_usado_dos_veces(self, jugador_enemigo):
        """
        Devuelve un booleano indicando si se puede usar el radar contra
        jugador_enemigo.
        """
        return len(self.jugador.radar.filter(contra=jugador_enemigo)) == 2

    def cant_barcos_sin_hundir(self):
        """
        Devuelve la candidad de barcos que no han sido hundidos.
        """
        result = self.acorazado_set.filter(hundido=False).count()
        result += self.patrulla_set.filter(hundido=False).count()
        result += self.submarino_set.filter(hundido=False).count()
        result += self.fragata_set.filter(hundido=False).count()
        result += self.portaaviones_set.filter(hundido=False).count()
        return result

    def movimiento_corto(self, barco, hacia_proa):
        """
        Realiza un movimiento corto en barco. Si hacia proa es True, el barco
        se mueve para arriba o para la izquierda dependiendo si esta vertical o
        horizontal, y a la inversa si es False.
        """
        barco.mover(1, hacia_proa)

    def movimiento_largo(self, barco, hacia_proa):
        """
        Realiza un movimiento largo en barco. Si hacia proa es True, el barco
        se mueve para arriba o para la izquierda dependiendo si esta vertical o
        horizontal, y a la inversa si es False.
        """
        if barco.tiene_mov_largo():
            barco.mover(2, hacia_proa)
        else:
            raise NoTieneMovimientoLargo()

    def poner_escudo(self, posicion):
        """
        Coloca el escudo en posicion.
        """
        assert not self.hay_escudo
        if not self.lleva_4_turnos_sin_escudo():
            raise EscudoYaUsado()
        #import pdb; pdb.set_trace()
        x, y = posicion
        if not (1 <= x < self.ancho - 1 and 1 <= y < self.ancho - 1):
            raise EscudoFueraDeTablero()
        self.hay_escudo = True
        self.posicion_escudo = posicion
        self.ronda_ultimo_escudo = self.jugador.partida.numero_ronda_actual
        self.save()
        
    def sacar_escudo(self):
        """
        Saca el escudo.
        """
        if self.hay_escudo:
            self.hay_escudo = False
            self.save()

    def lleva_4_turnos_sin_escudo(self):
        """
        Comprueba que se pueda hacer un escudo
        """
        ronda_actual = self.jugador.partida.numero_ronda_actual
        return ronda_actual - self.ronda_ultimo_escudo > 4

    def emerger_submarino(self):
        """
        Hace emerger a todos los submarinos.
        """
        for i in self.submarino_set.all():
            if i.esta_sumergido:
                i.esta_sumergido = False
                i.save()

    def __str__(self):
        return "Tablero de " + self.jugador.usuario.username

    def devolver_barco(self, posicion):
        """
        Devuelve el barco que encuentre en posicion.
        """
        barco = None
        x, y = posicion
        for i in self.acorazado_set.all():
            if i.estoy_en((x, y)):
                barco = i
        for i in self.patrulla_set.all():
            if i.estoy_en((x, y)):
                barco = i
        for i in self.portaaviones_set.all():
            if i.estoy_en((x, y)):
                barco = i
        for i in self.submarino_set.all():
            if i.estoy_en((x, y)):
                barco = i
        for i in self.fragata_set.all():
            if i.estoy_en((x, y)):
                barco = i

        if barco is None:
            raise NoHayBarco()
        return barco


class Radar(models.Model):
    """
    Modelo que representa el haber hecho un ataque de radar.
    Sirve para llevar la cuenta de los radares y cumplir el maximo de radares.
    """
    desde = models.ForeignKey('Jugador', related_name='radar', on_delete=models.CASCADE)
    contra = models.ForeignKey('Jugador', related_name='radar_contra_mi', on_delete=models.CASCADE)


class Barco(models.Model):
    """
    Modelo abstracto que sirve para dar los atributos y metodos generales
    de los barcos.
    """
    # x,y definen la posicion de la proa del barco
    x = models.PositiveIntegerField(blank=True, null=True)
    y = models.PositiveIntegerField(blank=True, null=True)
    horizontal = models.BooleanField(default=True)
    hundido = models.BooleanField(default=False)
    puntos_tocados = fields.ListField(blank=True, null=True)
    tablero = models.ForeignKey(Tablero, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def tocar(self, posicion):
        """
        Agrega el punto en posicion como un punto tocado. Posicion es una tupla
        (x,y) de ubicacion absoluta en el tablero.
        """
        assert self.estoy_en(posicion)
        x, y = posicion
        if self.horizontal:
            self.puntos_tocados.append(x - self.x)
        else:
            self.puntos_tocados.append(y - self.y)
        if set(self.puntos_tocados) == set(range(self.cant_celdas)):
            self.hundido = True
        self.save()

    def estoy_bien_ubicado(self):
        """
        Devuelve un booleano que dice si el barco cumple con las reglas de
        ubicacion.
        """
        return self._no_excedo_tablero() and not self._hay_barcos()

    def _no_excedo_tablero(self):
        """
        Devuelve un booleano diciendo si el barco excede el tablero.
        """
        if self.x < 0 or self.y < 0:
            return False
        if self.horizontal:
            ultima = self.x + self.cant_celdas
            return ultima <= self.tablero.ancho and self.y < self.tablero.ancho
        else:
            ultima = self.y + self.cant_celdas
            return ultima <= self.tablero.ancho and self.x < self.tablero.ancho

    def _hay_barcos(self):
        """
        Devuelve un booleano diciendo si el barco esta superpuesto a otro, o si
        hay algun barco que lo toque.
        """
        result = False
        t = self.tablero
        for cb in self.celdas().values():
            for barco in t.acorazado_set.all():
                if self != barco:
                    for celda in barco.celdas().values():
                        if cb.es_vecino(celda):
                            result = result or celda.hay_barco
            for barco in t.fragata_set.all():
                if self != barco:
                    for celda in barco.celdas().values():
                        if cb.es_vecino(celda):
                            result = result or celda.hay_barco
            for barco in t.portaaviones_set.all():
                if self != barco:
                    for celda in barco.celdas().values():
                        if cb.es_vecino(celda):
                            result = result or celda.hay_barco
            for barco in t.patrulla_set.all():
                if self != barco:
                    for celda in barco.celdas().values():
                        if cb.es_vecino(celda):
                            result = result or celda.hay_barco
            for barco in t.submarino_set.all():
                if self != barco:
                    for celda in barco.celdas().values():
                        if cb.es_vecino(celda):
                            result = result or celda.hay_barco
        return result

    def celdas(self):
        """
        Devuelve un diccionario de celdas indexado con tuplas de posciones en
        el tablero, con todas las secciones y estados del barco.
        """
        if self.x is None or self.y is None:
            return {}  # el barco no esta ubicado
        result = {}
        x = self.x
        y = self.y
        for i in range(self.cant_celdas):
            tipo_barco = type(self).__name__

            tocada = i in self.puntos_tocados
            sumergido = type(self) == Submarino and self.esta_sumergido

            c = Celda(x, y, (tipo_barco, i, self.horizontal), True,
                      False, self.hundido,
                      sumergido=sumergido, tocada=tocada)
            result[(x, y)] = c
            if self.horizontal:
                x = x + 1
            else:
                y = y + 1
        return result

    def estoy_en(self, posicion):
        """
        Devuelve true si alguna seccion del barco esta en posicion.
        """
        x, y = posicion
        if self.horizontal:
            ultima = self.x + self.cant_celdas
            return self.y == y and x in range(self.x, ultima)
        else:
            ultima = self.y + self.cant_celdas
            return self.x == x and y in range(self.y, ultima)

    def mover(self, cantidad, hacia_proa):
        """
        Mueve el barco cantidad de celdas, con hacia proa en true el barco se
        mueve hacia arriba o a la izquierda dependiendo si esta vertical, o
        horizontal.

        El punto (0,0) del tablero es arriba a la izquierda.
        Los barcos horizontales siempre tienen la proa a la izquierda.
        Los barcos verticales seimpre tienen la proa hacia arriba.
        """
        if len(self.puntos_tocados) > 0:
            raise BarcoTocado()
        if type(self) == Submarino:
            if self.esta_sumergido:
                raise SubmarinoSinMovimiento
        if self.horizontal:
            if hacia_proa:
                self.x = self.x - cantidad
            else:
                self.x = self.x + cantidad
        else:
            if hacia_proa:
                self.y = self.y - cantidad
            else:
                self.y = self.y + cantidad
        if self.estoy_bien_ubicado():
            self.save()
        else:
            raise BarcoMalUbicado()

    def tiene_mov_largo(self):
        """
        Devuelve un booleano que determina si el barco puede hacer un
        movimiento largo.
        """
        if self.tablero.lleva_4_turnos_sin_escudo():
            if type(self) in [Fragata, Patrulla]:
                return True
            elif type(self) == Submarino:
                return not self.esta_sumergido
        return False

    def sumergimiento(self):
        """
        Metodo para sobreescribir, hace que todos los barcos que no son
        submarinos den una excepcion al intentar sumergirse.
        """
        if type(self) != Submarino:
            raise BarcoNoSumergible()


class Acorazado(Barco):
    """
    Modelo que hereda de Barco, para representar al Acorazado.
    """
    ronda_ultimo_ataque_potente = models.IntegerField(
        default=-3)  # para que pueda al principio

    def __init__(self, *args, **kwargs):
        super(Acorazado, self).__init__(*args, **kwargs)
        self.cant_celdas = CELDAS_ACORAZADO

    def lleva_2_turnos_sin_potente(self):
        """
        Devuelve un booleano que dice si el acorazado lleva dos turnos
        completos sin usar el ataque potente.
        """
        # 3 turnos del potente, porque durante 2 turnos no pudo ser usado
        ronda_actual = self.tablero.jugador.partida.numero_ronda_actual
        return ronda_actual - self.ronda_ultimo_ataque_potente >= 3

    def __str__(self):
        return "Acorazado"


class Patrulla(Barco):
    """
    Modelo que hereda de Barco, para representar a la Patrulla.
    """
    def __init__(self, *args, **kwargs):
        super(Patrulla, self).__init__(*args, **kwargs)
        self.cant_celdas = CELDAS_PATRULLA

    def __str__(self):
        return "Patrulla"


class Portaaviones(Barco):
    """
    Modelo que hereda de Barco, para representar al Portaaviones.
    """
    def __init__(self, *args, **kwargs):
        super(Portaaviones, self).__init__(*args, **kwargs)
        self.cant_celdas = CELDAS_PORTAAVIONES

    def __str__(self):
        return "Portaaviones"


class Submarino(Barco):
    """
    Modelo que hereda de Barco, para representar al Submarino.
    """
    esta_sumergido = models.BooleanField(default=False)
    veces_sumergimiento = models.PositiveIntegerField(default=0)

    def __init__(self, *args, **kwargs):
        super(Submarino, self).__init__(*args, **kwargs)
        self.cant_celdas = CELDAS_SUBMARINO

    def tocar(self, posicion):
        """
        Metodo sobreescrito, toca al submarino solo si no esta sumergido.
        """
        assert self.estoy_en(posicion)
        if not self.esta_sumergido:
            super(Submarino, self).tocar(posicion)

    def sumergimiento(self):
        """
        Metodo sobreescrito.
        Realiza el sumergimiento.
        """
        if len(self.puntos_tocados) == 0:
            if self.sumergido_tres_veces():
                raise SumergidoTresVeces()
            self.esta_sumergido = True
            self.veces_sumergimiento += 1
            self.save()
        else:
            raise BarcoTocado()

    def sumergido_tres_veces(self):
        """
        Devuelve un booleano que informa si el submarino ha sido sumergido
        tres veces.
        """
        return self.veces_sumergimiento == 3

    def __str__(self):
        return "Submarino"


class Fragata(Barco):
    """
    Modelo que hereda de Barco, para representar a la Fragata.
    """
    def __init__(self, *args, **kwargs):
        super(Fragata, self).__init__(*args, **kwargs)
        self.cant_celdas = CELDAS_FRAGATA

    def __str__(self):
        return "Fragata"


class TableroVisible(models.Model):
    """
    Modelo que representa la forma en que ve un jugador atacante al tablero
    atacado de un enemigo. Guarda los ataques anteriores y las zonas visibles
    para el atacante.
    """
    jugador_atacante = models.ForeignKey(
        Jugador, related_name='tableros_visibles', on_delete=models.CASCADE)
    tablero_atacado = models.ForeignKey(Tablero, related_name='visibles', on_delete=models.CASCADE)
    puntos_atacados = fields.ListField(blank=True, null=True)
    tiros_agua = fields.ListField(blank=True, null=True)
    tiros_escudo = fields.ListField(blank=True, null=True)
    hay_radar = models.BooleanField(default=False)
    posicion_radar = fields.TupleField(blank=True, null=True)
    turno_del_radar = models.IntegerField(blank=True, null=True)

    @property
    def ancho(self):
        """
        Equivalente al metodo de Tablero.
        """
        return self.tablero_atacado.ancho

    @property
    def lista_alto(self):
        """
        Equivalente al metodo de Tablero.
        """
        return self.tablero_atacado.lista_alto

    @property
    def lista_ancho(self):
        """
        Equivalente al metodo de Tablero.
        """
        return self.tablero_atacado.lista_ancho

    def _guardar_resultados_ataque(self, celdas):
        """
        Procesa los resultados de un ataque que llegan en forma de un
        diccionario de celdas.
        """
        for celda in celdas.keys():
            if celda in self.tiros_agua:
                self.tiros_agua.remove(celda)
            if celda in self.tiros_escudo:
                self.tiros_escudo.remove(celda)

            if celdas[celda].hay_barco and not celdas[celda].sumergido:
                # para que no te muestre un submarino sumergido
                self.puntos_atacados.append(celda)
            elif celdas[celda].hay_escudo:
                self.tiros_escudo.append(celda)
            else:
                self.tiros_agua.append(celda)
        self.save()

    def ataque_normal(self, posicion):
        """
        Realiza el ataque normal.
        """
        celdas = self.tablero_atacado.ataque_normal(posicion)
        self._guardar_resultados_ataque(celdas)

    def _puede_ataque_potente(self):
        """
        Deterimina si el jugador esta en condiciones de realizar un ataque
        potente.
        """
        tablero_atacante = self.jugador_atacante.tablero
        if tablero_atacante.acorazado_set.filter(hundido=False).count() > 0:
            for a in tablero_atacante.acorazado_set.filter(hundido=False):
                if a.lleva_2_turnos_sin_potente():
                    return a
        return None

    def ataque_potente(self, posicion):
        """
        Realiza el ataque potente.
        """
        acorazado = self._puede_ataque_potente()
        if acorazado is None:
            raise NoPuedeAtaquePotente()
        celdas = self.tablero_atacado.ataque_potente(posicion)
        ronda_actual = self.jugador_atacante.partida.numero_ronda_actual
        acorazado.ronda_ultimo_ataque_potente = ronda_actual
        acorazado.save()
        self._guardar_resultados_ataque(celdas)

    def ataque_radar(self, posicion):
        """
        Realiza el ataque de radar.
        """
        x, y = posicion
        if not (1 <= x < self.ancho - 1 and 1 <= y < self.ancho - 1):
            raise AtaqueFueraDelTablero()
        enemigo = self.tablero_atacado.jugador
        if self.jugador_atacante.radar.filter(contra=enemigo).count() < 2:
            self.jugador_atacante.radar.create(
                contra=self.tablero_atacado.jugador)
            self.hay_radar = True
            self.posicion_radar = posicion
            turnos_totales = self.jugador_atacante.partida.cant_turnos_totales
            self.turno_del_radar = turnos_totales
        else:
            raise RadarUsado2VecesContra(
                self.jugador_atacante, self.tablero_atacado.jugador)

    @property
    def celdas(self):
        """
        Devuelve un diccionario de celdas con los estados de cada una.
        Se usa para renderizar.
        """
        result = {}
        celdas_totales = self.tablero_atacado.celdas
        for (x, y) in celdas_totales.keys():
            if (x, y) in self.puntos_atacados or celdas_totales[(x, y)].tocada:
                result[(x, y)] = celdas_totales[(x, y)]
                result[(x, y)].hay_escudo = False
                # para que si disparaste y despues el
                # tipo puso un escudo no lo veas.
            elif (x, y) in self.tiros_escudo:
                result[(x, y)] = Celda(x, y, hay_escudo=True, hay_disparo=True)
            elif (x, y) in self.tiros_agua:
                result[(x, y)] = Celda(x, y, hay_disparo=True)
            else:
                result[(x, y)] = Celda(x, y)

        turnos_totales = self.jugador_atacante.partida.cant_turnos_totales
        if self.hay_radar and self.turno_del_radar == turnos_totales:
            celdas_espiadas = self.tablero_atacado.ataque_radar(
                self.posicion_radar)
            for (x, y) in celdas_espiadas.keys():
                result[(x, y)] = celdas_espiadas[(x, y)]
        return result

    def __str__(self):
        return "Tablero de %s, segun %s" % (
            self.tablero_atacado.jugador, self.jugador_atacante)
