#!/usr/bin/env python


from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from bn.models import *


class BNTestCase(TestCase):
    def crear_partida(self, nombre):
        partida = Partida(
            nombre=nombre,
            cant_jugadores=2,
            cant_acorazados=1,
            cant_patrullas=1,
            cant_portaaviones=1,
            cant_submarinos=1,
            cant_fragatas=1,
            cant_turnos_totales=0,
            cant_turnos_de_la_ronda=0,
            ancho_tablero=9,
            numero_ronda_actual=0,
            iniciada=False,
            terminada=False,
        )
        partida.save()
        return partida

    def crear_partida_corta(self, nombre, jugadores=2):
        partida = Partida(
            nombre=nombre,
            cant_jugadores=jugadores,
            cant_acorazados=0,
            cant_patrullas=1,
            cant_portaaviones=0,
            cant_submarinos=0,
            cant_fragatas=0,
            cant_turnos_totales=0,
            cant_turnos_de_la_ronda=0,
            ancho_tablero=9,
            numero_ronda_actual=0,
            iniciada=False,
            terminada=False,
        )
        partida.save()
        return partida

    def crear_jugador(self, usuario, partida):
        return partida.jugador_set.create(usuario=usuario)

    def crear_tablero(self, jugador):
        partida = jugador.partida
        jugador.tablero = Tablero(
            ancho=partida.ancho_tablero,
            cant_acorazados=partida.cant_acorazados,
            cant_patrullas=partida.cant_patrullas,
            cant_portaaviones=partida.cant_portaaviones,
            cant_submarinos=partida.cant_submarinos,
            cant_fragatas=partida.cant_fragatas,
        )
        jugador.tablero.save()
        return jugador.tablero

    def ubicar_barcos_predeterminadamente(self, tablero):
        j = 0
        barco = tablero.barco_sin_ubicar()
        while barco:
            barco.x = j
            j = j + 2
            barco.y = 0
            barco.horizontal = False
            barco.save()
            barco = tablero.barco_sin_ubicar()
        tablero.jugador.ubicaciones_confirmadas = True
        tablero.jugador.save()


class RegistroUsuario(BNTestCase):
    def test_registra_usuario(self):
        """
        Crea un usuario y comprueba que se le inicie sesion.
        """
        response = self.client.post(
            reverse("nuevo_usuario"),
            {
                "username": "test",
                "email": "test@test.com",
                "password1": "test",
                "password2": "test",
            },
        )
        self.assertEqual(User.objects.count(), 1)
        usuario = User.objects.get(pk=1)
        self.assertTrue(usuario.username == "test")
        self.assertRedirects(response, reverse("menu_principal"))


class InicioSesion(BNTestCase):
    def test_inicia_sesion(self):
        usuario = User.objects.create_user("test", "test@test.com", "test")
        response = self.client.post(
            reverse("login"),
            {
                "username": "test",
                "password": "test",
            },
        )

        self.assertTrue(usuario.username == "test")
        self.assertRedirects(response, reverse("menu_principal"))


class CrearPartida(BNTestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("test", "test@test.com", "test")

        self.client.login(username="test", password="test")

    def test_crea_partida(self):
        response = self.client.post(
            reverse("nueva_partida"),
            {
                "nombre": "PartidaTest",
                "cant_jugadores": 2,
                "cant_acorazados": 1,
                "cant_patrullas": 1,
                "cant_portaaviones": 1,
                "cant_submarinos": 1,
                "cant_fragatas": 1,
                "ancho_tablero": 9,
            },
        )

        self.assertEqual(Partida.objects.count(), 1)
        partida = Partida.objects.get(pk=1)
        self.assertTrue(partida.nombre == "PartidaTest")
        self.assertTrue(partida.cant_jugadores == 2)
        self.assertTrue(partida.cant_acorazados == 1)
        self.assertTrue(partida.cant_patrullas == 1)
        self.assertTrue(partida.cant_portaaviones == 1)
        self.assertTrue(partida.cant_submarinos == 1)
        self.assertTrue(partida.cant_fragatas == 1)
        self.assertTrue(partida.ancho_tablero == 9)

        self.assertTrue(partida.cant_turnos_totales == 0)
        self.assertTrue(partida.cant_turnos_de_la_ronda == 0)
        self.assertTrue(partida.numero_ronda_actual == 0)
        self.assertFalse(partida.iniciada)
        self.assertFalse(partida.terminada)

        self.assertRedirects(response, reverse("ubicar_barcos", args=(partida.id,)))


class UnirsePartida(BNTestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("test", "test@test.com", "test")

        self.client.login(username="test", password="test")

        self.partida = self.crear_partida("PartidaTest")

    def test_unirse_partida(self):
        # veo que este la partida en el menu principal
        response = self.client.get(reverse("menu_principal"))
        self.assertContains(response, "PartidaTest")
        self.assertContains(response, "Unirse")
        self.assertContains(response, reverse("ubicar_barcos", args=(self.partida.id,)))

        # me uno
        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertTemplateUsed(response, "ubicacion_barcos.html")


class UbicarBarcos(BNTestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("test", "test@test.com", "test")

        self.client.login(username="test", password="test")

        self.partida = self.crear_partida("PartidaTest")

        # aca deberia ir algo que me una a partida-> Si???

    def test_ubicar_barcos(self):
        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Acorazado")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "A", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Fragata")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "C", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Portaaviones")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "E", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Patrulla")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "G", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Submarino")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "I", "y": 1, "horizontal": False},
        )

        # el target_status_code es 302 porque ir a ubicar_barcos te tiene que
        # llevar a otra redireccion para ir a esperar jugadores
        self.assertRedirects(
            response,
            reverse("ubicar_barcos", args=(self.partida.id,)),
            target_status_code=302,
        )


