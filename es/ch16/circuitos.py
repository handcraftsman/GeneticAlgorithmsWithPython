# File: circuitos.py
#    Del capítulo 16 de _Algoritmos Genéticos con Python_
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

class Not:
    def __init__(self, entrada):
        self._entrada = entrada

    def obtener_salida(self):
        if self._entrada is None:
            return None
        valor = self._entrada.obtener_salida()
        if valor is None:
            return None
        return not valor

    def __str__(self):
        if self._entrada is None:
            return "Not(?)"
        return "Not({})".format(self._entrada)

    @staticmethod
    def recuento_de_entradas():
        return 1


class PuertaCon2Entradas:
    def __init__(self, entradaA, entradaB, etiqueta, fnPrueba):
        self._entradaA = entradaA
        self._entradaB = entradaB
        self._etiqueta = etiqueta
        self._fnPrueba = fnPrueba

    def obtener_salida(self):
        if self._entradaA is None or self._entradaB is None:
            return None
        aValor = self._entradaA.obtener_salida()
        if aValor is None:
            return None
        bValor = self._entradaB.obtener_salida()
        if bValor is None:
            return None
        return self._fnPrueba(aValor, bValor)

    def __str__(self):
        if self._entradaA is None or self._entradaB is None:
            return "{}(?)".format(self._etiqueta)
        return "{}({} {})".format(self._etiqueta, self._entradaA,
                                  self._entradaB)

    @staticmethod
    def recuento_de_entradas():
        return 2


class And(PuertaCon2Entradas):
    def __init__(self, entradaA, entradaB):
        super().__init__(entradaA, entradaB, type(self).__name__,
                         lambda a, b: a and b)


class Or(PuertaCon2Entradas):
    def __init__(self, entradaA, entradaB):
        super().__init__(entradaA, entradaB, type(self).__name__,
                         lambda a, b: a or b)


class Xor(PuertaCon2Entradas):
    def __init__(self, entradaA, entradaB):
        super().__init__(entradaA, entradaB, type(self).__name__,
                         lambda a, b: a != b)


class Fuente:
    def __init__(self, fuenteId, contenedorDeFuentes):
        self._fuenteId = fuenteId
        self._contenedorDeFuentes = contenedorDeFuentes

    def obtener_salida(self):
        return self._contenedorDeFuentes[self._fuenteId]

    def __str__(self):
        return self._fuenteId

    @staticmethod
    def recuento_de_entradas():
        return 0
