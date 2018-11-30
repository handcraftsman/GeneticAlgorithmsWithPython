# File: cartas.py
#    Del capítulo 6 de _Algoritmos Genéticos con Python_
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
import functools
import operator
import random
import unittest

import genetic


def obtener_aptitud(genes):
    sumaDelGrupo1 = sum(genes[0:5])
    productoDelGrupo2 = functools.reduce(operator.mul, genes[5:10])
    duplicados = (len(genes) - len(set(genes)))
    return Aptitud(sumaDelGrupo1, productoDelGrupo2, duplicados)


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{} - {}\t{}\t{}".format(
        ', '.join(map(str, candidato.Genes[0:5])),
        ', '.join(map(str, candidato.Genes[5:10])),
        candidato.Aptitud,
        diferencia))


def mutar(genes, geneSet):
    if len(genes) == len(set(genes)):
        cuenta = random.randint(1, 4)
        while cuenta > 0:
            cuenta -= 1
            índiceA, índiceB = random.sample(range(len(genes)), 2)
            genes[índiceA], genes[índiceB] = genes[índiceB], genes[índiceA]
    else:
        índiceA = random.randrange(0, len(genes))
        índiceB = random.randrange(0, len(geneSet))
        genes[índiceA] = geneSet[índiceB]


class PruebasDeCartas(unittest.TestCase):
    def test(self):
        geneSet = [i + 1 for i in range(10)]
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes)

        def fnMutar(genes):
            mutar(genes, geneSet)

        aptitudÓptima = Aptitud(36, 360, 0)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, 10, aptitudÓptima,
                                      geneSet, fnMostrar,
                                      mutación_personalizada=fnMutar)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test())


class Aptitud:
    def __init__(self, sumaDelGrupo1, productoDelGrupo2, duplicados):
        self.SumaDelGrupo1 = sumaDelGrupo1
        self.ProductoDelGrupo2 = productoDelGrupo2
        diferenciaSuma = abs(36 - sumaDelGrupo1)
        diferenciaProducto = abs(360 - productoDelGrupo2)
        self.DiferenciaTotal = diferenciaSuma + diferenciaProducto
        self.Duplicados = duplicados

    def __gt__(self, otro):
        if self.Duplicados != otro.Duplicados:
            return self.Duplicados < otro.Duplicados
        return self.DiferenciaTotal < otro.DiferenciaTotal

    def __str__(self):
        return "sum: {} prod: {} dups: {}".format(
            self.SumaDelGrupo1,
            self.ProductoDelGrupo2,
            self.Duplicados)


if __name__ == '__main__':
    unittest.main()
