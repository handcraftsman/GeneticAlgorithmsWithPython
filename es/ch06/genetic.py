# File: genetic.py
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

import random
import statistics
import sys
import time


def _generar_padre(longitud, geneSet, obtener_aptitud):
    genes = []
    while len(genes) < longitud:
        tamañoMuestral = min(longitud - len(genes), len(geneSet))
        genes.extend(random.sample(geneSet, tamañoMuestral))
    aptitud = obtener_aptitud(genes)
    return Cromosoma(genes, aptitud)


def _mutar(padre, geneSet, obtener_aptitud):
    genesDelNiño = padre.Genes[:]
    índice = random.randrange(0, len(padre.Genes))
    nuevoGen, alterno = random.sample(geneSet, 2)
    genesDelNiño[índice] = alterno if nuevoGen == genesDelNiño[
        índice] else nuevoGen
    aptitud = obtener_aptitud(genesDelNiño)
    return Cromosoma(genesDelNiño, aptitud)


def _mutar_personalizada(padre, mutación_personalizada, obtener_aptitud):
    genesDelNiño = padre.Genes[:]
    mutación_personalizada(genesDelNiño)
    aptitud = obtener_aptitud(genesDelNiño)
    return Cromosoma(genesDelNiño, aptitud)


def obtener_mejor(obtener_aptitud, longitudObjetivo, aptitudÓptima, geneSet,
                  mostrar, mutación_personalizada=None):
    if mutación_personalizada is None:
        def fnMutar(padre):
            return _mutar(padre, geneSet, obtener_aptitud)
    else:
        def fnMutar(padre):
            return _mutar_personalizada(padre, mutación_personalizada,
                                        obtener_aptitud)

    def fnGenerarPadre():
        return _generar_padre(longitudObjetivo, geneSet, obtener_aptitud)

    for mejora in _obtener_mejoras(fnMutar, fnGenerarPadre):
        mostrar(mejora)
        if not aptitudÓptima > mejora.Aptitud:
            return mejora


def _obtener_mejoras(nuevo_niño, generar_padre):
    mejorPadre = generar_padre()
    yield mejorPadre
    while True:
        niño = nuevo_niño(mejorPadre)
        if mejorPadre.Aptitud > niño.Aptitud:
            continue
        if not niño.Aptitud > mejorPadre.Aptitud:
            mejorPadre = niño
            continue
        yield niño
        mejorPadre = niño


class Cromosoma:
    def __init__(self, genes, aptitud):
        self.Genes = genes
        self.Aptitud = aptitud


class Comparar:
    @staticmethod
    def ejecutar(función):
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
                    statistics.stdev(cronometrajes, promedio) if i > 1 else 0))
