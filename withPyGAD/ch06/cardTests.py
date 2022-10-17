import pygad
import functools
import operator
import numpy


def fitness_func(genes, solution_idx):
    group1Sum = sum(genes[0:5])
    group2Product = functools.reduce(operator.mul, genes[5:10])
    duplicateCount = (len(genes) - len(set(genes)))
    return 1 / ((abs(36 - group1Sum) + abs(360 - group2Product)) + 1) - duplicateCount


geneset = numpy.array([[i + 1 for i in range(10)], [i + 1 for i in range(10)]])


ga_instance = pygad.GA(num_generations=50,
                       num_parents_mating=1,
                       sol_per_pop=50,
                       fitness_func=fitness_func,
                       initial_population=None,
                       num_genes=10,
                       gene_type=int,
                       init_range_low=1,
                       init_range_high=10,
                       parent_selection_type="rank",
                       keep_parents=-1,
                       crossover_type=None,
                       mutation_type="swap",
                       mutation_percent_genes=40,
                       gene_space=[i + 1 for i in range(10)],
                       allow_duplicate_genes=False,
                       stop_criteria="reach_1")

ga_instance.run()


solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(
    solution_fitness=solution_fitness))
print("Solution index of best solution = {solution_idx}".format(
    solution_idx=solution_idx))
