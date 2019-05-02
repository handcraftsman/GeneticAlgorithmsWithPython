# File: genetic.py
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

import random
import statistics
import sys
import time
from bisect import bisect_left
from enum import Enum
from math import exp


def _generar_padre(longitud, geneSet, obtener_aptitud):
    genes = []
    while len(genes) < longitud:
        tamañoMuestral = min(longitud - len(genes), len(geneSet))
        genes.extend(random.sample(geneSet, tamañoMuestral))
    aptitud = obtener_aptitud(genes)
    return Cromosoma(genes, aptitud, Estrategias.Creación)


def _mudar(padre, geneSet, obtener_aptitud):
    genesDelNiño = padre.Genes[:]
    índice = random.randrange(0, len(padre.Genes))
    nuevoGen, alterno = random.sample(geneSet, 2)
    genesDelNiño[índice] = alterno if nuevoGen == genesDelNiño[
        índice] else nuevoGen
    aptitud = obtener_aptitud(genesDelNiño)
    return Cromosoma(genesDelNiño, aptitud, Estrategias.Mutación)


def _mudar_personalizada(padre, mutación_personalizada, obtener_aptitud):
    genesDelNiño = padre.Genes[:]
    mutación_personalizada(genesDelNiño)
    aptitud = obtener_aptitud(genesDelNiño)
    return Cromosoma(genesDelNiño, aptitud, Estrategias.Mutación)


def _intercambiar(genesDePadre, índice, padres, obtener_aptitud, intercambiar,
                  mudar, generar_padre):
    índiceDeDonante = random.randrange(0, len(padres))
    if índiceDeDonante == índice:
        índiceDeDonante = (índiceDeDonante + 1) % len(padres)
    genesDelNiño = intercambiar(genesDePadre, padres[índiceDeDonante].Genes)
    if genesDelNiño is None:
        # padre y donante son indistinguibles
        padres[índiceDeDonante] = generar_padre()
        return mudar(padres[índice])
    aptitud = obtener_aptitud(genesDelNiño)
    return Cromosoma(genesDelNiño, aptitud, Estrategias.Intercambio)


def obtener_mejor(obtener_aptitud, longitudObjetivo, aptitudÓptima, geneSet,
                  mostrar, mutación_personalizada=None,
                  creación_personalizada=None, edadMáxima=None,
                  tamañoDePiscina=1, intercambiar=None, segundosMáximos=None):
    if mutación_personalizada is None:
        def fnMudar(padre):
            return _mudar(padre, geneSet, obtener_aptitud)
    else:
        def fnMudar(padre):
            return _mudar_personalizada(padre, mutación_personalizada,
                                        obtener_aptitud)

    if creación_personalizada is None:
        def fnGenerarPadre():
            return _generar_padre(longitudObjetivo, geneSet, obtener_aptitud)
    else:
        def fnGenerarPadre():
            genes = creación_personalizada()
            return Cromosoma(genes, obtener_aptitud(genes),
                             Estrategias.Creación)

    búsquedaDeEstrategia = {
        Estrategias.Creación: lambda p, i, o: fnGenerarPadre(),
        Estrategias.Mutación: lambda p, i, o: fnMudar(p),
        Estrategias.Intercambio: lambda p, i, o:
        _intercambiar(p.Genes, i, o, obtener_aptitud, intercambiar, fnMudar,
                      fnGenerarPadre)
    }

    estrategiasUsadas = [búsquedaDeEstrategia[Estrategias.Mutación]]
    if intercambiar is not None:
        estrategiasUsadas.append(búsquedaDeEstrategia[Estrategias.Intercambio])

        def fnNuevoNiño(padre, índice, padres):
            return random.choice(estrategiasUsadas)(padre, índice, padres)
    else:
        def fnNuevoNiño(padre, índice, padres):
            return fnMudar(padre)

    for caducado, mejora in _obtener_mejoras(fnNuevoNiño, fnGenerarPadre,
                                             edadMáxima, tamañoDePiscina,
                                             segundosMáximos):
        if caducado:
            return mejora
        mostrar(mejora)
        f = búsquedaDeEstrategia[mejora.Estrategia]
        estrategiasUsadas.append(f)
        if not aptitudÓptima > mejora.Aptitud:
            return mejora


def _obtener_mejoras(nuevo_niño, generar_padre, edadMáxima, tamañoDePiscina,
                     segundosMáximos):
    horaInicio = time.time()
    mejorPadre = generar_padre()
    yield segundosMáximos is not None and time.time() \
          - horaInicio > segundosMáximos, mejorPadre
    padres = [mejorPadre]
    aptitudesHistóricas = [mejorPadre.Aptitud]
    for _ in range(tamañoDePiscina - 1):
        padre = generar_padre()
        if segundosMáximos is not None and time.time() - horaInicio > \
                segundosMáximos:
            yield True, padre
        if padre.Aptitud > mejorPadre.Aptitud:
            yield False, padre
            mejorPadre = padre
            aptitudesHistóricas.append(padre.Aptitud)
        padres.append(padre)
    índiceDelÚltimoPadre = tamañoDePiscina - 1
    pÍndice = 1
    while True:
        if segundosMáximos is not None and time.time() - horaInicio > \
                segundosMáximos:
            yield True, mejorPadre
        pÍndice = pÍndice - 1 if pÍndice > 0 else índiceDelÚltimoPadre
        padre = padres[pÍndice]
        niño = nuevo_niño(padre, pÍndice, padres)
        if padre.Aptitud > niño.Aptitud:
            if edadMáxima is None:
                continue
            padre.Edad += 1
            if edadMáxima > padre.Edad:
                continue
            índice = bisect_left(aptitudesHistóricas, niño.Aptitud, 0,
                                 len(aptitudesHistóricas))
            proporciónSimilar = índice / len(aptitudesHistóricas)
            if random.random() < exp(-proporciónSimilar):
                padres[pÍndice] = niño
                continue
            padres[pÍndice] = mejorPadre
            padre.Edad = 0
            continue
        if not niño.Aptitud > padre.Aptitud:
            # mismo aptitud
            niño.Edad = padre.Edad + 1
            padres[pÍndice] = niño
            continue
        padres[pÍndice] = niño
        padre.Edad = 0
        if niño.Aptitud > mejorPadre.Aptitud:
            yield False, niño
            mejorPadre = niño
            aptitudesHistóricas.append(niño.Aptitud)


class Cromosoma:
    def __init__(self, genes, aptitud, estrategia):
        self.Genes = genes
        self.Aptitud = aptitud
        self.Estrategia = estrategia
        self.Edad = 0


class Estrategias(Enum):
    Creación = 0,
    Mutación = 1,
    Intercambio = 2


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
