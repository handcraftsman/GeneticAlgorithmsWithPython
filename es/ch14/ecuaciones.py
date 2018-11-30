# File: ecuaciones.py
#    Del capítulo 14 de _Algoritmos Genéticos con Python_
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


def evaluar(genes, operacionesPriorizadas):
    ecuación = genes[:]
    for operationSet in operacionesPriorizadas:
        iOffset = 0
        for i in range(1, len(ecuación), 2):
            i += iOffset
            opSímbolo = ecuación[i]
            if opSímbolo in operationSet:
                operandoIzquierdo = ecuación[i - 1]
                operandoDerecho = ecuación[i + 1]
                ecuación[i - 1] = operationSet[opSímbolo](operandoIzquierdo,
                                                          operandoDerecho)
                del ecuación[i + 1]
                del ecuación[i]
                iOffset += -2
    return ecuación[0]


def añadir(a, b):
    return a + b


def sustraer(a, b):
    return a - b


def multiplicar(a, b):
    return a * b


def obtener_aptitud(genes, totalEsperado, fnEvaluar):
    resultado = fnEvaluar(genes)

    if resultado != totalEsperado:
        aptitud = totalEsperado - abs(resultado - totalEsperado)
    else:
        aptitud = 1000 - len(genes)

    return aptitud


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}".format(
        (' '.join(map(str, [i for i in candidato.Genes]))),
        candidato.Aptitud,
        diferencia))


def crear(números, operaciones, númerosMin, númerosMax):
    genes = [random.choice(números)]
    cuenta = random.randint(númerosMin, 1 + númerosMax)
    while cuenta > 1:
        cuenta -= 1
        genes.append(random.choice(operaciones))
        genes.append(random.choice(números))
    return genes


def mutar(genes, números, operaciones, númerosMin, númerosMax,
          fnObtenerAptitud):
    cuenta = random.randint(1, 10)
    aptitudInicial = fnObtenerAptitud(genes)
    while cuenta > 0:
        cuenta -= 1
        if fnObtenerAptitud(genes) > aptitudInicial:
            return
        cuentaDeNúmeros = (1 + len(genes)) / 2
        añadiendo = cuentaDeNúmeros < númerosMax and \
                    random.randint(0, 100) == 0
        if añadiendo:
            genes.append(random.choice(operaciones))
            genes.append(random.choice(números))
            continue

        eliminando = cuentaDeNúmeros > númerosMin and \
                     random.randint(0, 20) == 0
        if eliminando:
            índice = random.randrange(0, len(genes) - 1)
            del genes[índice]
            del genes[índice]
            continue

        índice = random.randrange(0, len(genes))
        genes[índice] = random.choice(operaciones) \
            if (índice & 1) == 1 else random.choice(números)


class PruebasDeEcuaciones(unittest.TestCase):
    def test_adición(self):
        operaciones = ['+', '-']
        operacionesPriorizadas = [{'+': añadir,
                                   '-': sustraer}]
        soluciónDeLongitudÓptima = [7, '+', 7, '+', 7, '+', 7, '+', 7, '-', 6]
        self.resolver(operaciones, operacionesPriorizadas,
                      soluciónDeLongitudÓptima)

    def test_multiplicación(self):
        operaciones = ['+', '-', '*']
        operacionesPriorizadas = [{'*': multiplicar},
                                  {'+': añadir,
                                   '-': sustraer}]
        soluciónDeLongitudÓptima = [6, '*', 3, '*', 3, '*', 6, '-', 7]
        self.resolver(operaciones, operacionesPriorizadas,
                      soluciónDeLongitudÓptima)

    def test_exponente(self):
        operaciones = ['^', '+', '-', '*']
        operacionesPriorizadas = [{'^': lambda a, b: a ** b},
                                  {'*': multiplicar},
                                  {'+': añadir,
                                   '-': sustraer}]
        soluciónDeLongitudÓptima = [6, '^', 3, '*', 2, '-', 5]
        self.resolver(operaciones, operacionesPriorizadas,
                      soluciónDeLongitudÓptima)

    def resolver(self, operaciones, operacionesPriorizadas,
                 soluciónDeLongitudÓptima):
        números = [1, 2, 3, 4, 5, 6, 7]
        totalEsperado = evaluar(soluciónDeLongitudÓptima,
                                operacionesPriorizadas)
        númerosMin = (1 + len(soluciónDeLongitudÓptima)) / 2
        númerosMax = 6 * númerosMin
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnEvaluar(genes):
            return evaluar(genes, operacionesPriorizadas)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, totalEsperado, fnEvaluar)

        def fnCrear():
            return crear(números, operaciones, númerosMin, númerosMax)

        def fnMutar(niño):
            mutar(niño, números, operaciones, númerosMin, númerosMax,
                  fnObtenerAptitud)

        aptitudÓptima = fnObtenerAptitud(soluciónDeLongitudÓptima)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, aptitudÓptima,
                                      None, fnMostrar, fnMutar, fnCrear,
                                      edadMáxima=50)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(self.test_exponente)


if __name__ == '__main__':
    unittest.main()
