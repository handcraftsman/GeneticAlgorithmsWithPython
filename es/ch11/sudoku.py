# File: sudoku.py
#    Del capítulo 11 de _Algoritmos Genéticos con Python_
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


def obtener_aptitud(genes, reglasDeValidación):
    try:
        primeraReglaQueFalla = next(regla for regla in reglasDeValidación
                                    if genes[regla.Índice] == genes[
                                        regla.OtroÍndice])
    except StopIteration:
        aptitud = 100
    else:
        aptitud = (1 + índice_fila(primeraReglaQueFalla.OtroÍndice)) * 10 \
                  + (1 + índice_columna(primeraReglaQueFalla.OtroÍndice))
    return aptitud


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()

    for filaId in range(9):
        fila = ' | '.join(
            ' '.join(str(i)
                     for i in
                     candidato.Genes[filaId * 9 + i:filaId * 9 + i + 3])
            for i in [0, 3, 6])
        print("", fila)
        if filaId < 8 and filaId % 3 == 2:
            print(" ----- + ----- + -----")
    print(" - = -   - = -   - = - {}\t{}\n"
          .format(candidato.Aptitud, diferencia))


def mutar(genes, reglasDeValidación):
    reglaSeleccionada = next(regla for regla in reglasDeValidación
                             if genes[regla.Índice] == genes[regla.OtroÍndice])
    if reglaSeleccionada is None:
        return

    if índice_fila(reglaSeleccionada.OtroÍndice) % 3 == 2 \
            and random.randint(0, 10) == 0:
        secciónPrincipio = sección_principio(reglaSeleccionada.Índice)
        actual = reglaSeleccionada.OtroÍndice
        while reglaSeleccionada.OtroÍndice == actual:
            barajar_en_su_lugar(genes, secciónPrincipio, 80)
            reglaSeleccionada = next(regla for regla in reglasDeValidación
                                     if genes[regla.Índice] == genes[
                                         regla.OtroÍndice])
        return
    fila = índice_fila(reglaSeleccionada.OtroÍndice)
    principio = fila * 9
    índiceA = reglaSeleccionada.OtroÍndice
    índiceB = random.randrange(principio, len(genes))
    genes[índiceA], genes[índiceB] = genes[índiceB], genes[índiceA]


def barajar_en_su_lugar(genes, primero, último):
    while primero < último:
        índice = random.randint(primero, último)
        genes[primero], genes[índice] = genes[índice], genes[primero]
        primero += 1


class PruebasDeSudoku(unittest.TestCase):
    def test(self):
        geneSet = [i for i in range(1, 9 + 1)]
        horaInicio = datetime.datetime.now()
        valorÓptimo = 100

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        reglasDeValidación = construir_las_reglas_de_validación()

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, reglasDeValidación)

        def fnCrear():
            return random.sample(geneSet * 9, 81)

        def fnMutar(genes):
            mutar(genes, reglasDeValidación)

        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, valorÓptimo,
                                      None, fnMostrar, fnMutar, fnCrear,
                                      edadMáxima=50)
        self.assertEqual(mejor.Aptitud, valorÓptimo)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test())


def construir_las_reglas_de_validación():
    reglas = []
    for índice in range(80):
        suFila = índice_fila(índice)
        suColumna = índice_columna(índice)
        suSección = fila_columna_sección(suFila, suColumna)

        for índice2 in range(índice + 1, 81):
            otroFila = índice_fila(índice2)
            otroColumna = índice_columna(índice2)
            otroSección = fila_columna_sección(otroFila, otroColumna)
            if suFila == otroFila or \
                            suColumna == otroColumna or \
                            suSección == otroSección:
                reglas.append(Regla(índice, índice2))

    reglas.sort(key=lambda x: x.OtroÍndice * 100 + x.Índice)
    return reglas


def índice_fila(índice):
    return int(índice / 9)


def índice_columna(índice):
    return int(índice % 9)


def fila_columna_sección(fila, columna):
    return int(fila / 3) * 3 + int(columna / 3)


def índice_sección(índice):
    return fila_columna_sección(índice_fila(índice), índice_columna(índice))


def sección_principio(índice):
    return int((índice_fila(índice) % 9) / 3) * 27 + int(
        índice_columna(índice) / 3) * 3


class Regla:
    def __init__(self, eso, otro):
        if eso > otro:
            eso, otro = otro, eso
        self.Índice = eso
        self.OtroÍndice = otro

    def __eq__(self, otro):
        return self.Índice == otro.Índice and \
               self.OtroÍndice == otro.OtroÍndice

    def __hash__(self):
        return self.Índice * 100 + self.OtroÍndice


if __name__ == '__main__':
    unittest.main()
