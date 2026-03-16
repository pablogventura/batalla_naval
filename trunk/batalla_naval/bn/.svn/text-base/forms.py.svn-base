#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from bn.models import *

#TODO agregar labels para que se vea bien


class NuevaPartidaForm(ModelForm):
    """
    Formulario que se muestra al crear nuevas partidas.
    """
    class Meta:
        model = Partida
        exclude = ('cant_turnos_totales', 'cant_turnos_de_la_ronda',
                   'numero_ronda_actual', 'iniciada', 'terminada')

    def clean_ancho_tablero(self):
        ancho = int(self.data['ancho_tablero'])
        if not 9 <= ancho <= 18:
            raise forms.ValidationError('El ancho debe estar entre 9 y 18')
        return ancho

    def clean_cant_jugadores(self):
        j = int(self.data['cant_jugadores'])
        if j < 2:
            raise forms.ValidationError('Debe haber al menos 2 jugadores.')
        return j

    def clean_nombre(self):
        nombre = self.data['nombre']
        for partida in Partida.objects.filter(nombre=nombre):
            if not partida.terminada:
                raise forms.ValidationError('Ya hay una partida en curso con ese nombre.')
        return nombre

    def clean(self, *args, **kwargs):
        cleaned_data = super(NuevaPartidaForm, self).clean(*args, **kwargs)
        ancho = cleaned_data.get('ancho_tablero')
        barcos = cleaned_data.get('cant_submarinos')
        barcos += cleaned_data.get('cant_fragatas')
        barcos += cleaned_data.get('cant_patrullas')
        barcos += cleaned_data.get('cant_acorazados')
        barcos += cleaned_data.get('cant_portaaviones')
        if not barcos > 0:
            raise forms.ValidationError('Debe haber al menos 1 barco.')

        # algoritmo de verificacion de la relacion del tamaño del tablero
        # con la cantidad y tamaño de los barcos
        celdas = self.cleaned_data['cant_submarinos'] * (
            CELDAS_SUBMARINO * 2 + 2)
        celdas += self.cleaned_data['cant_fragatas'] * (CELDAS_FRAGATA * 2 + 2)
        celdas += self.cleaned_data['cant_patrullas'] * (
            CELDAS_PATRULLA * 2 + 2)
        celdas += self.cleaned_data['cant_acorazados'] * (
            CELDAS_ACORAZADO * 2 + 2)
        celdas += self.cleaned_data['cant_portaaviones'] * (
            CELDAS_PORTAAVIONES * 2 + 2)
        if ancho:
            if celdas >= pow(ancho + 1, 2):
                raise forms.ValidationError(
                    'Demasiados barcos para el tamaño del tablero.')

        return self.cleaned_data


class NuevoUsuarioForm(UserCreationForm):
    """
    Formulario que se muestra al registrarse.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")


class UbicarBarcoForm(forms.Form):
    """
    Formulario que se muestra durante la ubicacion de barcos.
    """
    x = forms.CharField(max_length=1, initial='A', required=True)
    y = forms.IntegerField(initial=1, required=True)
    horizontal = forms.BooleanField(initial=False, required=False)

    def clean_x(self):
        x = self.data['x'].upper()
        x = ord(x) - 65
        return x

    def clean_y(self):
        y = int(self.data['y'])
        if y < 1:
            raise forms.ValidationError('Debe ser mayor a 1')
        y = y - 1
        return y


class AtaqueForm(forms.Form):
    """
    Formulario que se muestra para realizar un ataque.
    """
    x = forms.CharField(max_length=1, initial='A', required=True)
    y = forms.IntegerField(initial=1, required=True)
    tipo = forms.ChoiceField(widget=forms.Select(),
                             choices=([('N', 'Normal'),
                             ('P', 'Potente'), ('R', 'Radar'), ]),
                             required = True,)

    def clean_x(self):
        x = self.data['x'].upper()
        x = ord(x) - 65
        return x

    def clean_y(self):
        y = int(self.data['y'])
        if y < 1:
            raise forms.ValidationError('Debe ser mayor a 1')
        y = y - 1
        return y


class DefensaForm(forms.Form):
    """
    Formulario que se muestra para realizar una defensa.
    """
    x = forms.CharField(max_length=1, initial='A', required=True)
    y = forms.IntegerField(initial=1, required=True)
    tipo = forms.ChoiceField(widget=forms.Select(),
                             choices=([('SD', 'Saltear Defensa'),
                                       ('MC', 'Movimiento corto'),
                                       ('ML', 'Movimiento largo'),
                                       ('E', 'Escudo'),
                                       ('SS', 'Sumergimiento'),
                                       ]), required = True,)

    hacia_proa = forms.BooleanField(initial=False, required=False)

    def clean_x(self):
        x = self.data['x'].upper()
        x = ord(x) - 65
        return x

    def clean_y(self):
        y = int(self.data['y'])
        if y < 1:
            raise forms.ValidationError('Debe ser mayor a 1')
        y = y - 1
        return y
