# File: cuadradosMágicos.py
#    Del capítulo 8 de _Algoritmos Genéticos con Python_
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


def obtener_aptitud(genes, tamañoDiagonal, sumaEsperada):
    filas, columnas, sumaDiagonalNoreste, sumaDiagonalSureste = \
        obtener_sums(genes, tamañoDiagonal)

    sumaDeDiferencias = sum(int(abs(s - sumaEsperada))
                            for s in filas + columnas +
                            [sumaDiagonalSureste, sumaDiagonalNoreste]
                            if s != sumaEsperada)

    return Aptitud(sumaDeDiferencias)


def mostrar(candidato, tamañoDiagonal, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()

    filas, columnas, sumaDiagonalNoreste, sumaDiagonalSureste = \
        obtener_sums(candidato.Genes, tamañoDiagonal)

    for númeroDeFila in range(tamañoDiagonal):
        fila = candidato.Genes[
               númeroDeFila * tamañoDiagonal:(númeroDeFila + 1) *
                                             tamañoDiagonal]
        print("\t ", fila, "=", filas[númeroDeFila])
    print(sumaDiagonalNoreste, "\t", columnas, "\t", sumaDiagonalSureste)
    print(" - - - - - - - - - - -", candidato.Aptitud, diferencia)


def obtener_sums(genes, tamañoDiagonal):
    filas = [0 for _ in range(tamañoDiagonal)]
    columnas = [0 for _ in range(tamañoDiagonal)]
    sumaDiagonalSureste = 0
    sumaDiagonalNoreste = 0
    for fila in range(tamañoDiagonal):
        for columna in range(tamañoDiagonal):
            valor = genes[fila * tamañoDiagonal + columna]
            filas[fila] += valor
            columnas[columna] += valor
        sumaDiagonalSureste += genes[fila * tamañoDiagonal + fila]
        sumaDiagonalNoreste += genes[fila * tamañoDiagonal +
                                     (tamañoDiagonal - 1 - fila)]
    return filas, columnas, sumaDiagonalNoreste, sumaDiagonalSureste


def mutar(genes, índices):
    índiceA, índiceB = random.sample(índices, 2)
    genes[índiceA], genes[índiceB] = genes[índiceB], genes[índiceA]


# `nosetests` no admite caracteres como á en el nombre de la clase
class PruebasDeCuadradosMagicos(unittest.TestCase):
    def test_tamaño_3(self):
        self.generar(3, 50)

    def test_tamaño_4(self):
        self.generar(4, 50)

    def test_tamaño_5(self):
        self.generar(5, 500)

    def test_tamaño_10(self):
        self.generar(10, 5000)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(self.test_tamaño_4)

    def generar(self, tamañoDiagonal, edadMáxima):
        nCuadrado = tamañoDiagonal * tamañoDiagonal
        geneSet = [i for i in range(1, nCuadrado + 1)]
        sumaEsperada = tamañoDiagonal * (nCuadrado + 1) / 2

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, tamañoDiagonal, sumaEsperada)

        def fnMostrar(candidato):
            mostrar(candidato, tamañoDiagonal, horaInicio)

        geneÍndices = [i for i in range(0, len(geneSet))]

        def fnMutar(genes):
            mutar(genes, geneÍndices)

        def fnCreaciónPersonalizada():
            return random.sample(geneSet, len(geneSet))

        valorÓptimo = Aptitud(0)
        horaInicio = datetime.datetime.now()
        mejor = genetic.obtener_mejor(fnObtenerAptitud, nCuadrado, valorÓptimo,
                                      geneSet, fnMostrar, fnMutar,
                                      fnCreaciónPersonalizada, edadMáxima)
        self.assertTrue(not valorÓptimo > mejor.Aptitud)


class Aptitud:
    def __init__(self, sumaDeDiferencias):
        self.SumaDeDiferencias = sumaDeDiferencias

    def __gt__(self, otro):
        return self.SumaDeDiferencias < otro.SumaDeDiferencias

    def __str__(self):
        return "{}".format(self.SumaDeDiferencias)


if __name__ == '__main__':
    unittest.main()
