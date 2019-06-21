# File: regex.py
#    Del capítulo 17 de _Algoritmos Genéticos con Python_
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
import re
import unittest
from functools import partial

import genetic

metasDeRepetición = {'?', '*', '+', '{2}', '{2,}'}
metasDeInicio = {'|', '(', '['}
metasFinales = {')', ']'}
todosMetacaracteres = metasDeRepetición | metasDeInicio | metasFinales

erroresEnRegexes = {}


def reparar_regex(genes):
    resultado = []
    finales = []
    f = reparar_o_ignorar_metas_de_repetición
    for símbolo in genes:
        f = f(símbolo, resultado, finales)
    if ']' in finales and resultado[-1] == '[':
        del resultado[-1]
    resultado.extend(reversed(finales))
    return ''.join(resultado)


def reparar_o_ignorar_metas_de_repetición(símbolo, resultado, finales):
    if símbolo in metasDeRepetición or símbolo in metasFinales:
        return reparar_o_ignorar_metas_de_repetición
    if símbolo == '(':
        finales.append(')')
    resultado.append(símbolo)
    if símbolo == '[':
        finales.append(']')
        return reparar_in_character_set
    return manejar_metas_de_repetición_que_siguen_metas_de_repetición_o_inicio


def manejar_metas_de_repetición_que_siguen_metas_de_repetición_o_inicio(
        símbolo, resultado, finales):
    último = resultado[-1]
    if símbolo not in metasDeRepetición:
        if símbolo == '[':
            resultado.append(símbolo)
            finales.append(']')
            return reparar_in_character_set
        if símbolo == '(':
            finales.append(')')
        elif símbolo == ')':
            coincidencia = ''.join(finales).rfind(')')
            if coincidencia != -1:
                del finales[coincidencia]
            else:
                resultado[0:0] = ['(']
        resultado.append(símbolo)
    elif último in metasDeInicio:
        pass
    elif símbolo == '?' and último == '?' and len(resultado) > 2 \
            and resultado[-2] in metasDeRepetición:
        pass
    elif último in metasDeRepetición:
        pass
    else:
        resultado.append(símbolo)
    return manejar_metas_de_repetición_que_siguen_metas_de_repetición_o_inicio


def reparar_in_character_set(símbolo, resultado, finales):
    if símbolo == ']':
        if resultado[-1] == '[':
            del resultado[-1]
        resultado.append(símbolo)
        coincidencia = ''.join(finales).rfind(']')
        if coincidencia != -1:
            del finales[coincidencia]
        return manejar_metas_de_repetición_que_siguen_metas_de_repetición_o_inicio
    elif símbolo == '[':
        pass
    elif símbolo == '|' and resultado[-1] == '|':
        pass  # suprimir FutureWarning sobre ||
    else:
        resultado.append(símbolo)
    return reparar_in_character_set


def obtener_aptitud(genes, deseadas, noDeseadas):
    patrón = reparar_regex(genes)
    longitud = len(patrón)

    try:
        re.compile(patrón)
    except re.error as e:
        llave = str(e)
        llave = llave[:llave.index("at position")]
        info = [str(e),
                "genes = ['{}']".format("', '".join(genes)),
                "regex: " + patrón]
        if llave not in erroresEnRegexes or len(info[1]) < len(
                erroresEnRegexes[llave][1]):
            erroresEnRegexes[llave] = info
        return Aptitud(0, len(deseadas), len(noDeseadas), longitud)

    númeroDeDeseadosQueCoincidieron = sum(
        1 for i in deseadas if re.fullmatch(patrón, i))
    númeroDeNoDeseadosQueCoincidieron = sum(
        1 for i in noDeseadas if re.fullmatch(patrón, i))
    return Aptitud(númeroDeDeseadosQueCoincidieron, len(deseadas),
                   númeroDeNoDeseadosQueCoincidieron, longitud)


def mostrar(candidato, horaInicio):
    diferencia = (datetime.datetime.now() - horaInicio).total_seconds()
    print("{}\t{}\t{}".format(
        reparar_regex(candidato.Genes), candidato.Aptitud, diferencia))


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