class EsperandoJugadores(BNTestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("test", "test@test.com", "test")

        self.client.login(username="test", password="test")

        self.partida = self.crear_partida("PartidaTest")

        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()

        self.ubicar_barcos_predeterminadamente(self.tablero)

    def test_esperando(self):
        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertRedirects(
            response, reverse("esperando_jugadores", args=(self.partida.id,))
        )


class IniciarPartida(BNTestCase):
    def setUp(self):
        # Se crea la partida
        self.partida = self.crear_partida("PartidaTest")

        self.usuario = User.objects.create_user("test", "test@test.com", "test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)

        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.client.login(username="test2", password="test")
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.tablero_enemigo.crear_barcos()

        self.assertTrue(self.partida.cant_jugadores == 2)

    def test_iniciar_partida(self):
        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Acorazado")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "A", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Fragata")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "C", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Portaaviones")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "E", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Patrulla")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "G", "y": 1, "horizontal": False},
        )
        self.assertRedirects(
            response, reverse("ubicar_barcos", args=(self.partida.id,))
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))
        self.assertContains(response, "Submarino")

        response = self.client.post(
            reverse("ubicar_barcos", args=(self.partida.id,)),
            {"x": "I", "y": 1, "horizontal": False},
        )

        response = self.client.get(reverse("ubicar_barcos", args=(self.partida.id,)))

        response = self.client.get(
            reverse("esperando_jugadores", args=(self.partida.id,))
        )
        self.assertRedirects(
            response, reverse("esperando_turno", args=(self.partida.id,))
        )


