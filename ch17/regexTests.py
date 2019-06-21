# File: regexTests.py
#    from chapter 17 of _Genetic Algorithms with Python_
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
import re
import unittest
from functools import partial

import genetic

repeatMetas = {'?', '*', '+', '{2}', '{2,}'}
startMetas = {'|', '(', '['}
endMetas = {')', ']'}
allMetas = repeatMetas | startMetas | endMetas

regexErrorsSeen = {}


def repair_regex(genes):
    result = []
    finals = []
    f = repair_ignore_repeat_metas
    for token in genes:
        f = f(token, result, finals)
    if ']' in finals and result[-1] == '[':
        del result[-1]
    result.extend(reversed(finals))
    return ''.join(result)


def repair_ignore_repeat_metas(token, result, finals):
    if token in repeatMetas or token in endMetas:
        return repair_ignore_repeat_metas
    if token == '(':
        finals.append(')')
    result.append(token)
    if token == '[':
        finals.append(']')
        return repair_in_character_set
    return repair_ignore_repeat_metas_following_repeat_or_start_metas


def repair_ignore_repeat_metas_following_repeat_or_start_metas(token,
                                                               result,
                                                               finals):
    last = result[-1]
    if token not in repeatMetas:
        if token == '[':
            result.append(token)
            finals.append(']')
            return repair_in_character_set
        if token == '(':
            finals.append(')')
        elif token == ')':
            match = ''.join(finals).rfind(')')
            if match != -1:
                del finals[match]
            else:
                result[0:0] = ['(']
        result.append(token)
    elif last in startMetas:
        pass
    elif token == '?' and last == '?' and len(result) > 2 and \
                    result[-2] in repeatMetas:
        pass
    elif last in repeatMetas:
        pass
    else:
        result.append(token)
    return repair_ignore_repeat_metas_following_repeat_or_start_metas


def repair_in_character_set(token, result, finals):
    if token == ']':
        if result[-1] == '[':
            del result[-1]
        result.append(token)
        match = ''.join(finals).rfind(']')
        if match != -1:
            del finals[match]
        return repair_ignore_repeat_metas_following_repeat_or_start_metas
    elif token == '[':
        pass
    elif token == '|' and result[-1] == '|':
        pass  # suppresses FutureWarning about ||
    else:
        result.append(token)
    return repair_in_character_set


def get_fitness(genes, wanted, unwanted):
    pattern = repair_regex(genes)
    length = len(pattern)

    try:
        re.compile(pattern)
    except re.error as e:
        key = str(e)
        key = key[:key.index("at position")]
        info = [str(e),
                "genes = ['{}']".format("', '".join(genes)),
                "regex: " + pattern]
        if key not in regexErrorsSeen or len(info[1]) < len(
                regexErrorsSeen[key][1]):
            regexErrorsSeen[key] = info
        return Fitness(0, len(wanted), len(unwanted), length)

    numWantedMatched = sum(1 for i in wanted if re.fullmatch(pattern, i))
    numUnwantedMatched = sum(1 for i in unwanted if re.fullmatch(pattern, i))
    return Fitness(numWantedMatched, len(wanted), numUnwantedMatched,
                   length)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t{}\t{}".format(
        repair_regex(candidate.Genes), candidate.Fitness, timeDiff))


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


def mutate_swap(genes):
    if len(genes) < 2:
        return False
    indexA, indexB = random.sample(range(len(genes)), 2)
    genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
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


def mutate_to_character_set(genes):
    if len(genes) < 3:
        return False
    ors = [i for i in range(1, len(genes) - 1)
           if genes[i] == '|' and
           genes[i - 1] not in allMetas and
           genes[i + 1] not in allMetas]
    if len(ors) == 0:
        return False
    shorter = [i for i in ors
               if sum(len(w) for w in genes[i - 1:i + 2:2]) >
               len(set(c for w in genes[i - 1:i + 2:2] for c in w))]
    if len(shorter) == 0:
        return False
    index = random.choice(ors)
    distinct = set(c for w in genes[index - 1:index + 2:2] for c in w)
    sequence = ['['] + [i for i in distinct] + [']']
    genes[index - 1:index + 2] = sequence
    return True


def mutate_to_character_set_left(genes, wanted):
    if len(genes) < 4:
        return False
    ors = [i for i in range(-1, len(genes) - 3)
           if (i == -1 or genes[i] in startMetas) and
           len(genes[i + 1]) == 2 and
           genes[i + 1] in wanted and
           (len(genes) == i + 1 or genes[i + 2] == '|' or
            genes[i + 2] in endMetas)]
    if len(ors) == 0:
        return False
    lookup = {}
    for i in ors:
        lookup.setdefault(genes[i + 1][0], []).append(i)
    min2 = [i for i in lookup.values() if len(i) > 1]
    if len(min2) == 0:
        return False
    choice = random.choice(min2)
    characterSet = ['|', genes[choice[0] + 1][0], '[']
    characterSet.extend([genes[i + 1][1] for i in choice])
    characterSet.append(']')
    for i in reversed(choice):
        if i >= 0:
            genes[i:i + 2] = []
    genes.extend(characterSet)
    return True


