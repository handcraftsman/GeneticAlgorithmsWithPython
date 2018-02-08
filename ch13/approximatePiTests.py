# File: approximatePiTests.py
#    from chapter 13 of _Genetic Algorithms with Python_
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
import math
import random
import sys
import time
import unittest

import genetic


def get_fitness(genes, bitValues):
    denominator = get_denominator(genes, bitValues)
    if denominator == 0:
        return 0

    ratio = get_numerator(genes, bitValues) / denominator
    return math.pi - math.fabs(math.pi - ratio)


def display(candidate, startTime, bitValues):
    timeDiff = datetime.datetime.now() - startTime
    numerator = get_numerator(candidate.Genes, bitValues)
    denominator = get_denominator(candidate.Genes, bitValues)
    print("{}/{}\t{}\t{}".format(
        numerator,
        denominator,
        candidate.Fitness, timeDiff))


def bits_to_int(bits, bitValues):
    result = 0
    for i, bit in enumerate(bits):
        if bit == 0:
            continue
        result += bitValues[i]
    return result


def get_numerator(genes, bitValues):
    return 1 + bits_to_int(genes[:len(bitValues)], bitValues)


def get_denominator(genes, bitValues):
    return bits_to_int(genes[len(bitValues):], bitValues)


def mutate(genes, numBits):
    numeratorIndex, denominatorIndex \
        = random.randrange(0, numBits), random.randrange(numBits,
                                                         len(genes))
    genes[numeratorIndex] = 1 - genes[numeratorIndex]
    genes[denominatorIndex] = 1 - genes[denominatorIndex]


class ApproximatePiTests(unittest.TestCase):
    def test(self, bitValues=[512, 256, 128, 64, 32, 16, 8, 4, 2, 1],
             maxSeconds=None):
        geneset = [i for i in range(2)]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime, bitValues)

        def fnGetFitness(genes):
            return get_fitness(genes, bitValues)

        optimalFitness = 3.14159

        def fnMutate(genes):
            mutate(genes, len(bitValues))

        length = 2 * len(bitValues)
        best = genetic.get_best(fnGetFitness, length, optimalFitness,
                                geneset, fnDisplay, fnMutate, maxAge=250,
                                maxSeconds=maxSeconds)
        return optimalFitness <= best.Fitness

    def test_optimize(self):
        geneset = [i for i in range(1, 512 + 1)]
        length = 10
        maxSeconds = 2

        def fnGetFitness(genes):
            startTime = time.time()
            count = 0
            stdout = sys.stdout
            sys.stdout = None
            while time.time() - startTime < maxSeconds:
                if self.test(genes, maxSeconds):
                    count += 1
            sys.stdout = stdout
            distance = abs(sum(genes) - 1023)
            fraction = 1 / distance if distance > 0 else distance
            count += round(fraction, 4)
            return count

        def fnDisplay(chromosome):
            print("{}\t{}".format(chromosome.Genes, chromosome.Fitness))

        initial = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
        print("initial:", initial, fnGetFitness(initial))

        optimalFitness = 10 * maxSeconds
        genetic.get_best(fnGetFitness, length, optimalFitness, geneset,
                         fnDisplay, maxSeconds=600)

    def test_benchmark(self):
        genetic.Benchmark.run(
            lambda: self.test([98, 334, 38, 339, 117,
                               39, 145, 123, 40, 129]))

    def test_find_top_10_approximations(self):
        best = {}
        for numerator in range(1, 1024):
            for denominator in range(1, 1024):
                ratio = numerator / denominator
                piDist = math.pi - abs(math.pi - ratio)
                if piDist not in best or best[piDist][0] > numerator:
                    best[piDist] = [numerator, denominator]

        bestApproximations = list(reversed(sorted(best.keys())))
        for i in range(10):
            ratio = bestApproximations[i]
            nd = best[ratio]
            print("%i / %i\t%f" % (nd[0], nd[1], ratio))


if __name__ == '__main__':
    unittest.main()
