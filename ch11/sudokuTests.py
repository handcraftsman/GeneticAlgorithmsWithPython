# File: sudokuTests.py
#    from chapter 11 of _Genetic Algorithms with Python_
#
# Author: Clinton Sheppard <fluentcoder@gmail.com>
# Copyright (c) 2016 Clinton Sheppard
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


def get_fitness(genes, validationRules):
    try:
        firstFailingRule = next(rule for rule in validationRules
                                if genes[rule.Index] == genes[rule.OtherIndex])
    except StopIteration:
        fitness = 100
    else:
        fitness = (1 + index_row(firstFailingRule.OtherIndex)) * 10 \
                  + (1 + index_column(firstFailingRule.OtherIndex))
    return fitness


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime

    for row in range(9):
        line = ' | '.join(
            ' '.join(str(i)
                     for i in candidate.Genes[row * 9 + i:row * 9 + i + 3])
            for i in [0, 3, 6])
        print("", line)
        if row < 8 and row % 3 == 2:
            print(" ----- + ----- + -----")
    print(" - = -   - = -   - = - {}\t{}\n"
          .format(candidate.Fitness, timeDiff))


def mutate(genes, validationRules):
    selectedRule = next(rule for rule in validationRules
                        if genes[rule.Index] == genes[rule.OtherIndex])
    if selectedRule is None:
        return

    if index_row(selectedRule.OtherIndex) % 3 == 2 \
            and random.randint(0, 10) == 0:
        sectionStart = section_start(selectedRule.Index)
        current = selectedRule.OtherIndex
        while selectedRule.OtherIndex == current:
            shuffle_in_place(genes, sectionStart, 80)
            selectedRule = next(rule for rule in validationRules
                                if genes[rule.Index] == genes[rule.OtherIndex])
        return
    row = index_row(selectedRule.OtherIndex)
    start = row * 9
    indexA = selectedRule.OtherIndex
    indexB = random.randrange(start, len(genes))
    genes[indexA], genes[indexB] = genes[indexB], genes[indexA]


def shuffle_in_place(genes, first, last):
    while first < last:
        index = random.randint(first, last)
        genes[first], genes[index] = genes[index], genes[first]
        first += 1


class SudokuTests(unittest.TestCase):
    def test(self):
        geneset = [i for i in range(1, 9 + 1)]
        startTime = datetime.datetime.now()
        optimalValue = 100

        def fnDisplay(candidate):
            display(candidate, startTime)

        validationRules = build_validation_rules()

        def fnGetFitness(genes):
            return get_fitness(genes, validationRules)

        def fnCreate():
            return random.sample(geneset * 9, 81)

        def fnMutate(genes):
            mutate(genes, validationRules)

        best = genetic.get_best(fnGetFitness, None, optimalValue, None,
                                fnDisplay, fnMutate, fnCreate, maxAge=50)
        self.assertEqual(best.Fitness, optimalValue)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())


def build_validation_rules():
    rules = []
    for index in range(80):
        itsRow = index_row(index)
        itsColumn = index_column(index)
        itsSection = row_column_section(itsRow, itsColumn)

        for index2 in range(index + 1, 81):
            otherRow = index_row(index2)
            otherColumn = index_column(index2)
            otherSection = row_column_section(otherRow, otherColumn)
            if itsRow == otherRow or \
                            itsColumn == otherColumn or \
                            itsSection == otherSection:
                rules.append(Rule(index, index2))

    rules.sort(key=lambda x: x.OtherIndex * 100 + x.Index)
    return rules


def index_row(index):
    return int(index / 9)


def index_column(index):
    return int(index % 9)


def row_column_section(row, column):
    return int(row / 3) * 3 + int(column / 3)


def index_section(index):
    return row_column_section(index_row(index), index_column(index))


def section_start(index):
    return int((index_row(index) % 9) / 3) * 27 + int(
        index_column(index) / 3) * 3


class Rule:
    def __init__(self, it, other):
        if it > other:
            it, other = other, it
        self.Index = it
        self.OtherIndex = other

    def __eq__(self, other):
        return self.Index == other.Index and \
               self.OtherIndex == other.OtherIndex

    def __hash__(self):
        return self.Index * 100 + self.OtherIndex


if __name__ == '__main__':
    unittest.main()
