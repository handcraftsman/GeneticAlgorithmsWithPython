# File: ecuacionesLineales.py
#    Del capítulo 10 de _Algoritmos Genéticos con Python_
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
from fractions import Fraction
import random
import unittest

import genetic


def obtener_aptitud(genes, ecuaciones):
    aptitud = Aptitud(sum(abs(e(genes)) for e in ecuaciones))
    return aptitud


def mostrar(candidato, horaInicio, fnGenesAEntradas):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    símbolos = "xyza"
    resultado = ', '.join("{} = {}".format(s, v)
                          for s, v in
                          zip(símbolos, fnGenesAEntradas(candidato.Genes)))
    print("{}\t{}\t{}".format(
        resultado,
        candidato.Aptitud,
        diferencia))


def mutar(genes, geneSetOrdenado, ventana, geneÍndices):
    índices = random.sample(geneÍndices, random.randint(1, len(genes))) \
        if random.randint(0, 10) == 0 else [random.choice(geneÍndices)]
    ventana.deslizar()
    while len(índices) > 0:
        índice = índices.pop()
        geneSetÍndice = geneSetOrdenado.index(genes[índice])
        principio = max(0, geneSetÍndice - ventana.Tamaño)
        fin = min(len(geneSetOrdenado) - 1, geneSetÍndice + ventana.Tamaño)
        geneSetÍndice = random.randint(principio, fin)
        genes[índice] = geneSetOrdenado[geneSetÍndice]


class PruebasDeEcuacionesLineales(unittest.TestCase):
    def test_2_desconocidos(self):
        geneSet = [i for i in range(-5, 5) if i != 0]

        def fnGenesAEntradas(genes):
            return genes[0], genes[1]

        def e1(genes):
            x, y = fnGenesAEntradas(genes)
            return x + 2 * y - 4

        def e2(genes):
            x, y = fnGenesAEntradas(genes)
            return 4 * x + 4 * y - 12

        ecuaciones = [e1, e2]
        self.resolver_desconocidos(2, geneSet, ecuaciones, fnGenesAEntradas)

    def test_3_desconocidos(self):
        valores = [i for i in range(-5, 5) if i != 0]
        geneSet = [i for i in set(
            Fraction(d, e)
            for d in valores
            for e in valores if e != 0)]

        def fnGenesAEntradas(genes):
            return genes

        def e1(genes):
            x, y, z = genes
            return 6 * x - 2 * y + 8 * z - 20

        def e2(genes):
            x, y, z = genes
            return y + 8 * x * z + 1

        def e3(genes):
            x, y, z = genes
            return 2 * z * Fraction(6, x) \
                   + 3 * Fraction(y, 2) - 6

        ecuaciones = [e1, e2, e3]
        self.resolver_desconocidos(3, geneSet, ecuaciones, fnGenesAEntradas)

    def test_4_desconocidos(self):
        valores = [i for i in range(-13, 13) if i != 0]
        geneSet = [i for i in set(
            Fraction(d, e)
            for d in valores
            for e in valores if e != 0)]

        def fnGenesAEntradas(genes):
            return genes

        def e1(genes):
            x, y, z, a = genes
            return Fraction(1, 15) * x \
                   - 2 * y \
                   - 15 * z \
                   - Fraction(4, 5) * a \
                   - 3

        def e2(genes):
            x, y, z, a = genes
            return -Fraction(5, 2) * x \
                   - Fraction(9, 4) * y \
                   + 12 * z \
                   - a \
                   - 17

        def e3(genes):
            x, y, z, a = genes
            return -13 * x \
                   + Fraction(3, 10) * y \
                   - 6 * z \
                   - Fraction(2, 5) * a \
                   - 17

        def e4(genes):
            x, y, z, a = genes
            return Fraction(1, 2) * x \
                   + 2 * y \
                   + Fraction(7, 4) * z \
                   + Fraction(4, 3) * a \
                   + 9

        ecuaciones = [e1, e2, e3, e4]
        self.resolver_desconocidos(4, geneSet, ecuaciones, fnGenesAEntradas)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test_4_desconocidos())

    def resolver_desconocidos(self, numUnknowns, geneSet, ecuaciones,
                              fnGenesAEntradas):
        horaInicio = datetime.datetime.now()
        edadMáxima = 50
        ventana = Ventana(max(1, int(len(geneSet) / (2 * edadMáxima))),
                          max(1, int(len(geneSet) / 3)),
                          int(len(geneSet) / 2))
        geneÍndices = [i for i in range(numUnknowns)]
        geneSetOrdenado = sorted(geneSet)

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio, fnGenesAEntradas)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, ecuaciones)

        def fnMutar(genes):
            mutar(genes, geneSetOrdenado, ventana, geneÍndices)

        aptitudÓptima = Aptitud(0)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, numUnknowns,
                                      aptitudÓptima, geneSet, fnMostrar,
                                      fnMutar, edadMáxima=edadMáxima)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)


class Aptitud:
    def __init__(self, diferenciaTotal):
        self.DiferenciaTotal = diferenciaTotal

    def __gt__(self, otro):
        return self.DiferenciaTotal < otro.DiferenciaTotal

    def __str__(self):
        return "dif: {:0.2f}".format(float(self.DiferenciaTotal))


class Ventana:
    def __init__(self, mínimo, máximo, tamaño):
        self.Min = mínimo
        self.Max = máximo
        self.Tamaño = tamaño

    def deslizar(self):
        self.Tamaño = self.Tamaño - 1 if self.Tamaño > self.Min else self.Max


if __name__ == '__main__':
    unittest.main()
