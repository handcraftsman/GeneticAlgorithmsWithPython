# File: vendedor.py
#    Del capítulo 12 de _Algoritmos Genéticos con Python_
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
import unittest
from itertools import chain

import genetic


def obtener_aptitud(genes, búsquedaDeUbicación):
    aptitud = obtener_distancia(búsquedaDeUbicación[genes[0]],
                                búsquedaDeUbicación[genes[-1]])

    for i in range(len(genes) - 1):
        principio = búsquedaDeUbicación[genes[i]]
        end = búsquedaDeUbicación[genes[i + 1]]
        aptitud += obtener_distancia(principio, end)

    return Aptitud(round(aptitud, 2))


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}\t{}".format(
        ' '.join(map(str, candidato.Genes)),
        candidato.Aptitud,
        candidato.Estrategia.name,
        diferencia))


def obtener_distancia(ubicaciónA, ubicaciónB):
    ladoA = ubicaciónA[0] - ubicaciónB[0]
    ladoB = ubicaciónA[1] - ubicaciónB[1]
    ladoC = math.sqrt(ladoA * ladoA + ladoB * ladoB)
    return ladoC


def mutar(genes, fnObtenerAptitud):
    cuenta = random.randint(2, len(genes))
    aptitudInicial = fnObtenerAptitud(genes)
    while cuenta > 0:
        cuenta -= 1
        índiceA, índiceB = random.sample(range(len(genes)), 2)
        genes[índiceA], genes[índiceB] = genes[índiceB], genes[índiceA]
        aptitud = fnObtenerAptitud(genes)
        if aptitud > aptitudInicial:
            return


def intercambiar(genesDePadre, donanteGenes, fnObtenerAptitud):
    pares = {Par(donanteGenes[0], donanteGenes[-1]): 0}

    for i in range(len(donanteGenes) - 1):
        pares[Par(donanteGenes[i], donanteGenes[i + 1])] = 0

    genesTemporales = genesDePadre[:]
    if Par(genesDePadre[0], genesDePadre[-1]) in pares:
        # encontrar una discontinuidad
        encontró = False
        for i in range(len(genesDePadre) - 1):
            if Par(genesDePadre[i], genesDePadre[i + 1]) in pares:
                continue
            genesTemporales = genesDePadre[i + 1:] + genesDePadre[:i + 1]
            encontró = True
            break
        if not encontró:
            return None

    series = [[genesTemporales[0]]]
    for i in range(len(genesTemporales) - 1):
        if Par(genesTemporales[i], genesTemporales[i + 1]) in pares:
            series[-1].append(genesTemporales[i + 1])
            continue
        series.append([genesTemporales[i + 1]])

    aptitudInicial = fnObtenerAptitud(genesDePadre)
    cuenta = random.randint(2, 20)
    índicesDeSerie = range(len(series))
    while cuenta > 0:
        cuenta -= 1
        for i in índicesDeSerie:
            if len(series[i]) == 1:
                continue
            if random.randint(0, len(series)) == 0:
                series[i] = [n for n in reversed(series[i])]

        índiceA, índiceB = random.sample(índicesDeSerie, 2)
        series[índiceA], series[índiceB] = series[índiceB], series[índiceA]
        genesDelNiño = list(chain.from_iterable(series))
        if fnObtenerAptitud(genesDelNiño) > aptitudInicial:
            return genesDelNiño
    return genesDelNiño


class PruebasDeVendedorAmbulante(unittest.TestCase):
    def test_8_reinas(self):
        búsquedaDeUbicación = {
            'A': [4, 7],
            'B': [2, 6],
            'C': [0, 5],
            'D': [1, 3],
            'E': [3, 0],
            'F': [5, 1],
            'G': [7, 2],
            'H': [6, 4]
        }
        secuenciaÓptima = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.resolver(búsquedaDeUbicación, secuenciaÓptima)

    def test_ulysses16(self):
        búsquedaDeUbicación = cargar_datos("ulysses16.tsp")
        secuenciaÓptima = [14, 13, 12, 16, 1, 3, 2, 4,
                           8, 15, 5, 11, 9, 10, 7, 6]
        self.resolver(búsquedaDeUbicación, secuenciaÓptima)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test_ulysses16())

    def resolver(self, búsquedaDeUbicación, secuenciaÓptima):
        geneSet = [i for i in búsquedaDeUbicación.keys()]

        def fnCrear():
            return random.sample(geneSet, len(geneSet))

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, búsquedaDeUbicación)

        def fnMutar(genes):
            mutar(genes, fnObtenerAptitud)

        def fnIntercambio(padre, donante):
            return intercambiar(padre, donante, fnObtenerAptitud)

        aptitudÓptima = fnObtenerAptitud(secuenciaÓptima)
        horaInicio = datetime.datetime.now()
        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, aptitudÓptima,
                                      None, fnMostrar, fnMutar, fnCrear,
                                      edadMáxima=500, tamañoDePiscina=25,
                                      intercambiar=fnIntercambio)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)


def cargar_datos(archivoLocal):
    """ espera que:
        Sección de HEADER antes de la sección de DATA, todos los filas
        comienzan en columna 0
        Los elementos de la sección de DATA tienen un espacio en columna 0
            <espacio>1 23.45 67.89
        último fila de archivo es: " EOF"
    """
    with open(archivoLocal, mode='r') as fuente:
        contenido = fuente.read().splitlines()
    búsquedaDeUbicación = {}
    for fila in contenido:
        if fila[0] != ' ':  # HEADER
            continue
        if fila == " EOF":
            break

        id, x, y = fila.split(' ')[1:4]
        búsquedaDeUbicación[int(id)] = [float(x), float(y)]
    return búsquedaDeUbicación


class Aptitud:
    def __init__(self, distanciaTotal):
        self.DistanciaTotal = distanciaTotal

    def __gt__(self, otro):
        return self.DistanciaTotal < otro.DistanciaTotal

    def __str__(self):
        return "{:0.2f}".format(self.DistanciaTotal)


class Par:
    def __init__(self, nodo, adyacente):
        if nodo < adyacente:
            nodo, adyacente = adyacente, nodo
        self.Nodo = nodo
        self.Adyacente = adyacente

    def __eq__(self, otro):
        return self.Nodo == otro.Nodo and self.Adyacente == otro.Adyacente

    def __hash__(self):
        return hash(self.Nodo) * 397 ^ hash(self.Adyacente)


if __name__ == '__main__':
    unittest.main()
