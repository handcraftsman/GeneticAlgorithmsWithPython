# File: oneMaxTests.py
#    from chapter 2 of _Genetic Algorithms with Python_
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
    return genes.count(1)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}...{}\t{:3.2f}\t{}".format(
        ''.join(map(str, candidate.Genes[:15])),
        ''.join(map(str, candidate.Genes[-15:])),
        candidate.Fitness,
        timeDiff))


class OneMaxTests(unittest.TestCase):
    def test(self, length=100):
        geneset = [0, 1]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        optimalFitness = length
        best = genetic.get_best(fnGetFitness, length, optimalFitness,
                                geneset, fnDisplay)
        self.assertEqual(best.Fitness, optimalFitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test(4000))


if __name__ == '__main__':
    unittest.main()
