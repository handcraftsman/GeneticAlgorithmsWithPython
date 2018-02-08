# File: ticTacToeTests.py
#    from chapter 18 of _Genetic Algorithms with Python_
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
from functools import partial

import genetic


def get_fitness(genes):
    localCopy = genes[:]
    fitness = get_fitness_for_games(localCopy)
    fitness.GeneCount = len(genes)
    return fitness


squareIndexes = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def play1on1(xGenes, oGenes):
    board = dict((i, Square(i, ContentType.Empty)) for i in range(1, 9 + 1))
    empties = [v for v in board.values() if v.Content == ContentType.Empty]
    roundData = [[xGenes, ContentType.Mine, genetic.CompetitionResult.Loss,
                  genetic.CompetitionResult.Win],
                 [oGenes, ContentType.Opponent, genetic.CompetitionResult.Win,
                  genetic.CompetitionResult.Loss]]
    playerIndex = 0

    while len(empties) > 0:
        playerData = roundData[playerIndex]
        playerIndex = 1 - playerIndex
        genes, piece, lossResult, winResult = playerData

        moveAndRuleIndex = get_move(genes, board, empties)
        if moveAndRuleIndex is None:  # could not find a move
            return lossResult

        index = moveAndRuleIndex[0]
        board[index] = Square(index, piece)

        mostRecentMoveOnly = [board[index]]
        if len(RowContentFilter(piece, 3).get_matches(board, mostRecentMoveOnly)) > 0 or \
           len(ColumnContentFilter(piece, 3).get_matches(board, mostRecentMoveOnly)) > 0 or \
           len(DiagonalContentFilter(piece, 3).get_matches(board, mostRecentMoveOnly)) > 0:
            return winResult
        empties = [v for v in board.values() if v.Content == ContentType.Empty]
    return genetic.CompetitionResult.Tie


def get_fitness_for_games(genes):
    def getBoardString(b):
        return ''.join(map(lambda i:
                           '.' if b[i].Content == ContentType.Empty
                           else 'x' if b[i].Content == ContentType.Mine
                           else 'o', squareIndexes))

    board = dict((i, Square(i, ContentType.Empty)) for i in range(1, 9 + 1))

    queue = [board]
    for square in board.values():
        candiateCopy = board.copy()
        candiateCopy[square.Index] = Square(square.Index, ContentType.Opponent)
        queue.append(candiateCopy)

    winningRules = {}
    wins = ties = losses = 0

    while len(queue) > 0:
        board = queue.pop()
        boardString = getBoardString(board)
        empties = [v for v in board.values() if v.Content == ContentType.Empty]

        if len(empties) == 0:
            ties += 1
            continue

        candidateIndexAndRuleIndex = get_move(genes, board, empties)

        if candidateIndexAndRuleIndex is None:  # could not find a move
            # there are empties but didn't find a move
            losses += 1
            # go to next board
            continue

        # found at least one move
        index = candidateIndexAndRuleIndex[0]
        board[index] = Square(index, ContentType.Mine)
        # newBoardString = getBoardString(board)

        # if we now have three MINE in any ROW, COLUMN or DIAGONAL, we won
        mostRecentMoveOnly = [board[index]]
        if len(iHaveThreeInRow.get_matches(board, mostRecentMoveOnly)) > 0 or \
             len(iHaveThreeInColumn.get_matches(board, mostRecentMoveOnly)) > 0 or \
             len(iHaveThreeInDiagonal.get_matches(board, mostRecentMoveOnly)) > 0:
            ruleId = candidateIndexAndRuleIndex[1]
            if ruleId not in winningRules:
                winningRules[ruleId] = list()
            winningRules[ruleId].append(boardString)
            wins += 1
            # go to next board
            continue

        # we lose if any empties have two OPPONENT pieces in ROW, COL or DIAG
        empties = [v for v in board.values() if v.Content == ContentType.Empty]
        if len(opponentHasTwoInARow.get_matches(board, empties)) > 0:
            losses += 1
            # go to next board
            continue

        # queue all possible OPPONENT responses
        for square in empties:
            candiateCopy = board.copy()
            candiateCopy[square.Index] = Square(square.Index,
                                                ContentType.Opponent)
            queue.append(candiateCopy)

    return Fitness(wins, ties, losses, len(genes))


