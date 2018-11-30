# File: ticTacToe.py
#    Del capítulo 18 de _Algoritmos Genéticos con Python_
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
from functools import partial

import genetic


def obtener_aptitud(genes):
    copiaLocal = genes[:]
    aptitud = obtener_aptitud_para_juegos(copiaLocal)
    aptitud.ConteoDeGenes = len(genes)
    return aptitud


índicesDeCuadrados = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def jugar1en1(xGenes, oGenes):
    tablero = dict((i, Cuadrado(i, TipoDeContenido.Vacío)) for i in range(1, 9 + 1))
    vacíos = [v for v in tablero.values() if v.Contenido == TipoDeContenido.Vacío]
    datosDeRonda = [[xGenes, TipoDeContenido.Mia, genetic.ResultadoDeCompetición.Perdido,
                  genetic.ResultadoDeCompetición.Ganado],
                 [oGenes, TipoDeContenido.Oponente, genetic.ResultadoDeCompetición.Ganado,
                  genetic.ResultadoDeCompetición.Perdido]]
    índiceDelJugador = 0

    while len(vacíos) > 0:
        datosDelJugador = datosDeRonda[índiceDelJugador]
        índiceDelJugador = 1 - índiceDelJugador
        genes, pieza, perdió, ganó = datosDelJugador

        índiceDeReglaYMovimiento = obtener_mover(genes, tablero, vacíos)
        if índiceDeReglaYMovimiento is None:  # no pudo encontrar un movimiento
            return perdió

        índice = índiceDeReglaYMovimiento[0]
        tablero[índice] = Cuadrado(índice, pieza)

        sóloElMovimientoMásReciente = [tablero[índice]]
        if len(FiltroDeContenidoDeFila(pieza, 3).obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0 or \
           len(FiltroDeContenidoDeColumna(pieza, 3).obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0 or \
           len(DiagonalContenidoFilter(pieza, 3).obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0:
            return ganó
        vacíos = [v for v in tablero.values() if v.Contenido == TipoDeContenido.Vacío]
    return genetic.ResultadoDeCompetición.Empatado


def obtener_aptitud_para_juegos(genes):
    def obtenerCadenaDelTablero(b):
        return ''.join(map(lambda i:
                           '.' if b[i].Contenido == TipoDeContenido.Vacío
                           else 'x' if b[i].Contenido == TipoDeContenido.Mia
                           else 'o', índicesDeCuadrados))

    tablero = dict((i, Cuadrado(i, TipoDeContenido.Vacío)) for i in range(1, 9 + 1))

    cola = [tablero]
    for cuadrado in tablero.values():
        copiaDelCandidato = tablero.copy()
        copiaDelCandidato[cuadrado.Índice] = Cuadrado(cuadrado.Índice, TipoDeContenido.Oponente)
        cola.append(copiaDelCandidato)

    reglasGanadoras = {}
    ganados = empates = perdidos = 0

    while len(cola) > 0:
        tablero = cola.pop()
        cadenaDelTablero = obtenerCadenaDelTablero(tablero)
        vacíos = [v for v in tablero.values() if v.Contenido == TipoDeContenido.Vacío]

        if len(vacíos) == 0:
            empates += 1
            continue

        candidatoÍndiceAndReglaÍndice = obtener_mover(genes, tablero, vacíos)

        if candidatoÍndiceAndReglaÍndice is None:  # no pudo encontrar un movimiento
            # hay vacíos pero no encontró un movimiento
            perdidos += 1
            # ir al siguiente tablero
            continue

        # encontró al menos un movimiento
        índice = candidatoÍndiceAndReglaÍndice[0]
        tablero[índice] = Cuadrado(índice, TipoDeContenido.Mia)
        # newTableroString = obtenerCadenaDelTablero(tablero)

        # Si ahora tenemos tres de mis piezas en cualquier fila, columna o diagonal, ganamos
        sóloElMovimientoMásReciente = [tablero[índice]]
        if len(tengoTresEnUnaFila.obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0 or \
             len(tengoTresEnUnaColumna.obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0 or \
             len(tengoTresEnDiagonal.obtener_coincidencias(tablero, sóloElMovimientoMásReciente)) > 0:
            reglaId = candidatoÍndiceAndReglaÍndice[1]
            if reglaId not in reglasGanadoras:
                reglasGanadoras[reglaId] = list()
            reglasGanadoras[reglaId].append(cadenaDelTablero)
            ganados += 1
            # ir al siguiente tablero
            continue

        # perdemos si vacíos tienen dos piezas opositoras en una fila, columna o diagonal
        vacíos = [v for v in tablero.values() if v.Contenido == TipoDeContenido.Vacío]
        if len(oponenteTieneDosEnUnaFila.obtener_coincidencias(tablero, vacíos)) > 0:
            perdidos += 1
            # ir al siguiente tablero
            continue

        # poner en cola todas las posibles respuestas de los oponentes
        for cuadrado in vacíos:
            copiaDelCandidato = tablero.copy()
            copiaDelCandidato[cuadrado.Índice] = Cuadrado(cuadrado.Índice,
                                                TipoDeContenido.Oponente)
            cola.append(copiaDelCandidato)

    return Aptitud(ganados, empates, perdidos, len(genes))


def obtener_mover(reglaSet, tablero, vacíos, índiceDePrimeraRegla=0):
    copiaDeReglas = reglaSet[:]

    for reglaÍndice in range(índiceDePrimeraRegla, len(copiaDeReglas)):
        gene = copiaDeReglas[reglaÍndice]
        coincidencias = gene.obtener_coincidencias(tablero, vacíos)
        if len(coincidencias) == 0:
            continue
        if len(coincidencias) == 1:
            return [list(coincidencias)[0], reglaÍndice]
        if len(vacíos) > len(coincidencias):
            vacíos = [e for e in vacíos if e.Índice in coincidencias]

    return None


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    copiaLocal = candidato.Genes[:]
    for i in reversed(range(len(copiaLocal))):
        copiaLocal[i] = str(copiaLocal[i])

    print("\t{}\n{}\n{}".format(
        '\n\t'.join([d for d in copiaLocal]),
        candidato.Aptitud,
        diferencia))


def mutar_añadir(genes, geneSet):
    índice = random.randrange(0, len(genes) + 1) if len(genes) > 0 else 0
    genes[índice:índice] = [random.choice(geneSet)]
    return True


def mutar_remover(genes):
    if len(genes) < 1:
        return False
    del genes[random.randrange(0, len(genes))]
    if len(genes) > 1 and random.randint(0, 1) == 1:
        del genes[random.randrange(0, len(genes))]
    return True


def mutar_reemplazar(genes, geneSet):
    if len(genes) < 1:
        return False
    índice = random.randrange(0, len(genes))
    genes[índice] = random.choice(geneSet)
    return True


def mutar_intercambiar_adyacente(genes):
    if len(genes) < 2:
        return False
    índice = random.choice(range(len(genes) - 1))
    genes[índice], genes[índice + 1] = genes[índice + 1], genes[índice]
    return True


def mutar_mover(genes):
    if len(genes) < 3:
        return False
    principio = random.choice(range(len(genes)))
    fin = principio + random.randint(1, 2)
    aMover = genes[principio:fin]
    genes[principio:fin] = []
    índice = random.choice(range(len(genes)))
    if índice >= principio:
        índice += 1
    genes[índice:índice] = aMover
    return True


def mutar(genes, fnObtenerAptitud, operadoresDeMutación, recuentoDeMutaciones):
    aptitudInicial = fnObtenerAptitud(genes)
    cuenta = random.choice(recuentoDeMutaciones)
    for i in range(1, cuenta + 2):
        duplo = operadoresDeMutación[:]
        func = random.choice(duplo)
        while not func(genes):
            duplo.remove(func)
            func = random.choice(duplo)
        if fnObtenerAptitud(genes) > aptitudInicial:
            recuentoDeMutaciones.append(i)
            return


def crear_geneSet():
    opciones = [[TipoDeContenido.Oponente, [0, 1, 2]],
               [TipoDeContenido.Mia, [0, 1, 2]]]
    geneSet = [
        ReglaMetadatos(FiltroDeContenidoDeFila, opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeFilaSuperior(), opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeFilaDelMedio(),
                     opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeFilaInferior(),
                     opciones),
        ReglaMetadatos(FiltroDeContenidoDeColumna, opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeColumnaIzquierda(),
                     opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeColumnaMedia(),
                     opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeColumnaDerecha(),
                     opciones),
        ReglaMetadatos(DiagonalContenidoFilter, opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeUbicaciónDiagonal(),
                     opciones),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeEsquina()),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeLado()),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroCentral()),
        ReglaMetadatos(lambda contenidoEsperado, cuenta:
                     FiltroDeOpuestosDeFila(contenidoEsperado), opciones,
                     necesitaContenidoEspecífico=True),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeOpuestosDeColumna(
            contenidoEsperado), opciones, necesitaContenidoEspecífico=True),
        ReglaMetadatos(lambda contenidoEsperado, cuenta: FiltroDeOpuestosDeDiagonal(
            contenidoEsperado), opciones, necesitaContenidoEspecífico=True),
    ]

    genes = list()
    for gene in geneSet:
        genes.extend(gene.crear_reglas())

    print("creado " + str(len(genes)) + " genes")
    return genes


class TicTacToeTests(unittest.TestCase):
    def test_conocimiento_perfecto(self):
        mínGenes = 10
        máxGenes = 20
        geneSet = crear_geneSet()
        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes)

        recuentoDeMutaciones = [1]

        operadoresDeMutación = [
            partial(mutar_añadir, geneSet=geneSet),
            partial(mutar_reemplazar, geneSet=geneSet),
            mutar_remover,
            mutar_intercambiar_adyacente,
            mutar_mover,
        ]

        def fnMutar(genes):
            mutar(genes, fnObtenerAptitud, operadoresDeMutación, recuentoDeMutaciones)

        def fnIntercambio(padre, donante):
            niño = padre[0:int(len(padre) / 2)] + \
                    donante[int(len(donante) / 2):]
            fnMutar(niño)
            return niño

        def fnCrear():
            return random.sample(geneSet, random.randrange(mínGenes, máxGenes))

        aptitudÓptima = Aptitud(620, 120, 0, 11)
        mejor = genetic.obtener_mejor(fnObtenerAptitud, mínGenes, aptitudÓptima, None,
                                fnMostrar, fnMutar, fnCrear, edadMáxima=500,
                                tamañoDePiscina=20, intercambiar=fnIntercambio)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)

    def test_tornament(self):
        mínGenes = 10
        máxGenes = 20
        geneSet = crear_geneSet()
        horaInicio = datetime.datetime.now()

        def fnMostrar(genes, ganados, empates, perdidos, generación):
            print("-- generación {} --".format(generación))
            mostrar(genetic.Cromosoma(genes,
                                       Aptitud(ganados, empates, perdidos, len(genes)),
                                       None), horaInicio)

        recuentoDeMutaciones = [1]

        operadoresDeMutación = [
            partial(mutar_añadir, geneSet=geneSet),
            partial(mutar_reemplazar, geneSet=geneSet),
            mutar_remover,
            mutar_intercambiar_adyacente,
            mutar_mover,
        ]

        def fnMutar(genes):
            mutar(genes, lambda x: 0, operadoresDeMutación, recuentoDeMutaciones)

        def fnIntercambio(padre, donante):
            niño = padre[0:int(len(padre) / 2)] + \
                    donante[int(len(donante) / 2):]
            fnMutar(niño)
            return niño

        def fnCrear():
            return random.sample(geneSet, random.randrange(mínGenes, máxGenes))

        def fnClaveDeOrden(genes, ganados, empates, perdidos):
            return -1000 * perdidos - empates + 1 / len(genes)

        genetic.torneo(fnCrear, fnIntercambio, jugar1en1, fnMostrar,
                           fnClaveDeOrden, 13)


