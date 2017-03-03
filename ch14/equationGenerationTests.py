# File: equationGenerationTests.py
#    from chapter 14 of _Genetic Algorithms with Python_
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


def evaluate(genes, prioritizedOperations):
    equation = genes[:]
    for operationSet in prioritizedOperations:
        iOffset = 0
        for i in range(1, len(equation), 2):
            i += iOffset
            opToken = equation[i]
            if opToken in operationSet:
                leftOperand = equation[i - 1]
                rightOperand = equation[i + 1]
                equation[i - 1] = operationSet[opToken](leftOperand,
                                                        rightOperand)
                del equation[i + 1]
                del equation[i]
                iOffset += -2
    return equation[0]


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def get_fitness(genes, expectedTotal, fnEvaluate):
    result = fnEvaluate(genes)

    if result != expectedTotal:
        fitness = expectedTotal - abs(result - expectedTotal)
    else:
        fitness = 1000 - len(genes)

    return fitness


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t{}\t{}".format(
        (' '.join(map(str, [i for i in candidate.Genes]))),
        candidate.Fitness,
        timeDiff))


def create(numbers, operations, minNumbers, maxNumbers):
    genes = [random.choice(numbers)]
    count = random.randint(minNumbers, 1 + maxNumbers)
    while count > 1:
        count -= 1
        genes.append(random.choice(operations))
        genes.append(random.choice(numbers))
    return genes


def mutate(genes, numbers, operations, minNumbers, maxNumbers,
           fnGetFitness):
    count = random.randint(1, 10)
    initialFitness = fnGetFitness(genes)
    while count > 0:
        count -= 1
        if fnGetFitness(genes) > initialFitness:
            return
        numberCount = (1 + len(genes)) / 2
        adding = numberCount < maxNumbers and random.randint(0, 100) == 0
        if adding:
            genes.append(random.choice(operations))
            genes.append(random.choice(numbers))
            continue

        removing = numberCount > minNumbers and random.randint(0, 20) == 0
        if removing:
            index = random.randrange(0, len(genes) - 1)
            del genes[index]
            del genes[index]
            continue

        index = random.randrange(0, len(genes))
        genes[index] = random.choice(operations) \
            if (index & 1) == 1 else random.choice(numbers)


class EquationGenerationTests(unittest.TestCase):
    def test_addition(self):
        operations = ['+', '-']
        prioritizedOperations = [{'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [7, '+', 7, '+', 7, '+', 7, '+', 7, '-', 6]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def test_multiplication(self):
        operations = ['+', '-', '*']
        prioritizedOperations = [{'*': multiply},
                                 {'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [6, '*', 3, '*', 3, '*', 6, '-', 7]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def test_exponent(self):
        operations = ['^', '+', '-', '*']
        prioritizedOperations = [{'^': lambda a, b: a ** b},
                                 {'*': multiply},
                                 {'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [6, '^', 3, '*', 2, '-', 5]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def solve(self, operations, prioritizedOperations,
              optimalLengthSolution):
        numbers = [1, 2, 3, 4, 5, 6, 7]
        expectedTotal = evaluate(optimalLengthSolution,
                                 prioritizedOperations)
        minNumbers = (1 + len(optimalLengthSolution)) / 2
        maxNumbers = 6 * minNumbers
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnEvaluate(genes):
            return evaluate(genes, prioritizedOperations)

        def fnGetFitness(genes):
            return get_fitness(genes, expectedTotal, fnEvaluate)

        def fnCreate():
            return create(numbers, operations, minNumbers, maxNumbers)

        def fnMutate(child):
            mutate(child, numbers, operations, minNumbers, maxNumbers,
                   fnGetFitness)

        optimalFitness = fnGetFitness(optimalLengthSolution)
        best = genetic.get_best(fnGetFitness, None, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate, maxAge=50)
        self.assertTrue(not optimalFitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(self.test_exponent)


if __name__ == '__main__':
    unittest.main()