def mutar_intercambiar(genes):
    if len(genes) < 2:
        return False
    índiceA, índiceB = random.sample(range(len(genes)), 2)
    genes[índiceA], genes[índiceB] = genes[índiceB], genes[índiceA]
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


def mutar_a_conjunto_de_caracteres(genes):
    if len(genes) < 3:
        return False
    o = [i for i in range(1, len(genes) - 1)
         if genes[i] == '|' and
         genes[i - 1] not in todosMetacaracteres and
         genes[i + 1] not in todosMetacaracteres]
    if len(o) == 0:
        return False
    corta = [i for i in o
             if sum(len(w) for w in genes[i - 1:i + 2:2]) >
             len(set(c for w in genes[i - 1:i + 2:2] for c in w))]
    if len(corta) == 0:
        return False
    índice = random.choice(o)
    distinto = set(c for w in genes[índice - 1:índice + 2:2] for c in w)
    secuencia = ['['] + [i for i in distinto] + [']']
    genes[índice - 1:índice + 2] = secuencia
    return True


def mutar_a_conjunto_de_caracteres_izquierda(genes, deseadas):
    if len(genes) < 4:
        return False
    o = [i for i in range(-1, len(genes) - 3)
         if (i == -1 or genes[i] in metasDeInicio) and
         len(genes[i + 1]) == 2 and
         genes[i + 1] in deseadas and
         (len(genes) == i + 1 or genes[i + 2] == '|' or
          genes[i + 2] in metasFinales)]
    if len(o) == 0:
        return False
    búsqueda = {}
    for i in o:
        búsqueda.setdefault(genes[i + 1][0], []).append(i)
    mín2 = [i for i in búsqueda.values() if len(i) > 1]
    if len(mín2) == 0:
        return False
    choice = random.choice(mín2)
    caracteres = ['|', genes[choice[0] + 1][0], '[']
    caracteres.extend([genes[i + 1][1] for i in choice])
    caracteres.append(']')
    for i in reversed(choice):
        if i >= 0:
            genes[i:i + 2] = []
    genes.extend(caracteres)
    return True


def mutar_add_deseadas(genes, deseadas):
    índice = random.randrange(0, len(genes) + 1) if len(genes) > 0 else 0
    genes[índice:índice] = ['|'] + [random.choice(deseadas)]
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


