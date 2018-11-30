# File: pruebas.py
#    Del capítulo 15 de _Algoritmos Genéticos con Python_
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
from cortadora import *


def obtener_aptitud(genes, fnEvaluar):
    campo, cortadora, _ = fnEvaluar(genes)
    return Aptitud(campo.cuente_cortada(), len(genes), cortadora.CuentaDePasos)


def mostrar(candidato, horaInicio, fnEvaluar):
    campo, cortadora, programa = fnEvaluar(candidato.Genes)
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    campo.mostrar(cortadora)
    print("{}\t{}".format(
        candidato.Aptitud,
        diferencia))
    programa.print()


def mutar(genes, geneSet, mínGenes, máxGenes, fnObtenerAptitud, rondasMáximas):
    cuenta = random.randint(1, rondasMáximas)
    aptitudInicial = fnObtenerAptitud(genes)
    while cuenta > 0:
        cuenta -= 1
        if fnObtenerAptitud(genes) > aptitudInicial:
            return
        añadiendo = len(genes) == 0 or \
                    (len(genes) < máxGenes and random.randint(0, 5) == 0)
        if añadiendo:
            genes.append(random.choice(geneSet)())
            continue

        eliminando = len(genes) > mínGenes and random.randint(0, 50) == 0
        if eliminando:
            índice = random.randrange(0, len(genes))
            del genes[índice]
            continue

        índice = random.randrange(0, len(genes))
        genes[índice] = random.choice(geneSet)()


def crear(geneSet, mínGenes, máxGenes):
    cantidad = random.randint(mínGenes, máxGenes)
    genes = [random.choice(geneSet)() for _ in range(1, cantidad)]
    return genes


def intercambiar(padre, otroPadre):
    genesDelNiño = padre[:]
    if len(padre) <= 2 or len(otroPadre) < 2:
        return genesDelNiño
    longitud = random.randint(1, len(padre) - 2)
    principio = random.randrange(0, len(padre) - longitud)
    genesDelNiño[principio:principio + longitud] = \
        otroPadre[principio:principio + longitud]
    return genesDelNiño


