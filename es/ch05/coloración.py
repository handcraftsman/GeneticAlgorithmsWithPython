# File: coloración.py
#    Del capítulo 5 de _Algoritmos Genéticos con Python_
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


def cargar_datos(archivoLocal):
    """ espera: T D1 [D2 ... DN]
        donde T es el tipo de registro
        y D1 .. DN son elementos de datos apropiados del tipo de registro
    """
    reglas = set()
    nodos = set()
    with open(archivoLocal, mode='r') as fuente:
        contenido = fuente.read().splitlines()
    for fila in contenido:
        if fila[0] == 'e':  # e aa bb, aa y bb son identificadores de nodo
            nodoIds = fila.split(' ')[1:3]
            reglas.add(Regla(nodoIds[0], nodoIds[1]))
            nodos.add(nodoIds[0])
            nodos.add(nodoIds[1])
            continue
        if fila[0] == 'n':  
        # n aa ww, aa es un identificador de nodo, ww es un peso
            nodoIds = fila.split(' ')
            nodos.add(nodoIds[1])
    return reglas, nodos


def construir_reglas(artículos):
    reglasAñadidas = {}
    for país, adyacente in artículos.items():
        for paísAdyacente in adyacente:
            if paísAdyacente == '':
                continue
            regla = Regla(país, paísAdyacente)
            if regla in reglasAñadidas:
                reglasAñadidas[regla] += 1
            else:
                reglasAñadidas[regla] = 1
    for k, v in reglasAñadidas.items():
        if v != 2:
            print("regla {} no es bidireccional".format(k))
    return reglasAñadidas.keys()


def obtener_aptitud(genes, reglas, búsquedaÍndicePaís):
    reglasQuePasan = sum(1 for regla in reglas
                         if regla.EsVálida(genes, búsquedaÍndicePaís))
    return reglasQuePasan


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}".format(
        ''.join(map(str, candidato.Genes)),
        candidato.Aptitud,
        diferencia))


# `nosetests` no admite caracteres como ó y á en el nombre de la clase
class PruebasDeColoracionGrafica(unittest.TestCase):
    def test_países(self):
        self.color("países_españoles.col",
                   ["Naranja", "Amarillo", "Verde", "Rojo"])

    def test_R100_1gb(self):
        self.color("R100_1gb.col",
                   ["Dorado", "Naranja", "Amarillo", "Verde", "Rojo", "Morado"])

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test_R100_1gb())

    def color(self, file, colores):
        reglas, nodos = cargar_datos(file)
        valorÓptimo = len(reglas)
        búsquedaDeColor = {color[0]: color for color in colores}
        geneSet = list(búsquedaDeColor.keys())
        horaInicio = datetime.datetime.now()
        búsquedaDeÍndiceDeNodo = {key: índice
                                  for índice, key in enumerate(sorted(nodos))}

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, reglas, búsquedaDeÍndiceDeNodo)

        mejor = genetic.obtener_mejor(fnObtenerAptitud, len(nodos),
                                      valorÓptimo, geneSet, fnMostrar)
        self.assertTrue(not valorÓptimo > mejor.Aptitud)

        llaves = sorted(nodos)
        for índice in range(len(nodos)):
            print(
                llaves[índice] + " es " + búsquedaDeColor[mejor.Genes[índice]])


class Regla:
    def __init__(self, nodo, adyacente):
        if nodo < adyacente:
            nodo, adyacente = adyacente, nodo
        self.Nodo = nodo
        self.Adyacente = adyacente

    def __eq__(self, otro):
        return self.Nodo == otro.Nodo and self.Adyacente == otro.Adyacente

    def __hash__(self):
        return hash(self.Nodo) * 397 ^ hash(self.Adyacente)

    def __str__(self):
        return self.Nodo + " -> " + self.Adyacente

    def EsVálida(self, genes, búsquedaDeÍndiceDeNodo):
        índice = búsquedaDeÍndiceDeNodo[self.Nodo]
        índiceDeNodosAdyacentes = búsquedaDeÍndiceDeNodo[self.Adyacente]

        return genes[índice] != genes[índiceDeNodosAdyacentes]


if __name__ == '__main__':
    unittest.main()