class TipoDeContenido:
    Vacío = 'VACÍO'
    Mia = 'MIA'
    Oponente = 'OPONENTE'


class Cuadrado:
    def __init__(self, índice, contenido=TipoDeContenido.Vacío):
        self.Contenido = contenido
        self.Índice = índice
        self.Diagonales = []
        # diseño del tablero es
        #   1  2  3
        #   4  5  6
        #   7  8  9
        self.EsCentro = False
        self.EsEsquina = False
        self.EsLado = False
        self.EsFilaSuperior = False
        self.EsFilaDelMedio = False
        self.EsFilaInferior = False
        self.EsColumnaIzquierda = False
        self.EsColumnaEnMedio = False
        self.EsColumnaDerecha = False
        self.Fila = None
        self.Columna = None
        self.OpuestoDeDiagonal = None
        self.OpuestoDeFila = None
        self.OpuestoDeColumna = None

        if índice == 1 or índice == 2 or índice == 3:
            self.EsFilaSuperior = True
            self.Fila = [1, 2, 3]
        elif índice == 4 or índice == 5 or índice == 6:
            self.EsFilaDelMedio = True
            self.Fila = [4, 5, 6]
        elif índice == 7 or índice == 8 or índice == 9:
            self.EsFilaInferior = True
            self.Fila = [7, 8, 9]

        if índice % 3 == 1:
            self.Columna = [1, 4, 7]
            self.EsColumnaIzquierda = True
        elif índice % 3 == 2:
            self.Columna = [2, 5, 8]
            self.EsColumnaEnMedio = True
        elif índice % 3 == 0:
            self.Columna = [3, 6, 9]
            self.EsColumnaDerecha = True

        if índice == 5:
            self.EsCentro = True
        else:
            if índice == 1 or índice == 3 or índice == 7 or índice == 9:
                self.EsEsquina = True
            elif índice == 2 or índice == 4 or índice == 6 or índice == 8:
                self.EsLado = True

            if índice == 1:
                self.OpuestoDeFila = 3
                self.OpuestoDeColumna = 7
                self.OpuestoDeDiagonal = 9
            elif índice == 2:
                self.OpuestoDeColumna = 8
            elif índice == 3:
                self.OpuestoDeFila = 1
                self.OpuestoDeColumna = 9
                self.OpuestoDeDiagonal = 7
            elif índice == 4:
                self.OpuestoDeFila = 6
            elif índice == 6:
                self.OpuestoDeFila = 4
            elif índice == 7:
                self.OpuestoDeFila = 9
                self.OpuestoDeColumna = 1
                self.OpuestoDeDiagonal = 3
            elif índice == 8:
                self.OpuestoDeColumna = 2
            else:  # índice == 9
                self.OpuestoDeFila = 7
                self.OpuestoDeColumna = 3
                self.OpuestoDeDiagonal = 1

        if índice == 1 or self.OpuestoDeDiagonal == 1 or self.EsCentro:
            self.Diagonales.append([1, 5, 9])
        if índice == 3 or self.OpuestoDeDiagonal == 3 or self.EsCentro:
            self.Diagonales.append([7, 5, 3])


