"""
gpp_ts_intdiv.py: Construction and tabu search for graph partitioning.

The Graph Partioning Problem (GPP) is a combinatorial optimization
problem where: given a graph with an even number of nodes, find a
partition into half of the nodes that minimizes the number of edges
crossing it to the other partition.

This file contains a set of functions to illustrate:
  - diversification/intensification
  - div/intens tabu search

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

LOG = False     # whether or not to print intermediate solutions
import random

Infinity = 1.e10000

from gpp_ts import *

def diversify(sol, nodes):
    """Diversify: keep a part of the solution with random size.

    The solution is represented by a vector:
      - sol[i]=0  -  node i is in partition 0
      - sol[i]=1  -  node i is in partition 1
    """
    ind1 = [i for i in nodes if sol[i] == 1]
    ind0 = [i for i in nodes if sol[i] == 0]
    random.shuffle(ind1)
    random.shuffle(ind0)

    n = len(sol)//2
    start = int(random.random()*n)
    for i in range(start,n):
        bit = int(random.random() + .5)
        sol[ind0[i]] = bit
        sol[ind1[i]] = 1-bit


def ts_intens_divers(nodes, adj, sol, max_iter, tabulen, report):
    """Execute a tabu search run, with intensification/diversification."""
    assert len(nodes)%2 == 0    # graph partitioning is only for graphs with an even number of nodes
    cost, s, d = evaluate(nodes, adj, sol)
    tabu = [0 for i in nodes]

    bestcost = Infinity
    lastcost = Infinity
    D = 1
    count = 0
    for it in range(max_iter):
        if LOG:
            print( "tabu search, iteration", it)
            print( "initial sol:     ", sol)
        cost += move(1, nodes, adj, sol, s, d, tabu, tabulen, it)
        if LOG:
            print( "intermediate sol:", sol)
        cost += move(0, nodes, adj, sol, s, d, tabu, tabulen, it)
        if LOG:
            print( "completed sol:   ", sol)

        if cost < bestcost:
            bestcost = cost
            bestsol = list(sol)
            if report:
                report(bestcost, "it:%d"%it)
            if LOG:
                print( "*** intensifying ***")
            tabu = [0 for i in nodes]
            count = 0
        elif cost < lastcost:
            count = 0
        else:
            count += 1

        if count > D:
            count = 0
            if LOG:
                print( "*** diversifying ***")
            tabu = [0 for i in nodes]
            sol = list(bestsol)
            diversify(sol, nodes)
            cost, s, d = evaluate(nodes, adj, sol)
            D += 1
        if LOG:
            print( count, D, "iteration", it, "cost", cost, "/ best:", bestcost )
        lastcost = cost
    return bestsol, bestcost



