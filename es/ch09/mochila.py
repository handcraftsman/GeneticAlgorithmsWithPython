# File: mochila.py
#    Del capítulo 9 de _Algoritmos Genéticos con Python_
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
import sys
import unittest

import genetic


def obtener_aptitud(genes):
    pesoTotal = 0
    volumenTotal = 0
    valorTotal = 0
    for ac in genes:
        cuenta = ac.Cantidad
        pesoTotal += ac.Artículo.Peso * cuenta
        volumenTotal += ac.Artículo.Volumen * cuenta
        valorTotal += ac.Artículo.Valor * cuenta

    return Aptitud(pesoTotal, volumenTotal, valorTotal)


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    genes = candidato.Genes[:]
    genes.sort(key=lambda ac: ac.Cantidad, reverse=True)

    descripciones = [str(ac.Cantidad) + "x" + ac.Artículo.Nombre for ac in
                     genes]
    if len(descripciones) == 0:
        descripciones.append("Vacío")
    print("{}\t{}\t{}".format(
        ', '.join(descripciones),
        candidato.Aptitud,
        diferencia))


def cantidad_máxima(artículo, pesoMáximo, volumenMáximo):
    return min(int(pesoMáximo / artículo.Peso)
               if artículo.Peso > 0 else sys.maxsize,
               int(volumenMáximo / artículo.Volumen)
               if artículo.Volumen > 0 else sys.maxsize)


def crear(artículos, pesoMáximo, volumenMáximo):
    genes = []
    pesoRestante, volumenRestante = pesoMáximo, volumenMáximo
    for i in range(random.randrange(1, len(artículos))):
        nuevoGen = añadir(genes, artículos, pesoRestante, volumenRestante)
        if nuevoGen is not None:
            genes.append(nuevoGen)
            pesoRestante -= nuevoGen.Cantidad * nuevoGen.Artículo.Peso
            volumenRestante -= nuevoGen.Cantidad * nuevoGen.Artículo.Volumen
    return genes


def añadir(genes, artículos, pesoMáximo, volumenMáximo):
    artículosUsados = {ac.Artículo for ac in genes}
    artículo = random.choice(artículos)
    while artículo in artículosUsados:
        artículo = random.choice(artículos)

    cantidadMáxima = cantidad_máxima(artículo, pesoMáximo, volumenMáximo)
    return ArtículoCantidad(artículo,
                            cantidadMáxima) if cantidadMáxima > 0 else None


def mutar(genes, artículos, pesoMáximo, volumenMáximo, ventana):
    ventana.deslizar()
    aptitud = obtener_aptitud(genes)
    pesoRestante = pesoMáximo - aptitud.PesoTotal
    volumenRestante = volumenMáximo - aptitud.VolumenTotal

    eliminando = len(genes) > 1 and random.randint(0, 10) == 0
    if eliminando:
        índice = random.randrange(0, len(genes))
        ac = genes[índice]
        artículo = ac.Artículo
        pesoRestante += artículo.Peso * ac.Cantidad
        volumenRestante += artículo.Volumen * ac.Cantidad
        del genes[índice]

    añadiendo = (pesoRestante > 0 or volumenRestante > 0) and \
                (len(genes) == 0 or (len(genes) < len(artículos) and
                                     random.randint(0, 100) == 0))

    if añadiendo:
        nuevoGen = añadir(genes, artículos, pesoRestante, volumenRestante)
        if nuevoGen is not None:
            genes.append(nuevoGen)
            return

    índice = random.randrange(0, len(genes))
    ac = genes[índice]
    artículo = ac.Artículo
    pesoRestante += artículo.Peso * ac.Cantidad
    volumenRestante += artículo.Volumen * ac.Cantidad

    artículoACambiar = len(genes) < len(artículos) and \
                       random.randint(0, 4) == 0
    if artículoACambiar:
        artículoÍndice = artículos.index(ac.Artículo)
        principio = max(1, artículoÍndice - ventana.Tamaño)
        fin = min(len(artículos) - 1, artículoÍndice + ventana.Tamaño)
        artículo = artículos[random.randint(principio, fin)]
    cantidadMáxima = cantidad_máxima(artículo, pesoRestante, volumenRestante)
    if cantidadMáxima > 0:
        genes[índice] = ArtículoCantidad(artículo, cantidadMáxima
        if ventana.Tamaño > 1 else random.randint(1, cantidadMáxima))
    else:
        del genes[índice]


