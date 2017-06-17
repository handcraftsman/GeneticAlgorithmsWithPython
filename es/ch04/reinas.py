# File: reinas.py
#    Del capítulo 4 de _Algoritmos Genéticos con Python_
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
import unittest

import genetic


def obtener_aptitud(genes, tamaño):
    tablero = Tablero(genes, tamaño)
    filasConReinas = set()
    columnasConReinas = set()
    diagonalesNoresteConReinas = set()
    diagonalesSudoesteConReinas = set()
    for fila in range(tamaño):
        for columna in range(tamaño):
            if tablero.get(fila, columna) == 'R':
                filasConReinas.add(fila)
                columnasConReinas.add(columna)
                diagonalesNoresteConReinas.add(fila + columna)
                diagonalesSudoesteConReinas.add(tamaño - 1 - fila + columna)
    total = (tamaño - len(filasConReinas)
             + tamaño - len(columnasConReinas)
             + tamaño - len(diagonalesNoresteConReinas)
             + tamaño - len(diagonalesSudoesteConReinas))
    return Aptitud(total)


def mostrar(candidato, horaInicio, tamaño):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    tablero = Tablero(candidato.Genes, tamaño)
    tablero.print()
    print("{}\t- {}\t{}".format(
        ' '.join(map(str, candidato.Genes)),
        candidato.Aptitud,
        diferencia))


class PruebasDeReinas(unittest.TestCase):
    def test(self, tamaño=8):
        geneSet = [i for i in range(tamaño)]
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio, tamaño)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, tamaño)

        aptitudÓptima = Aptitud(0)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, 2 * tamaño,
                                      aptitudÓptima, geneSet, fnMostrar)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test(20))


class Tablero:
    def __init__(self, genes, tamaño):
        tablero = [['.'] * tamaño for _ in range(tamaño)]
        for índice in range(0, len(genes), 2):
            fila = genes[índice]
            columna = genes[índice + 1]
            tablero[columna][fila] = 'R'
        self._tablero = tablero

    def get(self, fila, columna):
        return self._tablero[columna][fila]

    def print(self):
        # 0,0 muestra en la esquina inferior izquierda
        for i in reversed(range(len(self._tablero))):
            print(' '.join(self._tablero[i]))


class Aptitud:
    def __init__(self, total):
        self.Total = total

    def __gt__(self, otro):
        return self.Total < otro.Total

    def __str__(self):
        return "{}".format(self.Total)


if __name__ == '__main__':
    unittest.main()
