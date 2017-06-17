# File: oneMax.py
#    Del capítulo 2 de _Algoritmos Genéticos con Python_
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


def obtener_aptitud(genes):
    return genes.count(1)


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}...{}\t{:3.2f}\t{}".format(
        ''.join(map(str, candidato.Genes[:15])),
        ''.join(map(str, candidato.Genes[-15:])),
        candidato.Aptitud,
        diferencia))


class PruebasDeOneMax(unittest.TestCase):
    def test(self, longitud=100):
        geneSet = [0, 1]
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes)

        aptitudÓptima = longitud
        mejor = genetic.obtener_mejor(fnObtenerAptitud, longitud,
                                      aptitudÓptima, geneSet, fnMostrar)
        self.assertEqual(mejor.Aptitud, aptitudÓptima)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test(4000))


if __name__ == '__main__':
    unittest.main()