class Regla:
    def __init__(self, prefijoDeDescripción, contenidoEsperado=None, cuenta=None):
        self.PrefijoDeDescripción = prefijoDeDescripción
        self.ContenidoEsperado = contenidoEsperado
        self.Cuenta = cuenta

    def __str__(self):
        resultado = self.PrefijoDeDescripción + " "
        if self.Cuenta is not None:
            resultado += str(self.Cuenta) + " "
        if self.ContenidoEsperado is not None:
            resultado += self.ContenidoEsperado + " "
        return resultado


class ReglaMetadatos:
    def __init__(self, crear, opciones=None, necesitaContenidoEspecífico=True,
                 necesitaCuentaEspecífica=True):
        if opciones is None:
            necesitaContenidoEspecífico = False
            necesitaCuentaEspecífica = False
        if necesitaCuentaEspecífica and not necesitaContenidoEspecífico:
            raise ValueError('necesitaCuentaEspecífica solo es válida si necesitaContenidoEspecífico es verdadera')
        self.crear = crear
        self.opciones = opciones
        self.necesitaContenidoEspecífico = necesitaContenidoEspecífico
        self.necesitaCuentaEspecífica = necesitaCuentaEspecífica

    def crear_reglas(self):
        opción = None
        cuenta = None

        visto = set()
        if self.necesitaContenidoEspecífico:
            reglas = list()

            for opciónInfo in self.opciones:
                opción = opciónInfo[0]
                if self.necesitaCuentaEspecífica:
                    cuentaDeOpciones = opciónInfo[1]

                    for cuenta in cuentaDeOpciones:
                        gene = self.crear(opción, cuenta)
                        if str(gene) not in visto:
                            visto.add(str(gene))
                            reglas.append(gene)
                else:
                    gene = self.crear(opción, None)
                    if str(gene) not in visto:
                        visto.add(str(gene))
                        reglas.append(gene)
            return reglas
        else:
            return [self.crear(opción, cuenta)]