class AtaqueNormal(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()

    def test_ataque_normal(self):
        response = self.client.get(reverse("elegir_enemigo", args=(self.partida.id,)))

        # compruebo que como hay un solo enemigo vaya a
        # atacarlo a el automaticamente
        self.assertRedirects(
            response, reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        self.assertTemplateUsed(response, "atacar.html")

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )

        self.assertTemplateUsed(response, "resultados_ataque.html")

        self.assertEqual(
            self.tablero_enemigo.acorazado_set.all()[0].puntos_tocados, [0]
        )

        self.assertContains(response, "Sesión de test1")
        self.assertContains(response, "tocado", 1)
        self.assertContains(response, "disparo", 0)


class AtaquePotente(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()

    def test_ataque_potente(self):
        response = self.client.get(reverse("elegir_enemigo", args=(self.partida.id,)))

        # compruebo que como hay un solo enemigo vaya a
        # atacarlo a el automaticamente
        self.assertRedirects(
            response, reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        self.assertTemplateUsed(response, "atacar.html")

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 1, "tipo": "P"},
        )

        self.assertTemplateUsed(response, "resultados_ataque.html")

        self.assertEqual(
            self.tablero_enemigo.acorazado_set.all()[0].puntos_tocados, [0, 1]
        )

        self.assertContains(response, "Sesión de test1")
        self.assertContains(response, "tocado", 2)
        self.assertContains(response, "disparo", 2)


class AtaqueRadar(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()

    def test_ataque_radar(self):
        response = self.client.get(reverse("elegir_enemigo", args=(self.partida.id,)))

        # compruebo que como hay un solo enemigo vaya a
        # atacarlo a el automaticamente
        self.assertRedirects(
            response, reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        self.assertTemplateUsed(response, "atacar.html")

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "b", "y": 2, "tipo": "R"},
        )

        self.assertTemplateUsed(response, "resultados_ataque.html")

        self.assertEqual(self.tablero_enemigo.acorazado_set.all()[0].puntos_tocados, [])
        self.assertEqual(self.tablero_enemigo.fragata_set.all()[0].puntos_tocados, [])

        self.assertContains(response, "Sesión de test1")
        self.assertContains(response, "radar", 9)
        self.assertContains(response, "aco0v", 1)
        self.assertContains(response, "aco1v", 1)
        self.assertContains(response, "aco2v", 1)
        self.assertContains(response, "fra0v", 1)
        self.assertContains(response, "fra1v", 1)
        self.assertContains(response, "fra2v", 1)
        self.assertContains(response, "disparo", 0)
        self.assertContains(response, "tocada", 0)


class DerrotoOponenteyQuedanOponentes(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida_corta("PartidaTest", 3)
        # Inicializo al jugador atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al jugador atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.client2 = Client()
        self.client2.login(username="test2", password="test")
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Inicializo al tercer jugador
        self.usuario3 = User.objects.create_user("test3", "test@test.com", "test")
        self.client3 = Client()
        self.client3.login(username="test3", password="test")
        self.jugador3 = self.crear_jugador(self.usuario3, self.partida)
        self.tablero3 = self.crear_tablero(self.jugador3)
        self.jugador3.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero3)

        self.partida.iniciar()

    def test_derroto_oponente_y_quedan_mas(self):
        response = self.client.get(reverse("elegir_enemigo", args=(self.partida.id,)))

        # compruebo que como hay un solo enemigo vaya a
        # compruebo que como hay dos enemigos no vaya a
        # atacarlo a el automaticamente
        self.assertTemplateUsed(response, "elegir_enemigo.html")

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        self.assertTemplateUsed(response, "atacar.html")

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )
        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "SD", "hacia_proa": False},
        )

        response = self.client2.post(
            reverse("ataque", args=(self.partida.id, self.jugador.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )
        response = self.client2.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "SD", "hacia_proa": False},
        )

        response = self.client3.post(
            reverse("ataque", args=(self.partida.id, self.jugador.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )
        response = self.client3.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "SD", "hacia_proa": False},
        )

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 2, "tipo": "N"},
        )

        self.assertEqual(self.partida.jugador_set.filter(derrotado=True).count(), 1)
        self.assertEqual(self.partida.jugador_set.filter(derrotado=False).count(), 2)

        self.assertTemplateUsed(response, "resultados_ataque.html")


class DerrotoOponenteyGanoPartida(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida_corta("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.client2 = Client()
        self.client2.login(username="test2", password="test")
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()

    def test_ganar_partida(self):
        response = self.client.get(reverse("elegir_enemigo", args=(self.partida.id,)))

        # compruebo que como hay un solo enemigo vaya a
        # atacarlo a el automaticamente
        self.assertRedirects(
            response, reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        self.assertTemplateUsed(response, "atacar.html")

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )
        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "SD", "hacia_proa": False},
        )

        response = self.client2.post(
            reverse("ataque", args=(self.partida.id, self.jugador.id)),
            {"x": "a", "y": 1, "tipo": "N"},
        )
        response = self.client2.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "SD", "hacia_proa": False},
        )

        response = self.client.post(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id)),
            {"x": "a", "y": 2, "tipo": "N"},
        )
        self.assertRedirects(response, reverse("ganador", args=(self.partida.id,)))


class MovimientoCorto(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()
        self.jugador.es_su_turno = True
        self.jugador.ya_ataco = True
        self.jugador.save()

    def test_mov_corto(self):

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        # compruebo que ya ataco y me direccione a defensa
        self.assertRedirects(response, reverse("defensa", args=(self.partida.id,)))

        response = self.client.get(reverse("defensa", args=(self.partida.id,)))
        self.assertTemplateUsed(response, "defender.html")

        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "a", "y": 1, "tipo": "MC", "hacia_proa": False},
        )

        self.assertRedirects(
            response, reverse("esperando_turno", args=(self.partida.id,))
        )
        self.assertEqual(self.tablero.acorazado_set.all()[0].y, 1)


class MovimientoLargo(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()
        self.jugador.es_su_turno = True
        self.jugador.ya_ataco = True
        self.jugador.save()

    def test_mov_largo(self):

        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        # compruebo que ya ataco y me direccione a defensa
        self.assertRedirects(response, reverse("defensa", args=(self.partida.id,)))

        response = self.client.get(reverse("defensa", args=(self.partida.id,)))
        self.assertTemplateUsed(response, "defender.html")

        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "c", "y": 1, "tipo": "ML", "hacia_proa": False},
        )

        self.assertRedirects(
            response, reverse("esperando_turno", args=(self.partida.id,))
        )
        self.assertEqual(self.tablero.fragata_set.all()[0].y, 2)