class PruebasDeMochila(unittest.TestCase):
    def test_galletas(self):
        artículos = [
            Recurso("Harina", 1680, 0.265, .41),
            Recurso("Mantequilla", 1440, 0.5, .13),
            Recurso("Azúcar", 1840, 0.441, .29)
        ]
        pesoMáximo = 10
        volumenMáximo = 4
        óptimo = obtener_aptitud(
            [ArtículoCantidad(artículos[0], 1),
             ArtículoCantidad(artículos[1], 14),
             ArtículoCantidad(artículos[2], 6)])
        self.rellenar_mochila(artículos, pesoMáximo, volumenMáximo, óptimo)

    def test_exnsd16(self):
        informaciónDelProblema = cargar_datos("exnsd16.ukp")
        artículos = informaciónDelProblema.Recursos
        pesoMáximo = informaciónDelProblema.PesoMáximo
        volumenMáximo = 0
        óptimo = obtener_aptitud(informaciónDelProblema.Solución)
        self.rellenar_mochila(artículos, pesoMáximo, volumenMáximo, óptimo)

    def test_comparativa(self):
        genetic.Comparar.ejecutar(lambda: self.test_exnsd16())

    def rellenar_mochila(self, artículos, pesoMáximo, volumenMáximo,
                         aptitudÓptima):
        horaInicio = datetime.datetime.now()
        ventana = Ventana(1,
                          max(1, int(len(artículos) / 3)),
                          int(len(artículos) / 2))

        artículosOrdenados = sorted(artículos,
                                    key=lambda artículo: artículo.Valor)

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes)

        def fnCrear():
            return crear(artículos, pesoMáximo, volumenMáximo)

        def fnMutar(genes):
            mutar(genes, artículosOrdenados, pesoMáximo, volumenMáximo,
                  ventana)

        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, aptitudÓptima,
                                      None, fnMostrar, fnMutar, fnCrear,
                                      edadMáxima=50)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)


def cargar_datos(archivoLocal):
    with open(archivoLocal, mode='r') as fuente:
        filas = fuente.read().splitlines()
    datos = DatosDelProblema()
    f = encontrar_restricción

    for fila in filas:
        f = f(fila.strip(), datos)
        if f is None:
            break
    return datos


def encontrar_restricción(fila, datos):
    partes = fila.split(' ')
    if partes[0] != "c:":
        return encontrar_restricción
    datos.PesoMáximo = int(partes[1])
    return buscar_inicio_de_datos


def buscar_inicio_de_datos(fila, datos):
    if fila != "begin data":
        return buscar_inicio_de_datos
    return leer_recurso_o_encontrar_final_de_datos


def leer_recurso_o_encontrar_final_de_datos(fila, datos):
    if fila == "end data":
        return encontrar_inicio_de_la_solución
    partes = fila.split('\t')
    recurso = Recurso("R" + str(1 + len(datos.Recursos)), int(partes[1]),
                      int(partes[0]), 0)
    datos.Recursos.append(recurso)
    return leer_recurso_o_encontrar_final_de_datos


def encontrar_inicio_de_la_solución(fila, datos):
    if fila == "sol:":
        return leer_solución_recurso_o_encontrar_final_de_solución
    return encontrar_inicio_de_la_solución


def leer_solución_recurso_o_encontrar_final_de_solución(fila, datos):
    if fila == "":
        return None
    partes = [p for p in fila.split('\t') if p != ""]
    recursoÍndice = int(partes[0]) - 1  # hacer que sea basado en 0
    recursoCantidad = int(partes[1])
    datos.Solución.append(
        ArtículoCantidad(datos.Recursos[recursoÍndice], recursoCantidad))
    return leer_solución_recurso_o_encontrar_final_de_solución


class Recurso:
    def __init__(self, nombre, valor, peso, volumen):
        self.Nombre = nombre
        self.Valor = valor
        self.Peso = peso
        self.Volumen = volumen


class ArtículoCantidad:
    def __init__(self, artículo, cantidad):
        self.Artículo = artículo
        self.Cantidad = cantidad

    def __eq__(self, otro):
        return self.Artículo == otro.Artículo and \
               self.Cantidad == otro.Cantidad


class Aptitud:
    def __init__(self, pesoTotal, volumenTotal, valorTotal):
        self.PesoTotal = pesoTotal
        self.VolumenTotal = volumenTotal
        self.ValorTotal = valorTotal

    def __gt__(self, otro):
        if self.ValorTotal != otro.ValorTotal:
            return self.ValorTotal > otro.ValorTotal
        if self.PesoTotal != otro.PesoTotal:
            return self.PesoTotal < otro.PesoTotal
        return self.VolumenTotal < otro.VolumenTotal

    def __str__(self):
        return "peso: {:0.2f} vol: {:0.2f} valor: {}".format(
            self.PesoTotal,
            self.VolumenTotal,
            self.ValorTotal)


class DatosDelProblema:
    def __init__(self):
        self.Recursos = []
        self.PesoMáximo = 0
        self.Solución = []


class Ventana:
    def __init__(self, mínimo, máximo, tamaño):
        self.Min = mínimo
        self.Max = máximo
        self.Tamaño = tamaño

    def deslizar(self):
        self.Tamaño = self.Tamaño - 1 if self.Tamaño > self.Min else self.Max


if __name__ == '__main__':
    unittest.main()