class ContenidoFilter(Regla):
    def __init__(self, descripción, contenidoEsperado, cuentaEsperada,
                 obtenerValorDelCuadrado):
        super().__init__(descripción, contenidoEsperado, cuentaEsperada)
        self.obtenerValorDelCuadrado = obtenerValorDelCuadrado

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            m = list(map(lambda i: tablero[i].Contenido,
                         self.obtenerValorDelCuadrado(cuadrado)))
            if m.count(self.ContenidoEsperado) == self.Cuenta:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroDeContenidoDeFila(ContenidoFilter):
    def __init__(self, contenidoEsperado, cuentaEsperada):
        super().__init__("su FILA tiene", contenidoEsperado, cuentaEsperada,
                         lambda s: s.Fila)


class FiltroDeContenidoDeColumna(ContenidoFilter):
    def __init__(self, contenidoEsperado, cuentaEsperada):
        super().__init__("su COLUMNA tiene", contenidoEsperado, cuentaEsperada,
                         lambda s: s.Columna)


class FiltroDeUbicación(Regla):
    def __init__(self, ubicaciónEsperada, descripciónDelContenedor, func):
        super().__init__(
            "es en " + descripciónDelContenedor + (" " if len(descripciónDelContenedor) > 0 else "") + ubicaciónEsperada)
        self.func = func

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if self.func(cuadrado):
                resultado.add(cuadrado.Índice)
        return resultado


