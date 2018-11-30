# File: pi.py
#    Del capítulo 13 de _Algoritmos Genéticos con Python_
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
import math
import random
import sys
import time
import unittest

import genetic


def obtener_aptitud(genes, valoresDeBits):
    denominator = obtener_denominador(genes, valoresDeBits)
    if denominator == 0:
        return 0

    relación = obtener_numerador(genes, valoresDeBits) / denominator
    return math.pi - math.fabs(math.pi - relación)


def mostrar(candidato, horaInicio, valoresDeBits):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    numerador = obtener_numerador(candidato.Genes, valoresDeBits)
    denominator = obtener_denominador(candidato.Genes, valoresDeBits)
    print("{}/{}\t{}\t{}".format(
        numerador,
        denominator,
        candidato.Aptitud, diferencia))


def bits_a_entero(bits, valoresDeBits):
    resultado = 0
    for i, bit in enumerate(bits):
        if bit == 0:
            continue
        resultado += valoresDeBits[i]
    return resultado


def obtener_numerador(genes, valoresDeBits):
    return 1 + bits_a_entero(genes[:len(valoresDeBits)], valoresDeBits)


def obtener_denominador(genes, valoresDeBits):
    return bits_a_entero(genes[len(valoresDeBits):], valoresDeBits)


def mutar(genes, numBits):
    índiceDelNumerador, índiceDelDenominador \
        = random.randrange(0, numBits), random.randrange(numBits,
                                                         len(genes))
    genes[índiceDelNumerador] = 1 - genes[índiceDelNumerador]
    genes[índiceDelDenominador] = 1 - genes[índiceDelDenominador]


class PruebasDePi(unittest.TestCase):
    def test(self, valoresDeBits=[512, 256, 128, 64, 32, 16, 8, 4, 2, 1],
             segundosMáximos=None):
        geneSet = [i for i in range(2)]
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio, valoresDeBits)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, valoresDeBits)

        aptitudÓptima = 3.14159

        def fnMutar(genes):
            mutar(genes, len(valoresDeBits))

        longitud = 2 * len(valoresDeBits)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, longitud,
                                      aptitudÓptima, geneSet, fnMostrar,
                                      fnMutar, edadMáxima=250,
                                      segundosMáximos=segundosMáximos)
        return aptitudÓptima <= mejor.Aptitud

    def test_optimize(self):
        geneSet = [i for i in range(1, 512 + 1)]
        longitud = 10
        segundosMáximos = 2

        def fnObtenerAptitud(genes):
            horaInicio = time.time()
            cuenta = 0
            stdout = sys.stdout
            sys.stdout = None
            while time.time() - horaInicio < segundosMáximos:
                if self.test(genes, segundosMáximos):
                    cuenta += 1
            sys.stdout = stdout
            distancia = abs(sum(genes) - 1023)
            fracción = 1 / distancia if distancia > 0 else distancia
            cuenta += round(fracción, 4)
            return cuenta

        def fnMostrar(cromosoma):
            print("{}\t{}".format(cromosoma.Genes, cromosoma.Aptitud))

        initial = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
        print("initial:", initial, fnObtenerAptitud(initial))

        aptitudÓptima = 10 * segundosMáximos
        genetic.obtener_mejor(fnObtenerAptitud, longitud, aptitudÓptima,
                              geneSet, fnMostrar, segundosMáximos=600)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(
            lambda: self.test([98, 334, 38, 339, 117,
                               39, 145, 123, 40, 129]))

    def test_encontrar_10_mejores_aproximaciones(self):
        mejor = {}
        for numerador in range(1, 1024):
            for denominator in range(1, 1024):
                relación = numerador / denominator
                piDist = math.pi - abs(math.pi - relación)
                if piDist not in mejor or mejor[piDist][0] > numerador:
                    mejor[piDist] = [numerador, denominator]

        mejoresAproximaciones = list(reversed(sorted(mejor.keys())))
        for i in range(10):
            relación = mejoresAproximaciones[i]
            nd = mejor[relación]
            print("%i / %i\t%f" % (nd[0], nd[1], relación))


if __name__ == '__main__':
    unittest.main()
