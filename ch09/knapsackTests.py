# File: knapsackTests.py
#    from chapter 9 of _Genetic Algorithms with Python_
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
import sys
import unittest

import genetic


def get_fitness(genes):
    totalWeight = 0
    totalVolume = 0
    totalValue = 0
    for iq in genes:
        count = iq.Quantity
        totalWeight += iq.Item.Weight * count
        totalVolume += iq.Item.Volume * count
        totalValue += iq.Item.Value * count

    return Fitness(totalWeight, totalVolume, totalValue)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    genes = candidate.Genes[:]
    genes.sort(key=lambda iq: iq.Quantity, reverse=True)

    descriptions = [str(iq.Quantity) + "x" + iq.Item.Name for iq in genes]
    if len(descriptions) == 0:
        descriptions.append("Empty")
    print("{}\t{}\t{}".format(
        ', '.join(descriptions),
        candidate.Fitness,
        timeDiff))


def max_quantity(item, maxWeight, maxVolume):
    return min(int(maxWeight / item.Weight)
               if item.Weight > 0 else sys.maxsize,
               int(maxVolume / item.Volume)
               if item.Volume > 0 else sys.maxsize)


def create(items, maxWeight, maxVolume):
    genes = []
    remainingWeight, remainingVolume = maxWeight, maxVolume
    for i in range(random.randrange(1, len(items))):
        newGene = add(genes, items, remainingWeight, remainingVolume)
        if newGene is not None:
            genes.append(newGene)
            remainingWeight -= newGene.Quantity * newGene.Item.Weight
            remainingVolume -= newGene.Quantity * newGene.Item.Volume
    return genes


def add(genes, items, maxWeight, maxVolume):
    usedItems = {iq.Item for iq in genes}
    item = random.choice(items)
    while item in usedItems:
        item = random.choice(items)

    maxQuantity = max_quantity(item, maxWeight, maxVolume)
    return ItemQuantity(item, maxQuantity) if maxQuantity > 0 else None


def mutate(genes, items, maxWeight, maxVolume, window):
    window.slide()
    fitness = get_fitness(genes)
    remainingWeight = maxWeight - fitness.TotalWeight
    remainingVolume = maxVolume - fitness.TotalVolume

    removing = len(genes) > 1 and random.randint(0, 10) == 0
    if removing:
        index = random.randrange(0, len(genes))
        iq = genes[index]
        item = iq.Item
        remainingWeight += item.Weight * iq.Quantity
        remainingVolume += item.Volume * iq.Quantity
        del genes[index]

    adding = (remainingWeight > 0 or remainingVolume > 0) and \
             (len(genes) == 0 or
              (len(genes) < len(items) and random.randint(0, 100) == 0))

    if adding:
        newGene = add(genes, items, remainingWeight, remainingVolume)
        if newGene is not None:
            genes.append(newGene)
            return

    index = random.randrange(0, len(genes))
    iq = genes[index]
    item = iq.Item
    remainingWeight += item.Weight * iq.Quantity
    remainingVolume += item.Volume * iq.Quantity

    changeItem = len(genes) < len(items) and random.randint(0, 4) == 0
    if changeItem:
        itemIndex = items.index(iq.Item)
        start = max(1, itemIndex - window.Size)
        stop = min(len(items) - 1, itemIndex + window.Size)
        item = items[random.randint(start, stop)]
    maxQuantity = max_quantity(item, remainingWeight, remainingVolume)
    if maxQuantity > 0:
        genes[index] = ItemQuantity(item, maxQuantity
        if window.Size > 1 else random.randint(1, maxQuantity))
    else:
        del genes[index]


