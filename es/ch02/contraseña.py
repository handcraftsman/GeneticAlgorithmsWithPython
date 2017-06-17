# File: contraseña.py
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
import random
import unittest

import genetic


def obtener_aptitud(conjetura, objetivo):
    return sum(1 for esperado, real in zip(objetivo, conjetura)
               if esperado == real)


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}".format(
        ''.join(candidato.Genes),
        candidato.Aptitud,
        diferencia))


# `nosetests` no admite caracteres como ñ en el nombre de la clase
class PruebasDeContrasena(unittest.TestCase):
    geneSet = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!¡.,"

    def test_Hola_Mundo(self):
        objetivo = "¡Hola Mundo!"
        self.adivine_contraseña(objetivo)

    def test_Porque_me_formaste_de_una_manera_formidable_y_maravillosa(self):
        objetivo = "Porque me formaste de una manera formidable y maravillosa."
        self.adivine_contraseña(objetivo)

    def adivine_contraseña(self, objetivo):
        horaInicio = datetime.datetime.now()

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, objetivo)

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        aptitudÓptima = len(objetivo)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, len(objetivo),
                                      aptitudÓptima, self.geneSet, fnMostrar)
        self.assertEqual(''.join(mejor.Genes), objetivo)

    def test_aleatorio(self):
        longitud = 150
        objetivo = ''.join(random.choice(self.geneSet)
                           for _ in range(longitud))

        self.adivine_contraseña(objetivo)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(self.test_aleatorio)


if __name__ == '__main__':
    unittest.main()