class PruebasDeRegex(unittest.TestCase):
    def test_dos_dígitos(self):
        deseadas = {"01", "11", "10"}
        noDeseadas = {"00", ""}
        self.encontrar_regex(deseadas, noDeseadas, 7)

    def test_grupos(self):
        deseadas = {"01", "0101", "010101"}
        noDeseadas = {"0011", ""}
        self.encontrar_regex(deseadas, noDeseadas, 5)

    def test_códigos_de_estado(self):
        Aptitud.UseRegexLongitud = True
        deseadas = {"NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND"}
        noDeseadas = {"N" + l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      if "N" + l not in deseadas}
        operadoresPersonalizados = [
            partial(mutar_a_conjunto_de_caracteres_izquierda,
                    deseadas=deseadas),
        ]
        self.encontrar_regex(deseadas, noDeseadas, 11,
                             operadoresPersonalizados)

    def test_longitud_par(self):
        deseadas = {"00", "01", "10", "11", "0000", "0001", "0010", "0011",
                    "0100", "0101", "0110", "0111", "1000", "1001", "1010",
                    "1011", "1100", "1101", "1110", "1111"}
        noDeseadas = {"0", "1", "000", "001", "010", "011", "100", "101",
                      "110", "111", ""}
        operadoresPersonalizados = [
            mutar_a_conjunto_de_caracteres,
        ]
        self.encontrar_regex(deseadas, noDeseadas, 10,
                             operadoresPersonalizados)

    def test_50_códigos_de_estado(self):
        Aptitud.UseRegexLongitud = True
        deseadas = {"AL", "AK", "AZ", "AR", "CA",
                    "CO", "CT", "DE", "FL", "GA",
                    "HI", "ID", "IL", "IN", "IA",
                    "KS", "KY", "LA", "ME", "MD",
                    "MA", "MI", "MN", "MS", "MO",
                    "MT", "NE", "NV", "NH", "NJ",
                    "NM", "NY", "NC", "ND", "OH",
                    "OK", "OR", "PA", "RI", "SC",
                    "SD", "TN", "TX", "UT", "VT",
                    "VA", "WA", "WV", "WI", "WY"}
        noDeseadas = {a + b for a in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      for b in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      if a + b not in deseadas} | \
                     set(i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        operadoresPersonalizados = [
            partial(mutar_a_conjunto_de_caracteres_izquierda,
                    deseadas=deseadas),
            mutar_a_conjunto_de_caracteres,
            partial(mutar_add_deseadas, deseadas=[i for i in deseadas]),
        ]
        self.encontrar_regex(deseadas, noDeseadas, 120,
                             operadoresPersonalizados)

    def encontrar_regex(self, deseadas, noDeseadas, longitudEsperada,
                        operadoresPersonalizados=None):
        horaInicio = datetime.datetime.now()
        genesDeTexto = deseadas | set(c for w in deseadas for c in w)
        geneSet = [i for i in todosMetacaracteres | genesDeTexto]

        def fnMostrar(candidato):
            mostrar(candidato, horaInicio)

        def fnObtenerAptitud(genes):
            return obtener_aptitud(genes, deseadas, noDeseadas)

        recuentoDeMutaciones = [1]

        operadoresDeMutación = [
            partial(mutar_añadir, geneSet=geneSet),
            partial(mutar_reemplazar, geneSet=geneSet),
            mutar_remover,
            mutar_intercambiar,
            mutar_mover,
        ]
        if operadoresPersonalizados is not None:
            operadoresDeMutación.extend(operadoresPersonalizados)

        def fnMutar(genes):
            mutar(genes, fnObtenerAptitud, operadoresDeMutación,
                  recuentoDeMutaciones)

        aptitudÓptima = Aptitud(len(deseadas), len(deseadas), 0,
                                longitudEsperada)

        mejor = genetic.obtener_mejor(
            fnObtenerAptitud, max(len(i) for i in genesDeTexto),
            aptitudÓptima, geneSet, fnMostrar, fnMutar, tamañoDePiscina=10)
        self.assertTrue(not aptitudÓptima > mejor.Aptitud)

        for info in erroresEnRegexes.values():
            print("")
            print(info[0])
            print(info[1])
            print(info[2])

    def test_comparativa(self):
        genetic.Comparar.ejecutar(self.test_dos_dígitos)


class Aptitud:
    UseRegexLongitud = False

    def __init__(self, númeroDeDeseadosQueCoincidieron, totalDeseado,
                 númeroDeNoDeseadosQueCoincidieron, longitud):
        self.NúmeroDeDeseadosQueCoincidieron = númeroDeDeseadosQueCoincidieron
        self._totalDeseado = totalDeseado
        self.NúmeroDeNoDeseadosQueCoincidieron = \
            númeroDeNoDeseadosQueCoincidieron
        self.Longitud = longitud

    def __gt__(self, otro):
        conjunto = (self._totalDeseado -
                    self.NúmeroDeDeseadosQueCoincidieron) + \
                   self.NúmeroDeNoDeseadosQueCoincidieron
        otroConjunto = (otro._totalDeseado -
                        otro.NúmeroDeDeseadosQueCoincidieron) + \
                       otro.NúmeroDeNoDeseadosQueCoincidieron
        if conjunto != otroConjunto:
            return conjunto < otroConjunto
        éxito = conjunto == 0
        otroÉxito = otroConjunto == 0
        if éxito != otroÉxito:
            return éxito
        if not éxito:
            return self.Longitud <= otro.Longitud if \
                Aptitud.UseRegexLongitud else False
        return self.Longitud < otro.Longitud

    def __str__(self):
        return "coincide con: {} deseadas, y {} no deseadas, lon {}".format(
            "todas" if self._totalDeseado ==
                       self.NúmeroDeDeseadosQueCoincidieron else
            self.NúmeroDeDeseadosQueCoincidieron,
            self.NúmeroDeNoDeseadosQueCoincidieron,
            self.Longitud)


if __name__ == '__main__':
    unittest.main()
