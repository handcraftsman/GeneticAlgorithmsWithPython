# File: knightsTests.py
#    from chapter 7 of _Genetic Algorithms with Python_
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


def get_fitness(genes, boardWidth, boardHeight):
    attacked = set(pos
                   for kn in genes
                   for pos in get_attacks(kn, boardWidth, boardHeight))
    return len(attacked)


def display(candidate, startTime, boardWidth, boardHeight):
    timeDiff = datetime.datetime.now() - startTime
    board = Board(candidate.Genes, boardWidth, boardHeight)
    board.print()

    print("{}\n\t{}\t{}".format(
        ' '.join(map(str, candidate.Genes)),
        candidate.Fitness,
        timeDiff))


def mutate(genes, boardWidth, boardHeight, allPositions, nonEdgePositions):
    count = 2 if random.randint(0, 10) == 0 else 1
    while count > 0:
        count -= 1
        positionToKnightIndexes = dict((p, []) for p in allPositions)
        for i, knight in enumerate(genes):
            for position in get_attacks(knight, boardWidth, boardHeight):
                positionToKnightIndexes[position].append(i)
        knightIndexes = set(i for i in range(len(genes)))
        unattacked = []
        for kvp in positionToKnightIndexes.items():
            if len(kvp[1]) > 1:
                continue
            if len(kvp[1]) == 0:
                unattacked.append(kvp[0])
                continue
            for p in kvp[1]:  # len == 1
                if p in knightIndexes:
                    knightIndexes.remove(p)

        potentialKnightPositions = \
            [p for positions in
             map(lambda x: get_attacks(x, boardWidth, boardHeight),
                 unattacked)
             for p in positions if p in nonEdgePositions] \
                if len(unattacked) > 0 else nonEdgePositions

        geneIndex = random.randrange(0, len(genes)) \
            if len(knightIndexes) == 0 \
            else random.choice([i for i in knightIndexes])

        position = random.choice(potentialKnightPositions)
        genes[geneIndex] = position


def create(fnGetRandomPosition, expectedKnights):
    genes = [fnGetRandomPosition() for _ in range(expectedKnights)]
    return genes


def get_attacks(location, boardWidth, boardHeight):
    return [i for i in set(
        Position(x + location.X, y + location.Y)
        for x in [-2, -1, 1, 2] if 0 <= x + location.X < boardWidth
        for y in [-2, -1, 1, 2] if 0 <= y + location.Y < boardHeight
        and abs(y) != abs(x))]


class KnightsTests(unittest.TestCase):
    def test_3x4(self):
        width = 4
        height = 3
        # 1,0   2,0   3,0
        # 0,2   1,2   2,2
        # 2 	 N N N .
        # 1 	 . . . .
        # 0 	 . N N N
        #   	 0 1 2 3
        self.find_knight_positions(width, height, 6)

    def test_8x8(self):
        width = 8
        height = 8
        self.find_knight_positions(width, height, 14)

    def test_10x10(self):
        width = 10
        height = 10
        self.find_knight_positions(width, height, 22)

    def test_12x12(self):
        width = 12
        height = 12
        self.find_knight_positions(width, height, 28)

    def test_13x13(self):
        width = 13
        height = 13
        self.find_knight_positions(width, height, 32)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_10x10())

    def find_knight_positions(self, boardWidth, boardHeight, expectedKnights):
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime, boardWidth, boardHeight)

        def fnGetFitness(genes):
            return get_fitness(genes, boardWidth, boardHeight)

        allPositions = [Position(x, y)
                        for y in range(boardHeight)
                        for x in range(boardWidth)]

        if boardWidth < 6 or boardHeight < 6:
            nonEdgePositions = allPositions
        else:
            nonEdgePositions = [i for i in allPositions
                                if 0 < i.X < boardWidth - 1 and
                                0 < i.Y < boardHeight - 1]

        def fnGetRandomPosition():
            return random.choice(nonEdgePositions)

        def fnMutate(genes):
            mutate(genes, boardWidth, boardHeight, allPositions,
                   nonEdgePositions)

        def fnCreate():
            return create(fnGetRandomPosition, expectedKnights)

        optimalFitness = boardWidth * boardHeight
        best = genetic.get_best(fnGetFitness, None, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate)
        self.assertTrue(not optimalFitness > best.Fitness)


class Position:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "{},{}".format(self.X, self.Y)

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

    def __hash__(self):
        return self.X * 1000 + self.Y


class Board:
    def __init__(self, positions, width, height):
        board = [['.'] * width for _ in range(height)]

        for index in range(len(positions)):
            knightPosition = positions[index]
            board[knightPosition.Y][knightPosition.X] = 'N'
        self._board = board
        self._width = width
        self._height = height

    def print(self):
        # 0,0 prints in bottom left corner
        for i in reversed(range(self._height)):
            print(i, "\t", ' '.join(self._board[i]))
        print(" \t", ' '.join(map(str, range(self._width))))


if __name__ == '__main__':
    unittest.main()
