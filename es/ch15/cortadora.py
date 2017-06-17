# File: cortadora.py
#    Del capítulo 15 de _Algoritmos Genéticos con Python_
#
# Author: Clinton Sheppard <fluentcoder@gmail.com>
# Copyright (c) 2017 Clinton Sheppard
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from enum import Enum


class ContenidoDelCampo(Enum):
    Hierba = ' #'
    Cortado = ' .'
    Cortador = 'C'

    def __str__(self):
        return self.value


class Dirección:
    def __init__(self, índice, xOffset, yOffset, símbolo):
        self.Índice = índice
        self.XOffset = xOffset
        self.YOffset = yOffset
        self.Símbolo = símbolo

    def mover_de(self, ubicación, distancia=1):
        return Ubicación(ubicación.X + distancia * self.XOffset,
                         ubicación.Y + distancia * self.YOffset)


class Direcciones(Enum):
    Norte = Dirección(0, 0, -1, '^')
    Este = Dirección(1, 1, 0, '>')
    Sur = Dirección(2, 0, 1, 'v')
    Oeste = Dirección(3, -1, 0, '<')

    @staticmethod
    def obtener_dirección_después_de_girar_a_la_izquierda_90_grados(dirección):
        nuevoÍndice = dirección.Índice - 1 \
            if dirección.Índice > 0 \
            else len(Direcciones) - 1
        nuevaDirección = next(i for i in Direcciones
                              if i.value.Índice == nuevoÍndice)
        return nuevaDirección.value

    @staticmethod
    def obtener_dirección_después_de_girar_a_la_derecha_90_grados(dirección):
        nuevoÍndice = dirección.Índice + 1 \
            if dirección.Índice < len(Direcciones) - 1 \
            else 0
        nuevaDirección = next(i for i in Direcciones
                              if i.value.Índice == nuevoÍndice)
        return nuevaDirección.value


class Ubicación:
    def __init__(self, x, y):
        self.X, self.Y = x, y

    def mover(self, xOffset, yOffset):
        return Ubicación(self.X + xOffset, self.Y + yOffset)


class Cortadora:
    def __init__(self, ubicación, dirección):
        self.Ubicación = ubicación
        self.Dirección = dirección
        self.CuentaDePasos = 0

    def girar_a_la_izquierda(self):
        self.CuentaDePasos += 1
        self.Dirección = Direcciones \
            .obtener_dirección_después_de_girar_a_la_izquierda_90_grados(
            self.Dirección)

    def corta(self, campo):
        nuevaUbicación = self.Dirección.mover_de(self.Ubicación)
        nuevaUbicación, esVálida = campo.arreglar_ubicación(nuevaUbicación)
        if esVálida:
            self.Ubicación = nuevaUbicación
            self.CuentaDePasos += 1
            campo.ajuste(self.Ubicación,
                         self.CuentaDePasos if self.CuentaDePasos > 9
                         else " {}".format(self.CuentaDePasos))

    def salta(self, campo, adelante, derecha):
        nuevaUbicación = self.Dirección.mover_de(self.Ubicación, adelante)
        derechaDirección = Direcciones \
            .obtener_dirección_después_de_girar_a_la_derecha_90_grados(
            self.Dirección)
        nuevaUbicación = derechaDirección.mover_de(nuevaUbicación, derecha)
        nuevaUbicación, esVálida = campo.arreglar_ubicación(nuevaUbicación)
        if esVálida:
            self.Ubicación = nuevaUbicación
            self.CuentaDePasos += 1
            campo.ajuste(self.Ubicación, self.CuentaDePasos
            if self.CuentaDePasos > 9
            else " {}".format(self.CuentaDePasos))


class Campo:
    def __init__(self, anchura, altura, contenidoInicial):
        self.Campo = [[contenidoInicial] * anchura for _ in range(altura)]
        self.Anchura = anchura
        self.Altura = altura

    def ajuste(self, ubicación, símbolo):
        self.Campo[ubicación.Y][ubicación.X] = símbolo

    def cuente_cortada(self):
        return sum(1 for fila in range(self.Altura)
                   for columna in range(self.Anchura)
                   if self.Campo[fila][columna] != ContenidoDelCampo.Hierba)

    def mostrar(self, cortadora):
        for índiceDeFilas in range(self.Altura):
            if índiceDeFilas != cortadora.Ubicación.Y:
                fila = ' '.join(map(str, self.Campo[índiceDeFilas]))
            else:
                r = self.Campo[índiceDeFilas][:]
                r[cortadora.Ubicación.X] = "{}{}".format(
                    ContenidoDelCampo.Cortador, cortadora.Dirección.Símbolo)
                fila = ' '.join(map(str, r))
            print(fila)


class CampoValidando(Campo):
    def __init__(self, anchura, altura, contenidoInicial):
        super().__init__(anchura, altura, contenidoInicial)

    def arreglar_ubicación(self, ubicación):
        if ubicación.X >= self.Anchura or \
                        ubicación.X < 0 or \
                        ubicación.Y >= self.Altura or \
                        ubicación.Y < 0:
            return None, False
        return ubicación, True


class CampoToroidal(Campo):
    def __init__(self, anchura, altura, contenidoInicial):
        super().__init__(anchura, altura, contenidoInicial)

    def arreglar_ubicación(self, ubicación):
        nuevaUbicación = Ubicación(ubicación.X, ubicación.Y)
        if nuevaUbicación.X < 0:
            nuevaUbicación.X += self.Anchura
        elif nuevaUbicación.X >= self.Anchura:
            nuevaUbicación.X %= self.Anchura

        if nuevaUbicación.Y < 0:
            nuevaUbicación.Y += self.Altura
        elif nuevaUbicación.Y >= self.Altura:
            nuevaUbicación.Y %= self.Altura

        return nuevaUbicación, True
