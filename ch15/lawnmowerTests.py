# File: lawnmowerTests.py
#    from chapter 15 of _Genetic Algorithms with Python_
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
import lawnmower


def get_fitness(genes, fnEvaluate):
    field, mower, _ = fnEvaluate(genes)
    return Fitness(field.count_mowed(), len(genes), mower.StepCount)


def display(candidate, startTime, fnEvaluate):
    field, mower, program = fnEvaluate(candidate.Genes)
    timeDiff = datetime.datetime.now() - startTime
    field.display(mower)
    print("{}\t{}".format(
        candidate.Fitness,
        timeDiff))
    program.print()


def mutate(genes, geneSet, minGenes, maxGenes, fnGetFitness, maxRounds):
    count = random.randint(1, maxRounds)
    initialFitness = fnGetFitness(genes)
    while count > 0:
        count -= 1
        if fnGetFitness(genes) > initialFitness:
            return

        adding = len(genes) == 0 or \
                 (len(genes) < maxGenes and random.randint(0, 5) == 0)
        if adding:
            genes.append(random.choice(geneSet)())
            continue

        removing = len(genes) > minGenes and random.randint(0, 50) == 0
        if removing:
            index = random.randrange(0, len(genes))
            del genes[index]
            continue

        index = random.randrange(0, len(genes))
        genes[index] = random.choice(geneSet)()


def create(geneSet, minGenes, maxGenes):
    numGenes = random.randint(minGenes, maxGenes)
    genes = [random.choice(geneSet)() for _ in range(1, numGenes)]
    return genes


def crossover(parent, otherParent):
    childGenes = parent[:]
    if len(parent) <= 2 or len(otherParent) < 2:
        return childGenes
    length = random.randint(1, len(parent) - 2)
    start = random.randrange(0, len(parent) - length)
    childGenes[start:start + length] = otherParent[start:start + length]
    return childGenes


class LawnmowerTests(unittest.TestCase):
    def test_mow_turn(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn()]
        minGenes = width * height
        maxGenes = int(1.5 * minGenes)
        maxMutationRounds = 3
        expectedNumberOfInstructions = 78

        def fnCreateField():
            return lawnmower.ToroidField(width, height,
                                         lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfInstructions)

    def test_mow_turn_jump(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn(),
                   lambda: Jump(random.randint(0, min(width, height)),
                                random.randint(0, min(width, height)))]
        minGenes = width * height
        maxGenes = int(1.5 * minGenes)
        maxMutationRounds = 1
        expectedNumberOfInstructions = 64

        def fnCreateField():
            return lawnmower.ToroidField(width, height,
                                         lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfInstructions)

    def test_mow_turn_jump_validating(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn(),
                   lambda: Jump(random.randint(0, min(width, height)),
                                random.randint(0, min(width, height)))]
        minGenes = width * height
        maxGenes = int(1.5 * minGenes)
        maxMutationRounds = 3
        expectedNumberOfInstructions = 79

        def fnCreateField():
            return lawnmower.ValidatingField(width, height,
                                             lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfInstructions)

    def test_mow_turn_repeat(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn(),
                   lambda: Repeat(random.randint(0, 8),
                                  random.randint(0, 8))]
        minGenes = 3
        maxGenes = 20
        maxMutationRounds = 3
        expectedNumberOfInstructions = 9
        expectedNumberOfSteps = 88

        def fnCreateField():
            return lawnmower.ToroidField(width, height,
                                         lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfSteps)

    def test_mow_turn_jump_func(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn(),
                   lambda: Jump(random.randint(0, min(width, height)),
                                random.randint(0, min(width, height))),
                   lambda: Func()]
        minGenes = 3
        maxGenes = 20
        maxMutationRounds = 3
        expectedNumberOfInstructions = 18
        expectedNumberOfSteps = 65

        def fnCreateField():
            return lawnmower.ToroidField(width, height,
                                         lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfSteps)

    def test_mow_turn_jump_call(self):
        width = height = 8
        geneSet = [lambda: Mow(),
                   lambda: Turn(),
                   lambda: Jump(random.randint(0, min(width, height)),
                                random.randint(0, min(width, height))),
                   lambda: Func(expectCall=True),
                   lambda: Call(random.randint(0, 5))]
        minGenes = 3
        maxGenes = 20
        maxMutationRounds = 3
        expectedNumberOfInstructions = 18
        expectedNumberOfSteps = 65

        def fnCreateField():
            return lawnmower.ToroidField(width, height,
                                         lawnmower.FieldContents.Grass)

        self.run_with(geneSet, width, height, minGenes, maxGenes,
                      expectedNumberOfInstructions, maxMutationRounds,
                      fnCreateField, expectedNumberOfSteps)

    def run_with(self, geneSet, width, height, minGenes, maxGenes,
                 expectedNumberOfInstructions, maxMutationRounds,
                 fnCreateField, expectedNumberOfSteps):
        mowerStartLocation = lawnmower.Location(int(width / 2),
                                                int(height / 2))
        mowerStartDirection = lawnmower.Directions.South.value

        def fnCreate():
            return create(geneSet, 1, height)

        def fnEvaluate(instructions):
            program = Program(instructions)
            mower = lawnmower.Mower(mowerStartLocation, mowerStartDirection)
            field = fnCreateField()
            try:
                program.evaluate(mower, field)
            except RecursionError:
                pass
            return field, mower, program

        def fnGetFitness(genes):
            return get_fitness(genes, fnEvaluate)

        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime, fnEvaluate)

        def fnMutate(child):
            mutate(child, geneSet, minGenes, maxGenes, fnGetFitness,
                   maxMutationRounds)

        optimalFitness = Fitness(width * height,
                                 expectedNumberOfInstructions,
                                 expectedNumberOfSteps)

        best = genetic.get_best(fnGetFitness, None, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate, maxAge=None,
                                poolSize=10, crossover=crossover)

        self.assertTrue(not optimalFitness > best.Fitness)