class KnapsackTests(unittest.TestCase):
    def test_cookies(self):
        items = [
            Resource("Flour", 1680, 0.265, .41),
            Resource("Butter", 1440, 0.5, .13),
            Resource("Sugar", 1840, 0.441, .29)
        ]
        maxWeight = 10
        maxVolume = 4
        optimal = get_fitness(
            [ItemQuantity(items[0], 1),
             ItemQuantity(items[1], 14),
             ItemQuantity(items[2], 6)])
        self.fill_knapsack(items, maxWeight, maxVolume, optimal)

    def test_exnsd16(self):
        problemInfo = load_data("exnsd16.ukp")
        items = problemInfo.Resources
        maxWeight = problemInfo.MaxWeight
        maxVolume = 0
        optimal = get_fitness(problemInfo.Solution)
        self.fill_knapsack(items, maxWeight, maxVolume, optimal)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_exnsd16())

    def fill_knapsack(self, items, maxWeight, maxVolume, optimalFitness):
        startTime = datetime.datetime.now()
        window = Window(1,
                        max(1, int(len(items) / 3)),
                        int(len(items) / 2))

        sortedItems = sorted(items, key=lambda item: item.Value)

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        def fnCreate():
            return create(items, maxWeight, maxVolume)

        def fnMutate(genes):
            mutate(genes, sortedItems, maxWeight, maxVolume, window)

        best = genetic.get_best(fnGetFitness, None, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate, maxAge=50)
        self.assertTrue(not optimalFitness > best.Fitness)


def load_data(localFileName):
    with open(localFileName, mode='r') as infile:
        lines = infile.read().splitlines()
    data = KnapsackProblemData()
    f = find_constraint

    for line in lines:
        f = f(line.strip(), data)
        if f is None:
            break
    return data


def find_constraint(line, data):
    parts = line.split(' ')
    if parts[0] != "c:":
        return find_constraint
    data.MaxWeight = int(parts[1])
    return find_data_start


def find_data_start(line, data):
    if line != "begin data":
        return find_data_start
    return read_resource_or_find_data_end


def read_resource_or_find_data_end(line, data):
    if line == "end data":
        return find_solution_start
    parts = line.split('\t')
    resource = Resource("R" + str(1 + len(data.Resources)), int(parts[1]),
                        int(parts[0]), 0)
    data.Resources.append(resource)
    return read_resource_or_find_data_end


def find_solution_start(line, data):
    if line == "sol:":
        return read_solution_resource_or_find_solution_end
    return find_solution_start


def read_solution_resource_or_find_solution_end(line, data):
    if line == "":
        return None
    parts = [p for p in line.split('\t') if p != ""]
    resourceIndex = int(parts[0]) - 1  # make it 0 based
    resourceQuantity = int(parts[1])
    data.Solution.append(
        ItemQuantity(data.Resources[resourceIndex], resourceQuantity))
    return read_solution_resource_or_find_solution_end


class Resource:
    def __init__(self, name, value, weight, volume):
        self.Name = name
        self.Value = value
        self.Weight = weight
        self.Volume = volume


class ItemQuantity:
    def __init__(self, item, quantity):
        self.Item = item
        self.Quantity = quantity

    def __eq__(self, other):
        return self.Item == other.Item and self.Quantity == other.Quantity


class Fitness:
    def __init__(self, totalWeight, totalVolume, totalValue):
        self.TotalWeight = totalWeight
        self.TotalVolume = totalVolume
        self.TotalValue = totalValue

    def __gt__(self, other):
        if self.TotalValue != other.TotalValue:
            return self.TotalValue > other.TotalValue
        if self.TotalWeight != other.TotalWeight:
            return self.TotalWeight < other.TotalWeight
        return self.TotalVolume < other.TotalVolume

    def __str__(self):
        return "wt: {:0.2f} vol: {:0.2f} value: {}".format(
            self.TotalWeight,
            self.TotalVolume,
            self.TotalValue)


class KnapsackProblemData:
    def __init__(self):
        self.Resources = []
        self.MaxWeight = 0
        self.Solution = []


class Window:
    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size

    def slide(self):
        self.Size = self.Size - 1 if self.Size > self.Min else self.Max


if __name__ == '__main__':
    unittest.main()
