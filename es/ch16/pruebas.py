# File: pruebas.py
#    Del capítulo 16 de _Algoritmos Genéticos con Python_
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

import circuitos
import genetic


def obtener_aptitud(genes, reglas, entradas):
    circuito = nodos_a_circuito(genes)[0]
    etiquetasDeFuente = "ABCD"
    reglasExitosas = 0
    for regla in reglas:
        entradas.clear()
        entradas.update(zip(etiquetasDeFuente, regla[0]))
        if circuito.obtener_salida() == regla[1]:
            reglasExitosas += 1
    return reglasExitosas


def mostrar(candidato, horaInicio):
    circuito = nodos_a_circuito(candidato.Genes)[0]
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}".format(
        circuito,
        candidato.Aptitud,
        diferencia))


def crear_gen(índice, puertas, fuentes):
    if índice < len(fuentes):
        tipoDePuerta = fuentes[índice]
    else:
        tipoDePuerta = random.choice(puertas)
    índiceA = índiceB = None
    if tipoDePuerta[1].recuento_de_entradas() > 0:
        índiceA = random.randint(0, índice)
    if tipoDePuerta[1].recuento_de_entradas() > 1:
        índiceB = random.randint(0, índice) \
            if índice > 1 and índice >= len(fuentes) else 0
        if índiceB == índiceA:
            índiceB = random.randint(0, índice)
    return Nodo(tipoDePuerta[0], índiceA, índiceB)


def mutar(genesDelNiño, fnCrearGen, fnObtenerAptitud, fuenteCount):
    cuenta = random.randint(1, 5)
    aptitudInicial = fnObtenerAptitud(genesDelNiño)
    while cuenta > 0:
        cuenta -= 1
        índicesUsados = [i for i in nodos_a_circuito(genesDelNiño)[1]
                         if i >= fuenteCount]
        if len(índicesUsados) == 0:
            return
        índice = random.choice(índicesUsados)
        genesDelNiño[índice] = fnCrearGen(índice)
        if fnObtenerAptitud(genesDelNiño) > aptitudInicial:
            return


