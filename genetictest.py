#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from pyevolve.G1DList import G1DList
from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Mutators


def sortedness(chromosome):
    # fitness is based on "sortedness"
    prev = 0
    streak = 0
    max_streak = 0

    for v in chromosome:
        if v < prev:
            max_streak = max(max_streak, streak)
            streak = 0
        else:
            streak += 1

        prev = v

    return max_streak


def initializer_shuffled(genome, **args):
    l = range(genome.getListSize())
    random.shuffle(l)
    genome.setInternalList(l)


if __name__ == '__main__':
    list_length = 20
    genome = G1DList(list_length)
    genome.evaluator.set(sortedness)
    genome.initializator.set(initializer_shuffled)
    genome.mutator.set(Mutators.G1DListMutatorSwap)
    genome.crossover.clear()

    ga = GSimpleGA(genome)

    ga.setGenerations(100000)
    ga.evolve(freq_stats=1000)
    ga.setMultiProcessing()
    print ga.bestIndividual()