class RowFiltroDeUbicación(FiltroDeUbicación):
    def __init__(self, ubicaciónEsperada, func):
        super().__init__(ubicaciónEsperada, "FILA", func)


class ColumnFiltroDeUbicación(FiltroDeUbicación):
    def __init__(self, ubicaciónEsperada, func):
        super().__init__(ubicaciónEsperada, "COLUMNA", func)


class FiltroDeFilaSuperior(RowFiltroDeUbicación):
    def __init__(self):
        super().__init__("SUPERIOR", lambda cuadrado: cuadrado.EsFilaSuperior)


class FiltroDeFilaDelMedio(RowFiltroDeUbicación):
    def __init__(self):
        super().__init__("MEDIO", lambda cuadrado: cuadrado.EsFilaDelMedio)


class FiltroDeFilaInferior(RowFiltroDeUbicación):
    def __init__(self):
        super().__init__("INFERIOR", lambda cuadrado: cuadrado.EsFilaInferior)


class FiltroDeColumnaIzquierda(ColumnFiltroDeUbicación):
    def __init__(self):
        super().__init__("IZQUIERDA", lambda cuadrado: cuadrado.EsColumnaIzquierda)


class FiltroDeColumnaMedia(ColumnFiltroDeUbicación):
    def __init__(self):
        super().__init__("MEDIO", lambda cuadrado: cuadrado.EsColumnaEnMedio)


class FiltroDeColumnaDerecha(ColumnFiltroDeUbicación):
    def __init__(self):
        super().__init__("DERECHO", lambda cuadrado: cuadrado.EsColumnaDerecha)


class FiltroDeUbicaciónDiagonal(FiltroDeUbicación):
    def __init__(self):
        super().__init__("DIAGONAL", "",
                         lambda cuadrado: not (cuadrado.EsFilaDelMedio or
                                             cuadrado.EsColumnaEnMedio) or
                                        cuadrado.EsCentro)


class DiagonalContenidoFilter(Regla):
    def __init__(self, contenidoEsperado, cuenta):
        super().__init__("su DIAGONAL tiene", contenidoEsperado, cuenta)

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            for diagonal in cuadrado.Diagonales:
                m = list(map(lambda i: tablero[i].Contenido, diagonal))
                if m.count(self.ContenidoEsperado) == self.Cuenta:
                    resultado.add(cuadrado.Índice)
                    break
        return resultado