class PruebasDeCircuitos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entradas = dict()
        cls.puertas = [[circuitos.And, circuitos.And],
                       [lambda i1, i2: circuitos.Not(i1), circuitos.Not]]
        cls.fuentes = [
            [lambda i1, i2: circuitos.Fuente('A', cls.entradas),
             circuitos.Fuente],
            [lambda i1, i2: circuitos.Fuente('B', cls.entradas),
             circuitos.Fuente]]

    def test_generar_OR(self):
        reglas = [[[False, False], False],
                  [[False, True], True],
                  [[True, False], True],
                  [[True, True], True]]

        longitudÓptima = 6
        self.encontrar_circuito(reglas, longitudÓptima)

    def test_generar_XOR(self):
        reglas = [[[False, False], False],
                  [[False, True], True],
                  [[True, False], True],
                  [[True, True], False]]
        self.encontrar_circuito(reglas, 9)

    def test_generar_AxBxC(self):
        reglas = [[[False, False, False], False],
                  [[False, False, True], True],
                  [[False, True, False], True],
                  [[False, True, True], False],
                  [[True, False, False], True],
                  [[True, False, True], False],
                  [[True, True, False], False],
                  [[True, True, True], True]]
        self.fuentes.append(
            [lambda l, r: circuitos.Fuente('C', self.entradas),
             circuitos.Fuente])
        self.puertas.append([circuitos.Or, circuitos.Or])
        self.encontrar_circuito(reglas, 12)

    def obtener_reglas_para_sumador_de_2_bits_bit(self, bit):
        reglas = [[[0, 0, 0, 0], [0, 0, 0]], # 0 + 0 = 0
                  [[0, 0, 0, 1], [0, 0, 1]], # 0 + 1 = 1
                  [[0, 0, 1, 0], [0, 1, 0]], # 0 + 2 = 2
                  [[0, 0, 1, 1], [0, 1, 1]], # 0 + 3 = 3
                  [[0, 1, 0, 0], [0, 0, 1]], # 1 + 0 = 1
                  [[0, 1, 0, 1], [0, 1, 0]], # 1 + 1 = 2
                  [[0, 1, 1, 0], [0, 1, 1]], # 1 + 2 = 3
                  [[0, 1, 1, 1], [1, 0, 0]], # 1 + 3 = 4
                  [[1, 0, 0, 0], [0, 1, 0]], # 2 + 0 = 2
                  [[1, 0, 0, 1], [0, 1, 1]], # 2 + 1 = 3
                  [[1, 0, 1, 0], [1, 0, 0]], # 2 + 2 = 4
                  [[1, 0, 1, 1], [1, 0, 1]], # 2 + 3 = 5
                  [[1, 1, 0, 0], [0, 1, 1]], # 3 + 0 = 3
                  [[1, 1, 0, 1], [1, 0, 0]], # 3 + 1 = 4
                  [[1, 1, 1, 0], [1, 0, 1]], # 3 + 2 = 5
                  [[1, 1, 1, 1], [1, 1, 0]]] # 3 + 3 = 6
        reglasDeBitN = [[regla[0], regla[1][2 - bit]] for regla in reglas]
        self.puertas.append([circuitos.Or, circuitos.Or])
        self.puertas.append([circuitos.Xor, circuitos.Xor])
        self.fuentes.append(
            [lambda l, r: circuitos.Fuente('C', self.entradas),
             circuitos.Fuente])
        self.fuentes.append(
            [lambda l, r: circuitos.Fuente('D', self.entradas),
             circuitos.Fuente])
        return reglasDeBitN

    def test_sumador_de_2_bits_bit_1(self):
        reglas = self.obtener_reglas_para_sumador_de_2_bits_bit(0)
        self.encontrar_circuito(reglas, 3)

    def test_sumador_de_2_bits_bit_2(self):
        reglas = self.obtener_reglas_para_sumador_de_2_bits_bit(1)
        self.encontrar_circuito(reglas, 7)

    def test_sumador_de_2_bits_bit_4s(self):
        reglas = self.obtener_reglas_para_sumador_de_2_bits_bit(2)
        self.encontrar_circuito(reglas, 9)

    def encontrar_circuito(self, reglas, longitudEsperada):
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato, longitud=None):
            if longitud is not None:
                print("-- nodos distintos en el circuito:",
                      len(nodos_a_circuito(candidato.Genes)[1]))
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, reglas, self.entradas)

        def fnCrearGen(índice):
            return crear_gen(índice, self.puertas, self.fuentes)

        def fnMutar(genes):
            mutar(genes, fnCrearGen, fnObtenerAptitud, len(self.fuentes))

        longitudMáxima = 50

        def fnCrear():
            return [fnCrearGen(i) for i in range(longitudMáxima)]

        def fnFunciónDeOptimización(longitudVariable):
            nonlocal longitudMáxima
            longitudMáxima = longitudVariable
            return genetic.obtener_mejor(
                fnObtenerAptitud, None, len(reglas), None, fnMostrar,
                fnMutar, fnCrear, tamañoDePiscina=3, segundosMáximos=30)

        def fnEsUnaMejora(mejorActual, niño):
            return niño.Aptitud == len(reglas) and \
                   len(nodos_a_circuito(niño.Genes)[1]) < \
                   len(nodos_a_circuito(mejorActual.Genes)[1])

        def fnEsÓptimo(niño):
            return niño.Aptitud == len(reglas) and \
                   len(nodos_a_circuito(niño.Genes)[1]) <= longitudEsperada

        def fnObtenerValorDeCaracterísticaSiguiente(mejorActual):
            return len(nodos_a_circuito(mejorActual.Genes)[1])

        mejor = genetic.ascenso_de_la_colina(
            fnFunciónDeOptimización, fnEsUnaMejora, fnEsÓptimo,
            fnObtenerValorDeCaracterísticaSiguiente, fnMostrar,
            longitudMáxima)
        self.assertTrue(mejor.Aptitud == len(reglas))
        self.assertFalse(len(nodos_a_circuito(mejor.Genes)[1])
                         > longitudEsperada)


def nodos_a_circuito(genes):
    circuito = []
    índicesUsados = []
    for i, nodo in enumerate(genes):
        usados = {i}
        entradaA = entradaB = None
        if nodo.ÍndiceA is not None and i > nodo.ÍndiceA:
            entradaA = circuito[nodo.ÍndiceA]
            usados.update(índicesUsados[nodo.ÍndiceA])
            if nodo.ÍndiceB is not None and i > nodo.ÍndiceB:
                entradaB = circuito[nodo.ÍndiceB]
                usados.update(índicesUsados[nodo.ÍndiceB])
        circuito.append(nodo.CrearPuerta(entradaA, entradaB))
        índicesUsados.append(usados)
    return circuito[-1], índicesUsados[-1]


class Nodo:
    def __init__(self, crearPuerta, índiceA=None, índiceB=None):
        self.CrearPuerta = crearPuerta
        self.ÍndiceA = índiceA
        self.ÍndiceB = índiceB


if __name__ == '__main__':
    unittest.main()
