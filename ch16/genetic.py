# File: genetic.py
#    from chapter 16 of _Genetic Algorithms with Python_
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

import random
import statistics
import sys
import time
from bisect import bisect_left
from enum import Enum
from math import exp


def _generate_parent(length, geneSet, get_fitness):
    genes = []
    while len(genes) < length:
        sampleSize = min(length - len(genes), len(geneSet))
        genes.extend(random.sample(geneSet, sampleSize))
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness, Strategies.Create)


def _mutate(parent, geneSet, get_fitness):
    childGenes = parent.Genes[:]
    index = random.randrange(0, len(parent.Genes))
    newGene, alternate = random.sample(geneSet, 2)
    childGenes[index] = alternate if newGene == childGenes[index] else newGene
    fitness = get_fitness(childGenes)
    return Chromosome(childGenes, fitness, Strategies.Mutate)


def _mutate_custom(parent, custom_mutate, get_fitness):
    childGenes = parent.Genes[:]
    custom_mutate(childGenes)
    fitness = get_fitness(childGenes)
    return Chromosome(childGenes, fitness, Strategies.Mutate)


def _crossover(parentGenes, index, parents, get_fitness, crossover, mutate,
               generate_parent):
    donorIndex = random.randrange(0, len(parents))
    if donorIndex == index:
        donorIndex = (donorIndex + 1) % len(parents)
    childGenes = crossover(parentGenes, parents[donorIndex].Genes)
    if childGenes is None:
        # parent and donor are indistinguishable
        parents[donorIndex] = generate_parent()
        return mutate(parents[index])
    fitness = get_fitness(childGenes)
    return Chromosome(childGenes, fitness, Strategies.Crossover)


def get_best(get_fitness, targetLen, optimalFitness, geneSet, display,
             custom_mutate=None, custom_create=None, maxAge=None,
             poolSize=1, crossover=None, maxSeconds=None):
    if custom_mutate is None:
        def fnMutate(parent):
            return _mutate(parent, geneSet, get_fitness)
    else:
        def fnMutate(parent):
            return _mutate_custom(parent, custom_mutate, get_fitness)

    if custom_create is None:
        def fnGenerateParent():
            return _generate_parent(targetLen, geneSet, get_fitness)
    else:
        def fnGenerateParent():
            genes = custom_create()
            return Chromosome(genes, get_fitness(genes), Strategies.Create)

    strategyLookup = {
        Strategies.Create: lambda p, i, o: fnGenerateParent(),
        Strategies.Mutate: lambda p, i, o: fnMutate(p),
        Strategies.Crossover: lambda p, i, o:
        _crossover(p.Genes, i, o, get_fitness, crossover, fnMutate,
                   fnGenerateParent)
    }

    usedStrategies = [strategyLookup[Strategies.Mutate]]
    if crossover is not None:
        usedStrategies.append(strategyLookup[Strategies.Crossover])

        def fnNewChild(parent, index, parents):
            return random.choice(usedStrategies)(parent, index, parents)
    else:
        def fnNewChild(parent, index, parents):
            return fnMutate(parent)

    for timedOut, improvement in _get_improvement(fnNewChild,
                                                  fnGenerateParent, maxAge,
                                                  poolSize, maxSeconds):
        if timedOut:
            return improvement
        display(improvement)
        f = strategyLookup[improvement.Strategy]
        usedStrategies.append(f)
        if not optimalFitness > improvement.Fitness:
            return improvement


def _get_improvement(new_child, generate_parent, maxAge, poolSize,
                     maxSeconds):
    startTime = time.time()
    bestParent = generate_parent()
    yield maxSeconds is not None and time.time() \
          - startTime > maxSeconds, bestParent
    parents = [bestParent]
    historicalFitnesses = [bestParent.Fitness]
    for _ in range(poolSize - 1):
        parent = generate_parent()
        if maxSeconds is not None and time.time() - startTime > maxSeconds:
            yield True, parent
        if parent.Fitness > bestParent.Fitness:
            yield False, parent
            bestParent = parent
            historicalFitnesses.append(parent.Fitness)
        parents.append(parent)
    lastParentIndex = poolSize - 1
    pindex = 1
    while True:
        if maxSeconds is not None and time.time() - startTime > maxSeconds:
            yield True, bestParent
        pindex = pindex - 1 if pindex > 0 else lastParentIndex
        parent = parents[pindex]
        child = new_child(parent, pindex, parents)
        if parent.Fitness > child.Fitness:
            if maxAge is None:
                continue
            parent.Age += 1
            if maxAge > parent.Age:
                continue
            index = bisect_left(historicalFitnesses, child.Fitness, 0,
                                len(historicalFitnesses))
            difference = len(historicalFitnesses) - index
            proportionSimilar = difference / len(historicalFitnesses)
            if random.random() < exp(-proportionSimilar):
                parents[pindex] = child
                continue
            parents[pindex] = bestParent
            parent.Age = 0
            continue
        if not child.Fitness > parent.Fitness:
            # same fitness
            child.Age = parent.Age + 1
            parents[pindex] = child
            continue
        parents[pindex] = child
        parent.Age = 0
        if child.Fitness > bestParent.Fitness:
            yield False, child
            bestParent = child
            historicalFitnesses.append(child.Fitness)


def hill_climbing(optimizationFunction, is_improvement, is_optimal,
                  get_next_feature_value, display, initialFeatureValue):
    best = optimizationFunction(initialFeatureValue)
    stdout = sys.stdout
    sys.stdout = None
    while not is_optimal(best):
        featureValue = get_next_feature_value(best)
        child = optimizationFunction(featureValue)
        if is_improvement(best, child):
            best = child
            sys.stdout = stdout
            display(best, featureValue)
            sys.stdout = None
    sys.stdout = stdout
    return best


class Chromosome:
    def __init__(self, genes, fitness, strategy):
        self.Genes = genes
        self.Fitness = fitness
        self.Strategy = strategy
        self.Age = 0


class Strategies(Enum):
    Create = 0,
    Mutate = 1,
    Crossover = 2


class Benchmark:
    @staticmethod
    def run(function):
        timings = []
        stdout = sys.stdout
        for i in range(100):
            sys.stdout = None
            startTime = time.time()
            function()
            seconds = time.time() - startTime
            sys.stdout = stdout
            timings.append(seconds)
            mean = statistics.mean(timings)
            if i < 10 or i % 10 == 9:
                print("{} {:3.2f} {:3.2f}".format(
                    1 + i, mean,
                    statistics.stdev(timings, mean) if i > 1 else 0))