class Mow:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower, field):
        mower.mow(field)

    def __str__(self):
        return "mow"


class Turn:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower, field):
        mower.turn_left()

    def __str__(self):
        return "turn"


class Jump:
    def __init__(self, forward, right):
        self.Forward = forward
        self.Right = right

    def execute(self, mower, field):
        mower.jump(field, self.Forward, self.Right)

    def __str__(self):
        return "jump({},{})".format(self.Forward, self.Right)


class Repeat:
    def __init__(self, opCount, times):
        self.OpCount = opCount
        self.Times = times
        self.Ops = []

    def execute(self, mower, field):
        for i in range(self.Times):
            for op in self.Ops:
                op.execute(mower, field)

    def __str__(self):
        return "repeat({},{})".format(
            ' '.join(map(str, self.Ops))
            if len(self.Ops) > 0
            else self.OpCount,
            self.Times)


class Func:
    def __init__(self, expectCall=False):
        self.Ops = []
        self.ExpectCall = expectCall
        self.Id = None

    def execute(self, mower, field):
        for op in self.Ops:
            op.execute(mower, field)

    def __str__(self):
        return "func{1}: {0}".format(
            ' '.join(map(str, self.Ops)),
            self.Id if self.Id is not None else '')


class Call:
    def __init__(self, funcId=None):
        self.FuncId = funcId
        self.Funcs = None

    def execute(self, mower, field):
        funcId = 0 if self.FuncId is None else self.FuncId
        if len(self.Funcs) > funcId:
            self.Funcs[funcId].execute(mower, field)

    def __str__(self):
        return "call-{}".format(
            self.FuncId
            if self.FuncId is not None
            else 'func')


class Program:
    def __init__(self, genes):
        temp = genes[:]
        funcs = []

        for index in reversed(range(len(temp))):
            if type(temp[index]) is Repeat:
                start = index + 1
                end = min(index + temp[index].OpCount + 1, len(temp))
                temp[index].Ops = temp[start:end]
                del temp[start:end]
                continue

            if type(temp[index]) is Call:
                temp[index].Funcs = funcs

            if type(temp[index]) is Func:
                if len(funcs) > 0 and not temp[index].ExpectCall:
                    temp[index] = Call()
                    temp[index].Funcs = funcs
                    continue
                start = index + 1
                end = len(temp)
                func = Func()
                if temp[index].ExpectCall:
                    func.Id = len(funcs)
                func.Ops = [i for i in temp[start:end]
                            if type(i) is not Repeat or
                            type(i) is Repeat and len(i.Ops) > 0
                            ]
                funcs.append(func)
                del temp[index:end]

        for func in funcs:
            for index in reversed(range(len(func.Ops))):
                 if type(func.Ops[index]) is Call:
                    func_id = func.Ops[index].FuncId
                    if func_id is None:
                        continue
                    if func_id >= len(funcs) or \
                                    len(funcs[func_id].Ops) == 0:
                        del func.Ops[index]

        for index in reversed(range(len(temp))):
            if type(temp[index]) is Call:
                func_id = temp[index].FuncId
                if func_id is None:
                    continue
                if func_id >= len(funcs) or \
                                len(funcs[func_id].Ops) == 0:
                    del temp[index]
        self.Main = temp
        self.Funcs = funcs

    def evaluate(self, mower, field):
        for i, instruction in enumerate(self.Main):
            instruction.execute(mower, field)

    def print(self):
        if self.Funcs is not None:
            for func in self.Funcs:
                if func.Id is not None and len(func.Ops) == 0:
                    continue
                print(func)
        print(' '.join(map(str, self.Main)))


class Fitness:
    def __init__(self, totalMowed, totalInstructions, stepCount):
        self.TotalMowed = totalMowed
        self.TotalInstructions = totalInstructions
        self.StepCount = stepCount

    def __gt__(self, other):
        if self.TotalMowed != other.TotalMowed:
            return self.TotalMowed > other.TotalMowed
        if self.StepCount != other.StepCount:
            return self.StepCount < other.StepCount
        return self.TotalInstructions < other.TotalInstructions

    def __str__(self):
        return "{} mowed with {} instructions and {} steps".format(
            self.TotalMowed, self.TotalInstructions, self.StepCount)


if __name__ == '__main__':
    unittest.main()
