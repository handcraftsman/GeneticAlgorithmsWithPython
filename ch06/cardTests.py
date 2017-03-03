# File: cardTests.py
#    from chapter 6 of _Genetic Algorithms with Python_
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
import functools
import operator
import random
import unittest

import genetic


def get_fitness(genes):
    group1Sum = sum(genes[0:5])
    group2Product = functools.reduce(operator.mul, genes[5:10])
    duplicateCount = (len(genes) - len(set(genes)))
    return Fitness(group1Sum, group2Product, duplicateCount)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{} - {}\t{}\t{}".format(
        ', '.join(map(str, candidate.Genes[0:5])),
        ', '.join(map(str, candidate.Genes[5:10])),
        candidate.Fitness,
        timeDiff))


def mutate(genes, geneset):
    if len(genes) == len(set(genes)):
        count = random.randint(1, 4)
        while count > 0:
            count -= 1
            indexA, indexB = random.sample(range(len(genes)), 2)
            genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
    else:
        indexA = random.randrange(0, len(genes))
        indexB = random.randrange(0, len(geneset))
        genes[indexA] = geneset[indexB]


class CardTests(unittest.TestCase):
    def test(self):
        geneset = [i + 1 for i in range(10)]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        def fnMutate(genes):
            mutate(genes, geneset)

        optimalFitness = Fitness(36, 360, 0)
        best = genetic.get_best(fnGetFitness, 10, optimalFitness, geneset,
                                fnDisplay, custom_mutate=fnMutate)
        self.assertTrue(not optimalFitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())


class Fitness:
    def __init__(self, group1Sum, group2Product, duplicateCount):
        self.Group1Sum = group1Sum
        self.Group2Product = group2Product
        sumDifference = abs(36 - group1Sum)
        productDifference = abs(360 - group2Product)
        self.TotalDifference = sumDifference + productDifference
        self.DuplicateCount = duplicateCount

    def __gt__(self, other):
        if self.DuplicateCount != other.DuplicateCount:
            return self.DuplicateCount < other.DuplicateCount
        return self.TotalDifference < other.TotalDifference

    def __str__(self):
        return "sum: {} prod: {} dups: {}".format(
            self.Group1Sum,
            self.Group2Product,
            self.DuplicateCount)


if __name__ == '__main__':
    unittest.main()