def mutate_add_wanted(genes, wanted):
    index = random.randrange(0, len(genes) + 1) if len(genes) > 0 else 0
    genes[index:index] = ['|'] + [random.choice(wanted)]
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


class RegexTests(unittest.TestCase):
    def test_two_digits(self):
        wanted = {"01", "11", "10"}
        unwanted = {"00", ""}
        self.find_regex(wanted, unwanted, 7)

    def test_grouping(self):
        wanted = {"01", "0101", "010101"}
        unwanted = {"0011", ""}
        self.find_regex(wanted, unwanted, 5)

    def test_state_codes(self):
        Fitness.UseRegexLength = True
        wanted = {"NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND"}
        unwanted = {"N" + l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    if "N" + l not in wanted}
        customOperators = [
            partial(mutate_to_character_set_left, wanted=wanted),
        ]
        self.find_regex(wanted, unwanted, 11, customOperators)

    def test_even_length(self):
        wanted = {"00", "01", "10", "11", "0000", "0001", "0010", "0011",
                  "0100", "0101", "0110", "0111", "1000", "1001", "1010",
                  "1011", "1100", "1101", "1110", "1111"}
        unwanted = {"0", "1", "000", "001", "010", "011", "100", "101",
                    "110", "111", ""}
        customOperators = [
            mutate_to_character_set,
        ]
        self.find_regex(wanted, unwanted, 10, customOperators)

    def test_50_state_codes(self):
        Fitness.UseRegexLength = True
        wanted = {"AL", "AK", "AZ", "AR", "CA",
                  "CO", "CT", "DE", "FL", "GA",
                  "HI", "ID", "IL", "IN", "IA",
                  "KS", "KY", "LA", "ME", "MD",
                  "MA", "MI", "MN", "MS", "MO",
                  "MT", "NE", "NV", "NH", "NJ",
                  "NM", "NY", "NC", "ND", "OH",
                  "OK", "OR", "PA", "RI", "SC",
                  "SD", "TN", "TX", "UT", "VT",
                  "VA", "WA", "WV", "WI", "WY"}
        unwanted = {a + b for a in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    for b in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    if a + b not in wanted} | \
                   set(i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        customOperators = [
            partial(mutate_to_character_set_left, wanted=wanted),
            mutate_to_character_set,
            partial(mutate_add_wanted, wanted=[i for i in wanted]),
        ]
        self.find_regex(wanted, unwanted, 120, customOperators)

    def find_regex(self, wanted, unwanted, expectedLength,
                   customOperators=None):
        startTime = datetime.datetime.now()
        textGenes = wanted | set(c for w in wanted for c in w)
        fullGeneset = [i for i in allMetas | textGenes]

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, wanted, unwanted)

        mutationRoundCounts = [1]

        mutationOperators = [
            partial(mutate_add, geneset=fullGeneset),
            partial(mutate_replace, geneset=fullGeneset),
            mutate_remove,
            mutate_swap,
            mutate_move,
        ]
        if customOperators is not None:
            mutationOperators.extend(customOperators)

        def fnMutate(genes):
            mutate(genes, fnGetFitness, mutationOperators,
                   mutationRoundCounts)

        optimalFitness = Fitness(len(wanted), len(wanted), 0,
                                 expectedLength)

        best = genetic.get_best(fnGetFitness,
                                max(len(i) for i in textGenes),
                                optimalFitness, fullGeneset, fnDisplay, 
                                fnMutate, poolSize=10)
        self.assertTrue(not optimalFitness > best.Fitness)

        for info in regexErrorsSeen.values():
            print("")
            print(info[0])
            print(info[1])
            print(info[2])

    def test_benchmark(self):
        genetic.Benchmark.run(self.test_two_digits)


class Fitness:
    UseRegexLength = False

    def __init__(self, numWantedMatched, totalWanted, numUnwantedMatched,
                 length):
        self.NumWantedMatched = numWantedMatched
        self._totalWanted = totalWanted
        self.NumUnwantedMatched = numUnwantedMatched
        self.Length = length

    def __gt__(self, other):
        combined = (self._totalWanted - self.NumWantedMatched) \
                   + self.NumUnwantedMatched
        otherCombined = (other._totalWanted - other.NumWantedMatched) \
                        + other.NumUnwantedMatched
        if combined != otherCombined:
            return combined < otherCombined
        success = combined == 0
        otherSuccess = otherCombined == 0
        if success != otherSuccess:
            return success
        if not success:
            return self.Length <= other.Length if Fitness.UseRegexLength else False
        return self.Length < other.Length

    def __str__(self):
        return "matches: {} wanted, {} unwanted, len {}".format(
            "all" if self._totalWanted == self.NumWantedMatched else self.NumWantedMatched,
            self.NumUnwantedMatched,
            self.Length)


if __name__ == '__main__':
    unittest.main()
