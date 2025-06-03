"""
gpp_ts.py: Construction and tabu search for graph partitioning.

The Graph Partioning Problem (GPP) is a combinatorial optimization
problem where: given a graph with an even number of nodes, find a
partition into half of the nodes that minimizes the number of edges
crossing it to the other partition.

This file contains a set of functions to illustrate:
  - construction heuristics
  - tabu search

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""


LOG = False     # whether or not to print intermediate solutions
import random
Infinity = 1.e10000

def construct(nodes):
    """A simple construction method.

    The solution is represented by a vector:
      - sol[i]=0  -  node i is in partition 0
      - sol[i]=1  -  node i is in partition 1
    """
    indices = list(nodes)
    random.shuffle(indices)
    sol = [0 for i in nodes]
    for i in range(len(nodes)//2):
        sol[indices[i]] = 1
    return sol


def evaluate(nodes, adj, sol):
    """Evaluate a solution.

    Determines:
      - the cost of a solution, i.e., the number of edges going
        from one partition to the other;
      - s[i] - number of edges adjacent to i in the same partition;
      - d[i] - number of edges adjacent to i in a different partition.
    """
    assert sum(sol) == len(nodes)//2
    cost = 0
    s = [0 for i in nodes]
    d = [0 for i in nodes]

    for i in nodes:
        for j in adj[i]:
            if sol[i] == sol[j]:
                s[i] += 1
            else:
                d[i] += 1
    for i in nodes:
        cost += d[i]
    return cost/2, s, d


def find_move_rnd(part, nodes, adj, sol, s, d, tabu, tabulen, iteration):
    """Probabilistically find the best non-tabu move into partition type 'part'."""
    mindelta = Infinity
    istar = None
    cand = []
    for i in nodes:
        if sol[i] != part:      # check if making sol[i] = part improves solution
            # if tabu[i] <= iteration:
            if random.random() > float(tabu[i] - iteration)/tabulen:
                delta = s[i] - d[i]
                if delta < mindelta:
                    mindelta = delta
                    istar = i
                    cand = [(i,delta)]
                elif delta == mindelta:
                    cand.append((i,delta))
    if cand != []:
        return random.choice(cand)

    # there are no non-tabu moves, clear tabu list
    print( "blocked, no non-tabu move")
    tabu = [0 for i in nodes]
    return find_move_rnd(part, nodes, adj, sol, s, d, tabu, tabulen, iteration)
    

def find_move(part, nodes, adj, sol, s, d, tabu, tabulen, iteration):
    """Find the best non-tabu move into partition type 'part'."""
    mindelta = Infinity
    istar = None
    for i in nodes:
        if sol[i] != part:      # check if making sol[i] = part improves solution
            if tabu[i] <= iteration:
                delta = s[i] - d[i]
                if delta < mindelta:
                    mindelta = delta
                    istar = i
    if istar != None:
        return istar, mindelta
    
    print( "blocked, no non-tabu move")
    tabu = [0 for i in nodes]
    return find_move(part, nodes, adj, sol, s, d, tabu, tabulen, iteration)
    

def move(part, nodes, adj, sol, s, d, tabu, tabulen, iteration):
    """Determine and execute the best non-tabu move."""

    # find the best move
    # i, delta = find_move(part, nodes, adj, sol, s, d, tabu, tabulen, iteration)
    i, delta = find_move_rnd(part, nodes, adj, sol, s, d, tabu, tabulen, iteration)
    sol[i] = part
    tabu[i] = iteration + tabulen
    # tabu[i] = iteration + randint(1,tabulen) # another possibility

    # update cost structure for node i
    s[i],d[i] = d[i],s[i]       # i swaped partitions, so swap s and d
    for j in adj[i]:
        if sol[j] != part:
            s[j] -= 1
            d[j] += 1
        else:
            s[j] += 1
            d[j] -= 1
    return delta

        
def tabu_search(nodes, adj, sol, max_iter, tabulen, report = None):
    """Execute a tabu search run."""
    assert len(nodes)%2 == 0    # graph partitioning is only for graphs with an even number of nodes
    cost, s, d = evaluate(nodes, adj, sol)
    tabu = [0 for i in nodes]   # iteration up to which node 'i' is tabu

    bestcost = Infinity
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
            
    if report:
        report(bestcost, "it:%d"%it)

    # # check correctness of incremental evaluation
    # z,s,d = evaluate(nodes, adj, bestsol)
    # assert z == bestcost
    
    return bestsol, bestcost