class FiltroDeVictorias(Regla):
    def __init__(self, contenido):
        super().__init__("GANAR" if contenido == TipoDeContenido
                         .Mia else "bloquear OPONENTE de GANAR")
        self.reglaDeFila = FiltroDeContenidoDeFila(contenido, 2)
        self.reglaDeColumna = FiltroDeContenidoDeColumna(contenido, 2)
        self.reglaDeDiagonal = DiagonalContenidoFilter(contenido, 2)

    def obtener_coincidencias(self, tablero, cuadrados):
        enDiagonal = self.reglaDeDiagonal.obtener_coincidencias(tablero, cuadrados)
        if len(enDiagonal) > 0:
            return enDiagonal
        enFila = self.reglaDeFila.obtener_coincidencias(tablero, cuadrados)
        if len(enFila) > 0:
            return enFila
        enColumna = self.reglaDeColumna.obtener_coincidencias(tablero, cuadrados)
        return enColumna


class FiltroDeOpuestosDeDiagonal(Regla):
    def __init__(self, contenidoEsperado):
        super().__init__("OPUESTO en DIAGONAL es", contenidoEsperado)

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.OpuestoDeDiagonal is None:
                continue
            if tablero[cuadrado.OpuestoDeDiagonal].Contenido == self.ContenidoEsperado:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroDeOpuestosDeFila(Regla):
    def __init__(self, contenidoEsperado):
        super().__init__("OPUESTO en FILA es", contenidoEsperado)

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.OpuestoDeFila is None:
                continue
            if tablero[cuadrado.OpuestoDeFila].Contenido == self.ContenidoEsperado:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroDeOpuestosDeColumna(Regla):
    def __init__(self, contenidoEsperado):
        super().__init__("OPUESTO en COLUMNA es", contenidoEsperado)

    def obtener_coincidencias(self, tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.OpuestoDeColumna is None:
                continue
            if tablero[cuadrado.OpuestoDeColumna].Contenido == self.ContenidoEsperado:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroCentral(Regla):
    def __init__(self):
        super().__init__("es en CENTRO")

    @staticmethod
    def obtener_coincidencias(tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.EsCentro:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroDeEsquina(Regla):
    def __init__(self):
        super().__init__("es una ESQUINA")

    @staticmethod
    def obtener_coincidencias(tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.EsEsquina:
                resultado.add(cuadrado.Índice)
        return resultado


class FiltroDeLado(Regla):
    def __init__(self):
        super().__init__("es LADO")

    @staticmethod
    def obtener_coincidencias(tablero, cuadrados):
        resultado = set()
        for cuadrado in cuadrados:
            if cuadrado.EsLado:
                resultado.add(cuadrado.Índice)
        return resultado


tengoTresEnUnaFila = FiltroDeContenidoDeFila(TipoDeContenido.Mia, 3)
tengoTresEnUnaColumna = FiltroDeContenidoDeColumna(TipoDeContenido.Mia, 3)
tengoTresEnDiagonal = DiagonalContenidoFilter(TipoDeContenido.Mia, 3)
oponenteTieneDosEnUnaFila = FiltroDeVictorias(TipoDeContenido.Oponente)


class Aptitud:
    def __init__(self, ganados, empates, perdidos, conteoDeGenes):
        self.Ganados = ganados
        self.Empatados = empates
        self.Perdidos = perdidos
        conteoDeJuegos = ganados + empates + perdidos
        porcentajeGanados = 100 * round(ganados / conteoDeJuegos, 3)
        porcentajePerdidos = 100 * round(perdidos / conteoDeJuegos, 3)
        porcentajeEmpates = 100 * round(empates / conteoDeJuegos, 3)
        self.PorcentajeEmpates = porcentajeEmpates
        self.PorcentajeGanados = porcentajeGanados
        self.PorcentajePerdidos = porcentajePerdidos
        self.ConteoDeGenes = conteoDeGenes

    def __gt__(self, otro):
        if self.PorcentajePerdidos != otro.PorcentajePerdidos:
            return self.PorcentajePerdidos < otro.PorcentajePerdidos

        if self.Perdidos > 0:
            return False

        if self.Empatados != otro.Empatados:
            return self.Empatados < otro.Empatados
        return self.ConteoDeGenes < otro.ConteoDeGenes

    def __str__(self):
        return "{:.1f}% Perdidos ({}), {:.1f}% Empates ({}), {:.1f}% Ganados ({}), {} reglas".format(
            self.PorcentajePerdidos,
            self.Perdidos,
            self.PorcentajeEmpates,
            self.Empatados,
            self.PorcentajeGanados,
            self.Ganados,
            self.ConteoDeGenes)


if __name__ == '__main__':
    unittest.main()
