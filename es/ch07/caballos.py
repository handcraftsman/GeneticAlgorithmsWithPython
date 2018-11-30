# File: caballos.py
#    Del capítulo 7 de _Algoritmos Genéticos con Python_
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

import datetime
import random
import unittest

import genetic


def obtener_aptitud(genes, tableroAncho, tableroAltura):
    atacado = set(pos
                  for kn in genes
                  for pos in obtener_ataques(kn, tableroAncho,
                                             tableroAltura))
    return len(atacado)


def mostrar(candidato, horaInicio, tableroAncho, tableroAltura):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    tablero = Tablero(candidato.Genes, tableroAncho, tableroAltura)
    tablero.print()

    print("{}\n\t{}\t{}".format(
        ' '.join(map(str, candidato.Genes)),
        candidato.Aptitud,
        diferencia))


def mutar(genes, tableroAncho, tableroAltura, todasPosiciones,
          posicionesNoBordeadas):
    cuenta = 2 if random.randint(0, 10) == 0 else 1
    while cuenta > 0:
        cuenta -= 1
        posiciónACaballoÍndices = dict((p, []) for p in todasPosiciones)
        for i, caballo in enumerate(genes):
            for posición in obtener_ataques(caballo, tableroAncho,
                                            tableroAltura):
                posiciónACaballoÍndices[posición].append(i)
        caballoÍndices = set(i for i in range(len(genes)))
        noAtacados = []
        for kvp in posiciónACaballoÍndices.items():
            if len(kvp[1]) > 1:
                continue
            if len(kvp[1]) == 0:
                noAtacados.append(kvp[0])
                continue
            for p in kvp[1]:  # longitud == 1
                if p in caballoÍndices:
                    caballoÍndices.remove(p)

        posicionesPotenciales = \
            [p for posiciones in
             map(lambda x: obtener_ataques(x, tableroAncho, tableroAltura),
                 noAtacados)
             for p in posiciones if p in posicionesNoBordeadas] \
                if len(noAtacados) > 0 else posicionesNoBordeadas

        índiceDeGen = random.randrange(0, len(genes)) \
            if len(caballoÍndices) == 0 \
            else random.choice([i for i in caballoÍndices])

        posición = random.choice(posicionesPotenciales)
        genes[índiceDeGen] = posición


def crear(fnObtenerPosiciónAleatoria, caballosEsperados):
    genes = [fnObtenerPosiciónAleatoria() for _ in range(caballosEsperados)]
    return genes


def obtener_ataques(ubicación, tableroAncho, tableroAltura):
    return [i for i in set(
        Posición(x + ubicación.X, y + ubicación.Y)
        for x in [-2, -1, 1, 2] if 0 <= x + ubicación.X < tableroAncho
        for y in [-2, -1, 1, 2] if 0 <= y + ubicación.Y < tableroAltura
        and abs(y) != abs(x))]


class PruebasDeCaballos(unittest.TestCase):
    def test_3x4(self):
        anchura = 4
        altura = 3
        # 1,0   2,0   3,0
        # 0,2   1,2   2,2
        # 2 	 C C C .
        # 1 	 . . . .
        # 0 	 . C C C
        #   	 0 1 2 3
        self.encontrarCaballoPosiciones(anchura, altura, 6)

    def test_8x8(self):
        anchura = 8
        altura = 8
        self.encontrarCaballoPosiciones(anchura, altura, 14)

    def test_10x10(self):
        anchura = 10
        altura = 10
        self.encontrarCaballoPosiciones(anchura, altura, 22)

    def test_12x12(self):
        anchura = 12
        altura = 12
        self.encontrarCaballoPosiciones(anchura, altura, 28)

    def test_13x13(self):
        anchura = 13
        altura = 13
        self.encontrarCaballoPosiciones(anchura, altura, 32)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test_10x10())

    def encontrarCaballoPosiciones(self, tableroAncho, tableroAltura,
                                   caballosEsperados):
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio, tableroAncho, tableroAltura)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, tableroAncho, tableroAltura)

        todasPosiciones = [Posición(x, y)
                           for y in range(tableroAltura)
                           for x in range(tableroAncho)]

        if tableroAncho < 6 or tableroAltura < 6:
            posicionesNoBordeadas = todasPosiciones
        else:
            posicionesNoBordeadas = [i for i in todasPosiciones
                                     if 0 < i.X < tableroAncho - 1 and
                                     0 < i.Y < tableroAltura - 1]

        def fnObtenerPosiciónAleatoria():
            return random.choice(posicionesNoBordeadas)

        def fnMutar(genes):
            mutar(genes, tableroAncho, tableroAltura, todasPosiciones,
                  posicionesNoBordeadas)

        def fnCrear():
            return crear(fnObtenerPosiciónAleatoria, caballosEsperados)

        aptitudÓptima = tableroAncho * tableroAltura
        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, aptitudÓptima,
                                      None, fnMostrar, fnMutar, fnCrear)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)


class Posición:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "{},{}".format(self.X, self.Y)

    def __eq__(self, otro):
        return self.X == otro.X and self.Y == otro.Y

    def __hash__(self):
        return self.X * 1000 + self.Y


class Tablero:
    def __init__(self, posiciones, anchura, altura):
        tablero = [['.'] * anchura for _ in range(altura)]

        for índice in range(len(posiciones)):
            posiciónDeCaballo = posiciones[índice]
            tablero[posiciónDeCaballo.Y][posiciónDeCaballo.X] = 'C'
        self._tablero = tablero
        self._anchura = anchura
        self._altura = altura

    def print(self):
        # 0,0 muestra en la esquina inferior izquierda
        for i in reversed(range(self._altura)):
            print(i, "\t", ' '.join(self._tablero[i]))
        print(" \t", ' '.join(map(str, range(self._anchura))))


if __name__ == '__main__':
    unittest.main()