def get_move(ruleSet, board, empties, startingRuleIndex=0):
    ruleSetCopy = ruleSet[:]

    for ruleIndex in range(startingRuleIndex, len(ruleSetCopy)):
        gene = ruleSetCopy[ruleIndex]
        matches = gene.get_matches(board, empties)
        if len(matches) == 0:
            continue
        if len(matches) == 1:
            return [list(matches)[0], ruleIndex]
        if len(empties) > len(matches):
            empties = [e for e in empties if e.Index in matches]

    return None


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    localCopy = candidate.Genes[:]
    for i in reversed(range(len(localCopy))):
        localCopy[i] = str(localCopy[i])

    print("\t{}\n{}\n{}".format(
        '\n\t'.join([d for d in localCopy]),
        candidate.Fitness,
        timeDiff))


def mutate_add(genes, geneset):
    index = random.randrange(0, len(genes) + 1) if len(genes) > 0 else 0
    genes[index:index] = [random.choice(geneset)]
    return True


def mutate_remove(genes):
    if len(genes) < 1:
        return False
    del genes[random.randrange(0, len(genes))]
    if len(genes) > 1 and random.randint(0, 1) == 1:
        del genes[random.randrange(0, len(genes))]
    return True


def mutate_replace(genes, geneset):
    if len(genes) < 1:
        return False
    index = random.randrange(0, len(genes))
    genes[index] = random.choice(geneset)
    return True


def mutate_swap_adjacent(genes):
    if len(genes) < 2:
        return False
    index = random.choice(range(len(genes) - 1))
    genes[index], genes[index + 1] = genes[index + 1], genes[index]
    return True


def mutate_move(genes):
    if len(genes) < 3:
        return False
    start = random.choice(range(len(genes)))
    stop = start + random.randint(1, 2)
    toMove = genes[start:stop]
    genes[start:stop] = []
    index = random.choice(range(len(genes)))
    if index >= start:
        index += 1
    genes[index:index] = toMove
    return True


def mutate(genes, fnGetFitness, mutationOperators, mutationRoundCounts):
    initialFitness = fnGetFitness(genes)
    count = random.choice(mutationRoundCounts)
    for i in range(1, count + 2):
        copy = mutationOperators[:]
        func = random.choice(copy)
        while not func(genes):
            copy.remove(func)
            func = random.choice(copy)
        if fnGetFitness(genes) > initialFitness:
            mutationRoundCounts.append(i)
            return


def create_geneset():
    options = [[ContentType.Opponent, [0, 1, 2]],
               [ContentType.Mine, [0, 1, 2]]]
    geneset = [
        RuleMetadata(RowContentFilter, options),
        RuleMetadata(lambda expectedContent, count: TopRowFilter(), options),
        RuleMetadata(lambda expectedContent, count: MiddleRowFilter(),
                     options),
        RuleMetadata(lambda expectedContent, count: BottomRowFilter(),
                     options),
        RuleMetadata(ColumnContentFilter, options),
        RuleMetadata(lambda expectedContent, count: LeftColumnFilter(),
                     options),
        RuleMetadata(lambda expectedContent, count: MiddleColumnFilter(),
                     options),
        RuleMetadata(lambda expectedContent, count: RightColumnFilter(),
                     options),
        RuleMetadata(DiagonalContentFilter, options),
        RuleMetadata(lambda expectedContent, count: DiagonalLocationFilter(),
                     options),
        RuleMetadata(lambda expectedContent, count: CornerFilter()),
        RuleMetadata(lambda expectedContent, count: SideFilter()),
        RuleMetadata(lambda expectedContent, count: CenterFilter()),
        RuleMetadata(lambda expectedContent, count:
                     RowOppositeFilter(expectedContent), options,
                     needsSpecificContent=True),
        RuleMetadata(lambda expectedContent, count: ColumnOppositeFilter(
            expectedContent), options, needsSpecificContent=True),
        RuleMetadata(lambda expectedContent, count: DiagonalOppositeFilter(
            expectedContent), options, needsSpecificContent=True),
    ]

    genes = list()
    for gene in geneset:
        genes.extend(gene.create_rules())

    print("created " + str(len(genes)) + " genes")
    return genes