class PruebasDeCortadora(unittest.TestCase):
    def test_corta_gira(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira()]
        mínGenes = anchura * altura
        máxGenes = int(1.5 * mínGenes)
        rondasMáximasDeMutación = 3
        númeroEsperadoDeInstrucciones = 78

        def fnCrearCampo():
            return CampoToroidal(anchura, altura,
                                 ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDeInstrucciones)

    def test_corta_gira_salta(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira(),
                   lambda: Salta(random.randint(0, min(anchura, altura)),
                                 random.randint(0, min(anchura, altura)))]
        mínGenes = anchura * altura
        máxGenes = int(1.5 * mínGenes)
        rondasMáximasDeMutación = 1
        númeroEsperadoDeInstrucciones = 64

        def fnCrearCampo():
            return CampoToroidal(anchura, altura,
                                 ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDeInstrucciones)

    def test_corta_gira_salta_validando(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira(),
                   lambda: Salta(random.randint(0, min(anchura, altura)),
                                 random.randint(0, min(anchura, altura)))]
        mínGenes = anchura * altura
        máxGenes = int(1.5 * mínGenes)
        rondasMáximasDeMutación = 3
        númeroEsperadoDeInstrucciones = 79

        def fnCrearCampo():
            return CampoValidando(anchura, altura,
                                  ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDeInstrucciones)

    def test_corta_gira_repite(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira(),
                   lambda: Repite(random.randint(0, 8),
                                  random.randint(0, 8))]
        mínGenes = 3
        máxGenes = 20
        rondasMáximasDeMutación = 3
        númeroEsperadoDeInstrucciones = 9
        númeroEsperadoDePasos = 88

        def fnCrearCampo():
            return CampoToroidal(anchura, altura,
                                 ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDePasos)

    def test_corta_gira_salta_func(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira(),
                   lambda: Salta(random.randint(0, min(anchura, altura)),
                                 random.randint(0, min(anchura, altura))),
                   lambda: Func()]
        mínGenes = 3
        máxGenes = 20
        rondasMáximasDeMutación = 3
        númeroEsperadoDeInstrucciones = 17
        númeroEsperadoDePasos = 64

        def fnCrearCampo():
            return CampoToroidal(anchura, altura,
                                 ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDePasos)

    def test_corta_gira_salta_llama(self):
        anchura = altura = 8
        geneSet = [lambda: Corta(),
                   lambda: Gira(),
                   lambda: Salta(random.randint(0, min(anchura, altura)),
                                 random.randint(0, min(anchura, altura))),
                   lambda: Func(expectLlama=True),
                   lambda: Llama(random.randint(0, 5))]
        mínGenes = 3
        máxGenes = 20
        rondasMáximasDeMutación = 3
        númeroEsperadoDeInstrucciones = 18
        númeroEsperadoDePasos = 65

        def fnCrearCampo():
            return CampoToroidal(anchura, altura,
                                 ContenidoDelCampo.Hierba)

        self.ejecutar_con(geneSet, anchura, altura, mínGenes, máxGenes,
                          númeroEsperadoDeInstrucciones,
                          rondasMáximasDeMutación, fnCrearCampo,
                          númeroEsperadoDePasos)

    def ejecutar_con(self, geneSet, anchura, altura, mínGenes, máxGenes,
                     númeroEsperadoDeInstrucciones, rondasMáximasDeMutación,
                     fnCrearCampo, númeroEsperadoDePasos):
        ubicaciónInicialDelCortador = Ubicación(int(anchura / 2),
                                                int(altura / 2))
        direcciónInicialDelCortador = Direcciones.Sur.value

        def fnCrear():
            return crear(geneSet, 1, altura)

        def fnEvaluar(instrucciones):
            programa = Programa(instrucciones)
            cortadora = Cortadora(ubicaciónInicialDelCortador,
                                  direcciónInicialDelCortador)
            campo = fnCrearCampo()
            try:
                programa.evaluar(cortadora, campo)
            except RecursionError:
                pass
            return campo, cortadora, programa

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, fnEvaluar)

        horaInicio = datetime.datetime.now()

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio, fnEvaluar)

        def fnMutar(niño):
            mutar(niño, geneSet, mínGenes, máxGenes, fnObtenerAptitud,
                  rondasMáximasDeMutación)

        aptitudÓptima = Aptitud(anchura * altura,
                                númeroEsperadoDeInstrucciones,
                                númeroEsperadoDePasos)

        mejor = genetic.obtener_mejor(fnObtenerAptitud, None, aptitudÓptima,
                                      None, fnMostrar, fnMutar, fnCrear,
                                      edadMáxima=None, tamañoDePiscina=10,
                                      intercambiar=intercambiar)

        self.assertTrue(not aptitudÓptima > mejor.Aptitud)


class Corta:
    def __init__(self):
        pass

    @staticmethod
    def ejecutar(cortadora, campo):
        cortadora.corta(campo)

    def __str__(self):
        return "corta"


class Gira:
    def __init__(self):
        pass

    @staticmethod
    def ejecutar(cortadora, campo):
        cortadora.girar_a_la_izquierda()

    def __str__(self):
        return "gira"


class Salta:
    def __init__(self, adelante, derecha):
        self.Adelante = adelante
        self.Derecha = derecha

    def ejecutar(self, cortadora, campo):
        cortadora.salta(campo, self.Adelante, self.Derecha)

    def __str__(self):
        return "salta({},{})".format(self.Adelante, self.Derecha)


class Repite:
    def __init__(self, númeroDeOperaciones, veces):
        self.NúmeroDeOperaciones = númeroDeOperaciones
        self.Veces = veces
        self.Instrucciones = []

    def ejecutar(self, cortadora, campo):
        for i in range(self.Veces):
            for instrucción in self.Instrucciones:
                instrucción.ejecutar(cortadora, campo)

    def __str__(self):
        return "repite({},{})".format(
            ' '.join(map(str, self.Instrucciones))
            if len(self.Instrucciones) > 0
            else self.NúmeroDeOperaciones,
            self.Veces)