class Escudo(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()
        self.jugador.es_su_turno = True
        self.jugador.ya_ataco = True
        self.jugador.save()

    def test_escudo(self):
        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        # compruebo que ya ataco y me direccione a defensa
        self.assertRedirects(response, reverse("defensa", args=(self.partida.id,)))

        response = self.client.get(reverse("defensa", args=(self.partida.id,)))
        self.assertTemplateUsed(response, "defender.html")

        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "c", "y": 3, "tipo": "E", "hacia_proa": False},
        )

        self.assertRedirects(
            response, reverse("esperando_turno", args=(self.partida.id,))
        )
        mi_tablero = Tablero.objects.all()[0]
        for x in range(0, 9):
            for y in range(0, 9):
                if x in range(1, 4) and y in range(1, 4):
                    self.assertTrue(mi_tablero._en_escudo((x, y)))
                else:
                    self.assertFalse(mi_tablero._en_escudo((x, y)))


class Sumergimiento(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al atacante
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al atacado
        self.usuario_enemigo = User.objects.create_user(
            "test2", "test@test.com", "test"
        )
        self.jugador_enemigo = self.crear_jugador(self.usuario_enemigo, self.partida)
        self.tablero_enemigo = self.crear_tablero(self.jugador_enemigo)
        self.jugador_enemigo.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero_enemigo)
        # Empieza la partida
        self.partida.iniciar()
        self.jugador.es_su_turno = True
        self.jugador.ya_ataco = True
        self.jugador.save()

    def test_sumergimiento(self):
        response = self.client.get(
            reverse("ataque", args=(self.partida.id, self.jugador_enemigo.id))
        )
        # compruebo que ya ataco y me direccione a defensa
        self.assertRedirects(response, reverse("defensa", args=(self.partida.id,)))

        response = self.client.get(reverse("defensa", args=(self.partida.id,)))
        self.assertTemplateUsed(response, "defender.html")

        response = self.client.post(
            reverse("defensa", args=(self.partida.id,)),
            {"x": "i", "y": 1, "tipo": "SS", "hacia_proa": False},
        )

        self.assertRedirects(
            response, reverse("esperando_turno", args=(self.partida.id,))
        )
        mi_submarino = self.tablero.submarino_set.all()[0]

        self.assertTrue(mi_submarino.esta_sumergido)


class AbandonarPartidaNoIniciada(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al jugador 1
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al jugador 2
        self.usuario2 = User.objects.create_user("test2", "test@test.com", "test")
        self.client2 = Client()
        self.client2.login(username="test2", password="test")
        self.jugador2 = self.crear_jugador(self.usuario2, self.partida)
        self.tablero2 = self.crear_tablero(self.jugador2)
        self.jugador2.tablero.crear_barcos()

    def test_abandonar_partida_no_iniciada(self):
        response = self.client.get(reverse("abandonar", args=(self.partida.id,)))
        self.assertRedirects(response, reverse("menu_principal"))
        self.assertEqual(self.partida.jugador_set.count(), 1)
        response = self.client2.get(reverse("abandonar", args=(self.partida.id,)))
        self.assertRedirects(response, reverse("menu_principal"))
        self.assertEqual(Partida.objects.count(), 0)


class AbandonarPartidaIniciada(BNTestCase):
    def setUp(self):
        # Creo la partida
        self.partida = self.crear_partida("PartidaTest")
        # Inicializo al jugador 1
        self.usuario = User.objects.create_user("test1", "test@test.com", "test")
        self.client.login(username="test1", password="test")
        self.jugador = self.crear_jugador(self.usuario, self.partida)
        self.tablero = self.crear_tablero(self.jugador)
        self.jugador.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero)
        # Inicializo al jugador 2
        self.usuario2 = User.objects.create_user("test2", "test@test.com", "test")
        self.client2 = Client()
        self.client2.login(username="test2", password="test")
        self.jugador2 = self.crear_jugador(self.usuario2, self.partida)
        self.tablero2 = self.crear_tablero(self.jugador2)
        self.jugador2.tablero.crear_barcos()
        self.ubicar_barcos_predeterminadamente(self.tablero2)
        # Empieza la partida
        self.partida.iniciar()

    def test_abandonar_partida_iniciada(self):
        self.client.get(reverse("rendirse", args=(self.partida.id,)))
        self.assertEqual(self.partida.jugador_set.filter(derrotado=True).count(), 1)
        self.assertEqual(self.partida.jugador_set.filter(derrotado=False).count(), 1)


class CerrarSesion(BNTestCase):
    def setUp(self):
        self.partida = self.crear_partida("PartidaTest")
        self.usuario = User.objects.create_user("test", "test@test.com", "test")
        self.client.login(username="test", password="test")
        self.client.get(reverse("menu_principal"))

    def test_cerrar_sesion(self):
        # LogoutView en Django 5 requiere POST por defecto
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("menu_principal"))
        self.assertRedirects(response, reverse("login") + "?next=/menu/")