class TicTacToeTests(unittest.TestCase):
    def test_perfect_knowledge(self):
        minGenes = 10
        maxGenes = 20
        geneset = create_geneset()
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        mutationRoundCounts = [1]

        mutationOperators = [
            partial(mutate_add, geneset=geneset),
            partial(mutate_replace, geneset=geneset),
            mutate_remove,
            mutate_swap_adjacent,
            mutate_move,
        ]

        def fnMutate(genes):
            mutate(genes, fnGetFitness, mutationOperators, mutationRoundCounts)

        def fnCrossover(parent, donor):
            child = parent[0:int(len(parent) / 2)] + \
                    donor[int(len(donor) / 2):]
            fnMutate(child)
            return child

        def fnCreate():
            return random.sample(geneset, random.randrange(minGenes, maxGenes))

        optimalFitness = Fitness(620, 120, 0, 11)
        best = genetic.get_best(fnGetFitness, minGenes, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate, maxAge=500,
                                poolSize=20, crossover=fnCrossover)
        self.assertTrue(not optimalFitness > best.Fitness)

    def test_tornament(self):
        minGenes = 10
        maxGenes = 20
        geneset = create_geneset()
        startTime = datetime.datetime.now()

        def fnDisplay(genes, wins, ties, losses, generation):
            print("-- generation {} --".format(generation))
            display(genetic.Chromosome(genes,
                                       Fitness(wins, ties, losses, len(genes)),
                                       None), startTime)

        mutationRoundCounts = [1]

        mutationOperators = [
            partial(mutate_add, geneset=geneset),
            partial(mutate_replace, geneset=geneset),
            mutate_remove,
            mutate_swap_adjacent,
            mutate_move,
        ]

        def fnMutate(genes):
            mutate(genes, lambda x: 0, mutationOperators, mutationRoundCounts)

        def fnCrossover(parent, donor):
            child = parent[0:int(len(parent) / 2)] + \
                    donor[int(len(donor) / 2):]
            fnMutate(child)
            return child

        def fnCreate():
            return random.sample(geneset, random.randrange(minGenes, maxGenes))

        def fnSortKey(genes, wins, ties, losses):
            return -1000 * losses - ties + 1 / len(genes)

        genetic.tournament(fnCreate, fnCrossover, play1on1, fnDisplay,
                           fnSortKey, 13)


class ContentType:
    Empty = 'EMPTY'
    Mine = 'MINE'
    Opponent = 'OPPONENT'


class Square:
    def __init__(self, index, content=ContentType.Empty):
        self.Content = content
        self.Index = index
        self.Diagonals = []
        # board layout is
        #   1  2  3
        #   4  5  6
        #   7  8  9
        self.IsCenter = False
        self.IsCorner = False
        self.IsSide = False
        self.IsTopRow = False
        self.IsMiddleRow = False
        self.IsBottomRow = False
        self.IsLeftColumn = False
        self.IsMiddleColumn = False
        self.IsRightColumn = False
        self.Row = None
        self.Column = None
        self.DiagonalOpposite = None
        self.RowOpposite = None
        self.ColumnOpposite = None

        if index == 1 or index == 2 or index == 3:
            self.IsTopRow = True
            self.Row = [1, 2, 3]
        elif index == 4 or index == 5 or index == 6:
            self.IsMiddleRow = True
            self.Row = [4, 5, 6]
        elif index == 7 or index == 8 or index == 9:
            self.IsBottomRow = True
            self.Row = [7, 8, 9]

        if index % 3 == 1:
            self.Column = [1, 4, 7]
            self.IsLeftColumn = True
        elif index % 3 == 2:
            self.Column = [2, 5, 8]
            self.IsMiddleColumn = True
        elif index % 3 == 0:
            self.Column = [3, 6, 9]
            self.IsRightColumn = True

        if index == 5:
            self.IsCenter = True
        else:
            if index == 1 or index == 3 or index == 7 or index == 9:
                self.IsCorner = True
            elif index == 2 or index == 4 or index == 6 or index == 8:
                self.IsSide = True

            if index == 1:
                self.RowOpposite = 3
                self.ColumnOpposite = 7
                self.DiagonalOpposite = 9
            elif index == 2:
                self.ColumnOpposite = 8
            elif index == 3:
                self.RowOpposite = 1
                self.ColumnOpposite = 9
                self.DiagonalOpposite = 7
            elif index == 4:
                self.RowOpposite = 6
            elif index == 6:
                self.RowOpposite = 4
            elif index == 7:
                self.RowOpposite = 9
                self.ColumnOpposite = 1
                self.DiagonalOpposite = 3
            elif index == 8:
                self.ColumnOpposite = 2
            else:  # index == 9
                self.RowOpposite = 7
                self.ColumnOpposite = 3
                self.DiagonalOpposite = 1

        if index == 1 or self.DiagonalOpposite == 1 or self.IsCenter:
            self.Diagonals.append([1, 5, 9])
        if index == 3 or self.DiagonalOpposite == 3 or self.IsCenter:
            self.Diagonals.append([7, 5, 3])