class Func:
    def __init__(self, expectLlama=False):
        self.Instrucciones = []
        self.ExpectLlama = expectLlama
        self.Id = None

    def ejecutar(self, cortadora, campo):
        for instrucción in self.Instrucciones:
            instrucción.ejecutar(cortadora, campo)

    def __str__(self):
        return "func{1}: {0}".format(
            ' '.join(map(str, self.Instrucciones)),
            self.Id if self.Id is not None else '')


class Llama:
    def __init__(self, funcId=None):
        self.FuncId = funcId
        self.Funcs = None

    def ejecutar(self, cortadora, campo):
        funcId = 0 if self.FuncId is None else self.FuncId
        if len(self.Funcs) > funcId:
            self.Funcs[funcId].ejecutar(cortadora, campo)

    def __str__(self):
        return "llama-{}".format(
            self.FuncId
            if self.FuncId is not None
            else 'func')


class Programa:
    def __init__(self, genes):
        temp = genes[:]
        funcs = []

        for índice in reversed(range(len(temp))):
            if type(temp[índice]) is Repite:
                principio = índice + 1
                fin = min(índice + temp[índice].NúmeroDeOperaciones + 1,
                          len(temp))
                temp[índice].Instrucciones = temp[principio:fin]
                del temp[principio:fin]
                continue

            if type(temp[índice]) is Llama:
                temp[índice].Funcs = funcs
            if type(temp[índice]) is Func:
                if len(funcs) > 0 and not temp[índice].ExpectLlama:
                    temp[índice] = Llama()
                    temp[índice].Funcs = funcs
                    continue
                principio = índice + 1
                fin = len(temp)
                func = Func()
                if temp[índice].ExpectLlama:
                    func.Id = len(funcs)
                func.Instrucciones = [i for i in temp[principio:fin]
                                      if type(i) is not Repite or
                                      type(i) is Repite and len(
                                          i.Instrucciones) > 0]
                funcs.append(func)
                del temp[índice:fin]

        for func in funcs:
            for índice in reversed(range(len(func.Instrucciones))):
                if type(func.Instrucciones[índice]) is Llama:
                    func_id = func.Instrucciones[índice].FuncId
                    if func_id is None:
                        continue
                    if func_id >= len(funcs) or \
                                    len(funcs[func_id].Instrucciones) == 0:
                        del func.Instrucciones[índice]

        for índice in reversed(range(len(temp))):
            if type(temp[índice]) is Llama:
                func_id = temp[índice].FuncId
                if func_id is None:
                    continue
                if func_id >= len(funcs) or \
                                len(funcs[func_id].Instrucciones) == 0:
                    del temp[índice]
        self.Principal = temp
        self.Funcs = funcs

    def evaluar(self, cortadora, campo):
        for i, instrucción in enumerate(self.Principal):
            instrucción.ejecutar(cortadora, campo)

    def print(self):
        if self.Funcs is not None:
            for func in self.Funcs:
                if func.Id is not None and len(func.Instrucciones) == 0:
                    continue
                print(func)
        print(' '.join(map(str, self.Principal)))


class Aptitud:
    def __init__(self, totalCortada, instruccionesTotales, cuentaDePasos):
        self.TotalCortada = totalCortada
        self.InstruccionesTotales = instruccionesTotales
        self.CuentaDePasos = cuentaDePasos

    def __gt__(self, otro):
        if self.TotalCortada != otro.TotalCortada:
            return self.TotalCortada > otro.TotalCortada
        if self.CuentaDePasos != otro.CuentaDePasos:
            return self.CuentaDePasos < otro.CuentaDePasos
        return self.InstruccionesTotales < otro.InstruccionesTotales

    def __str__(self):
        return "{} segados con {} instrucciones y {} pasos".format(
            self.TotalCortada, self.InstruccionesTotales, self.CuentaDePasos)


if __name__ == '__main__':
    unittest.main()
