# File: sortedNumbersTests.py
#    from chapter 3 of _Genetic Algorithms with Python_
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
import unittest

import genetic


def get_fitness(genes):
    fitness = 1
    gap = 0

    for i in range(1, len(genes)):
        if genes[i] > genes[i - 1]:
            fitness += 1
        else:
            gap += genes[i - 1] - genes[i]
    return Fitness(fitness, gap)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t=> {}\t{}".format(
        ', '.join(map(str, candidate.Genes)),
        candidate.Fitness,
        timeDiff))


class SortedNumbersTests(unittest.TestCase):
    def test_sort_10_numbers(self):
        self.sort_numbers(10)

    def sort_numbers(self, totalNumbers):
        geneset = [i for i in range(100)]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        optimalFitness = Fitness(totalNumbers, 0)
        best = genetic.get_best(fnGetFitness, totalNumbers, optimalFitness,
                                geneset, fnDisplay)
        self.assertTrue(not optimalFitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.sort_numbers(40))


class Fitness:
    def __init__(self, numbersInSequenceCount, totalGap):
        self.NumbersInSequenceCount = numbersInSequenceCount
        self.TotalGap = totalGap

    def __gt__(self, other):
        if self.NumbersInSequenceCount != other.NumbersInSequenceCount:
            return self.NumbersInSequenceCount > other.NumbersInSequenceCount
        return self.TotalGap < other.TotalGap

    def __str__(self):
        return "{} Sequential, {} Total Gap".format(
            self.NumbersInSequenceCount,
            self.TotalGap)


if __name__ == '__main__':
    unittest.main()