class Rule:
    def __init__(self, descriptionPrefix, expectedContent=None, count=None):
        self.DescriptionPrefix = descriptionPrefix
        self.ExpectedContent = expectedContent
        self.Count = count

    def __str__(self):
        result = self.DescriptionPrefix + " "
        if self.Count is not None:
            result += str(self.Count) + " "
        if self.ExpectedContent is not None:
            result += self.ExpectedContent + " "
        return result


class RuleMetadata:
    def __init__(self, create, options=None, needsSpecificContent=True,
                 needsSpecificCount=True):
        if options is None:
            needsSpecificContent = False
            needsSpecificCount = False
        if needsSpecificCount and not needsSpecificContent:
            raise ValueError('needsSpecificCount is only valid if needsSpecificContent is true')
        self.create = create
        self.options = options
        self.needsSpecificContent = needsSpecificContent
        self.needsSpecificCount = needsSpecificCount

    def create_rules(self):
        option = None
        count = None

        seen = set()
        if self.needsSpecificContent:
            rules = list()

            for optionInfo in self.options:
                option = optionInfo[0]
                if self.needsSpecificCount:
                    optionCounts = optionInfo[1]

                    for count in optionCounts:
                        gene = self.create(option, count)
                        if str(gene) not in seen:
                            seen.add(str(gene))
                            rules.append(gene)
                else:
                    gene = self.create(option, None)
                    if str(gene) not in seen:
                        seen.add(str(gene))
                        rules.append(gene)
            return rules
        else:
            return [self.create(option, count)]


class ContentFilter(Rule):
    def __init__(self, description, expectedContent, expectedCount,
                 getValueFromSquare):
        super().__init__(description, expectedContent, expectedCount)
        self.getValueFromSquare = getValueFromSquare

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            m = list(map(lambda i: board[i].Content,
                         self.getValueFromSquare(square)))
            if m.count(self.ExpectedContent) == self.Count:
                result.add(square.Index)
        return result


class RowContentFilter(ContentFilter):
    def __init__(self, expectedContent, expectedCount):
        super().__init__("its ROW has", expectedContent, expectedCount,
                         lambda s: s.Row)


class ColumnContentFilter(ContentFilter):
    def __init__(self, expectedContent, expectedCount):
        super().__init__("its COLUMN has", expectedContent, expectedCount,
                         lambda s: s.Column)


class LocationFilter(Rule):
    def __init__(self, expectedLocation, containerDescription, func):
        super().__init__(
            "is in " + expectedLocation + " " + containerDescription)
        self.func = func

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if self.func(square):
                result.add(square.Index)
        return result


class RowLocationFilter(LocationFilter):
    def __init__(self, expectedLocation, func):
        super().__init__(expectedLocation, "ROW", func)


class ColumnLocationFilter(LocationFilter):
    def __init__(self, expectedLocation, func):
        super().__init__(expectedLocation, "COLUMN", func)


class TopRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("TOP", lambda square: square.IsTopRow)


class MiddleRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("MIDDLE", lambda square: square.IsMiddleRow)


class BottomRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("BOTTOM", lambda square: square.IsBottomRow)


class LeftColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("LEFT", lambda square: square.IsLeftColumn)


class MiddleColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("MIDDLE", lambda square: square.IsMiddleColumn)


class RightColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("RIGHT", lambda square: square.IsRightColumn)


