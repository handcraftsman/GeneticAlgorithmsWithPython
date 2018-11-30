# File: genetic.py
#    Del capítulo 1 de _Algoritmos Genéticos con Python_
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

import random
import statistics
import sys
import time


def _generar_padre(longitud, geneSet, obtener_aptitud):
    genes = []
    while len(genes) < longitud:
        tamañoMuestral = min(longitud - len(genes), len(geneSet))
        genes.extend(random.sample(geneSet, tamañoMuestral))
    genes = ''.join(genes)
    aptitud = obtener_aptitud(genes)
    return Cromosoma(genes, aptitud)


def _mutar(padre, geneSet, obtener_aptitud):
    índice = random.randrange(0, len(padre.Genes))
    genesDelNiño = list(padre.Genes)
    nuevoGen, alterno = random.sample(geneSet, 2)
    genesDelNiño[índice] = alterno if nuevoGen == genesDelNiño[
        índice] else nuevoGen
    genes = ''.join(genesDelNiño)
    aptitud = obtener_aptitud(genes)
    return Cromosoma(genes, aptitud)


def obtener_mejor(obtener_aptitud, longitudObjetivo, aptitudÓptima, geneSet,
                  mostrar):
    random.seed()
    mejorPadre = _generar_padre(longitudObjetivo, geneSet, obtener_aptitud)
    mostrar(mejorPadre)
    if mejorPadre.Aptitud >= aptitudÓptima:
        return mejorPadre
    while True:
        niño = _mutar(mejorPadre, geneSet, obtener_aptitud)
        if mejorPadre.Aptitud >= niño.Aptitud:
            continue
        mostrar(niño)
        if niño.Aptitud >= aptitudÓptima:
            return niño
        mejorPadre = niño


class Cromosoma:
    def __init__(self, genes, aptitud):
        self.Genes = genes
        self.Aptitud = aptitud


class Comparar:
    @staticmethod
    def ejecutar(función):
        print(función)
        cronometrajes = []
        stdout = sys.stdout
        for i in range(100):
            sys.stdout = None
            horaInicio = time.time()
            función()
            segundos = time.time() - horaInicio
            sys.stdout = stdout
            cronometrajes.append(segundos)
            promedio = statistics.mean(cronometrajes)
            if i < 10 or i % 10 == 9:
                print("{} {:3.2f} {:3.2f}".format(
                    1 + i, promedio,
                    statistics.stdev(cronometrajes,
                                     promedio) if i > 1 else 0))