class DiagonalLocationFilter(LocationFilter):
    def __init__(self):
        super().__init__("DIAGONAL", "",
                         lambda square: not (square.IsMiddleRow or
                                             square.IsMiddleColumn) or
                                        square.IsCenter)


class DiagonalContentFilter(Rule):
    def __init__(self, expectedContent, count):
        super().__init__("its DIAGONAL has", expectedContent, count)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            for diagonal in square.Diagonals:
                m = list(map(lambda i: board[i].Content, diagonal))
                if m.count(self.ExpectedContent) == self.Count:
                    result.add(square.Index)
                    break
        return result


class WinFilter(Rule):
    def __init__(self, content):
        super().__init__("WIN" if content == ContentType
                         .Mine else "block OPPONENT WIN")
        self.rowRule = RowContentFilter(content, 2)
        self.columnRule = ColumnContentFilter(content, 2)
        self.diagonalRule = DiagonalContentFilter(content, 2)

    def get_matches(self, board, squares):
        inDiagonal = self.diagonalRule.get_matches(board, squares)
        if len(inDiagonal) > 0:
            return inDiagonal
        inRow = self.rowRule.get_matches(board, squares)
        if len(inRow) > 0:
            return inRow
        inColumn = self.columnRule.get_matches(board, squares)
        return inColumn


class DiagonalOppositeFilter(Rule):
    def __init__(self, expectedContent):
        super().__init__("DIAGONAL-OPPOSITE is", expectedContent)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.DiagonalOpposite is None:
                continue
            if board[square.DiagonalOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class RowOppositeFilter(Rule):
    def __init__(self, expectedContent):
        super().__init__("ROW-OPPOSITE is", expectedContent)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.RowOpposite is None:
                continue
            if board[square.RowOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class ColumnOppositeFilter(Rule):
    def __init__(self, expectedContent):
        super().__init__("COLUMN-OPPOSITE is", expectedContent)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.ColumnOpposite is None:
                continue
            if board[square.ColumnOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class CenterFilter(Rule):
    def __init__(self):
        super().__init__("is in CENTER")

    @staticmethod
    def get_matches(board, squares):
        result = set()
        for square in squares:
            if square.IsCenter:
                result.add(square.Index)
        return result


class CornerFilter(Rule):
    def __init__(self):
        super().__init__("is a CORNER")

    @staticmethod
    def get_matches(board, squares):
        result = set()
        for square in squares:
            if square.IsCorner:
                result.add(square.Index)
        return result


class SideFilter(Rule):
    def __init__(self):
        super().__init__("is SIDE")

    @staticmethod
    def get_matches(board, squares):
        result = set()
        for square in squares:
            if square.IsSide:
                result.add(square.Index)
        return result


iHaveThreeInRow = RowContentFilter(ContentType.Mine, 3)
iHaveThreeInColumn = ColumnContentFilter(ContentType.Mine, 3)
iHaveThreeInDiagonal = DiagonalContentFilter(ContentType.Mine, 3)
opponentHasTwoInARow = WinFilter(ContentType.Opponent)


class Fitness:
    def __init__(self, wins, ties, losses, geneCount):
        self.Wins = wins
        self.Ties = ties
        self.Losses = losses
        totalGames = wins + ties + losses
        percentWins = 100 * round(wins / totalGames, 3)
        percentLosses = 100 * round(losses / totalGames, 3)
        percentTies = 100 * round(ties / totalGames, 3)
        self.PercentTies = percentTies
        self.PercentWins = percentWins
        self.PercentLosses = percentLosses
        self.GeneCount = geneCount

    def __gt__(self, other):
        if self.PercentLosses != other.PercentLosses:
            return self.PercentLosses < other.PercentLosses

        if self.Losses > 0:
            return False

        if self.Ties != other.Ties:
            return self.Ties < other.Ties
        return self.GeneCount < other.GeneCount

    def __str__(self):
        return "{:.1f}% Losses ({}), {:.1f}% Ties ({}), {:.1f}% Wins ({}), {} rules".format(
            self.PercentLosses,
            self.Losses,
            self.PercentTies,
            self.Ties,
            self.PercentWins,
            self.Wins,
            self.GeneCount)


if __name__ == '__main__':
    unittest.main()
