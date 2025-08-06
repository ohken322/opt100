import bisect
import random
Infinity = 1.e10000
LOG = True

from gcp_ts import rsatur, evaluate, tabu_search

#
# functions related to the genetic algorithm
#

def gcp_ga(nodes, adj, K, ngen, nelem, TABULEN, TABUITER, report=None):
    """Evolve a Genetic Algorithm, with crossover and mutation based on Hao 1999.

    A population of 'nelem' elements is evolved for 'ngen' generations.
    The number of colores allowed is fixed to 'K'.  This function will search
    a coloring such that the number of conflicts (adjacent nodes with the same
    color) is minimum.  If a solution with no conflicts is found, it is
    returned immediately.

    Parameters:
     * K - number of colors
     * ngen - number of generations
     * nelem - number of elements to keep in population
     * TABUITER - number of tabu search iterations to do on each newly created solution
     * report - function to call to log best found solutions

    Returns the best solution found and its number of conflicts.
    """

    # Implement selection based on rank.
    # Probabilities are inversely proportional to the rank:
    # p_i = (n-i)/(n*(n+1)/2)   i=0,1,...,n-1
    p = [(nelem-i)/(nelem*(nelem+1.)/2) for i in range(nelem)]
    psum = [sum(p[0:i+1]) for i in range(nelem)]
    def select():
        r = random.random()
        for i in range(len(psum)):
            if psum[i]>r:
                return i
        return len(psum)

    # initialize population
    sols = []   # sols[i] -> element i of population, a tuple (obj,sol)
    i = 0
    while i < nelem:
        newsol = rsatur(nodes, adj, K)  # solution construction
        obj = evaluate(nodes, adj, newsol)   # do not improve initial solution
        # obj = local_search(nodes, adj, K, newsol, TABUITER)
        # !!!!! newsol,obj = tabu_search(nodes, adj, K, newsol, TABULEN, TABUITER)

        # if LOG:
        #     print(sol(i,K,obj,newsol))
        if (obj, newsol) not in sols:
            sols.append((obj,newsol))
            i += 1
        elif LOG:
            print( "solution was already in pool, skiping")
    sols.sort() # key for sorting is obj (the first element of each tuple)

    # best found solution:
    best_obj = sols[0][0]       # sol[0] is the solution with lowest obj
    best_sol = list(sols[0][1])
    if best_obj == 0:   # feasible solution for K colors found
        return best_sol, best_obj
    if report:
        report(best_obj, "\t%d colors\tgeneration:%d" % (K,0))

    # start evolution
    for g in range(ngen):
        # if LOG:
        #     # print population on some generations
        #     if not g%10:
        #         print()
        #         print( "GENERATION", g, "\t (%d colors)" % K)
        #         for i in range(len(sols)):
        #             print(sol(i,K,sols[i][0],sols[i][1]))

        # solution recombination
        p1 = select()        # select parents
        p2 = select()
        sol1 = sols[p1][1]   # extract solution list
        sol2 = sols[p2][1]
        newsol = crossover(nodes,sol1,sol2,K)  # recombination
        if LOG:
            print()
            print( 'xover of ', p1, 'and', p2, '\t-->', newsol)

        # mutation:
        # obj = local_search(nodes, adj, K, newsol, TABUITER)      # mutation
        # !!!!! newsol,obj = tabu_search(nodes, adj, K, newsol, TABULEN, TABUITER)
        newsol,obj = tabu_search(nodes, adj, K, newsol, TABULEN, g+1)
        if LOG:
            print( 'mutate (tabu search) \t--> %s (obj=%d)' % (newsol, obj))

        # update best found solution
        if obj < best_obj:
            best_obj = obj
            best_sol = list(newsol)
            if report:
                report(best_obj, "\t%d colors\tgeneration:%d" % (K,g))
            if obj == 0:       # feasible solution for K colors found
                return best_sol, best_obj

        # if solution is not in population, and is better than the worst element, insert it
        if (obj, newsol) in sols:
            if LOG:
                print( "solution already exists in population")
            continue
        
        if (obj < sols[-1][0] or len(sols) < nelem):
            bisect.insort(sols,(obj,newsol))
        while len(sols) > nelem:
            sols.pop(-1)        # remove worst element

    # report final solution
    if report:
        report(best_obj, "\t%d colors\tgeneration:%d" % (K,ngen))

    # if LOG:
    #     print( "final solutions:")
    #     for i in range(len(sols)):
    #         print(sol(i,K,sols[i][0],sols[i][1]))
    #     print()

    return best_sol, best_obj


def crossover(nodes,s1,s2,K):
    """Create a solution based on 's1' and 's2', according to Hao 1999.

    
    """
    # count number of nodes colored with each color in the incoming solutions
    n1 = [s1.count(k) for k in range(K)]
    n2 = [s2.count(k) for k in range(K)]

    new = [None for i in nodes]         # solution to be created with crossover
    for l in range(K):
        if l % 2:
            src, n = s1, n1       # odd  color, select source from parent 1
        else:
            src, n = s2, n2       # even color, select source from parent 2

        # determine color appearing in most nodes of the selected candidate
        nmax = -1
        for k in range(K):
            if n[k] > nmax:
                kmax = k        # color on most nodes
                nmax = n[k]     # number of nodes colored with it
        if nmax <= 0:   # no candidates, all colors already assigned
            break

        # color nodes whose color in the parent is kmax 
        for i in nodes:
            if src[i] == kmax and new[i] == None:
                new[i] = kmax

            # update candidate's information:
            # decrease counters for each node with color kmax
            if s1[i] == kmax:
                n1[kmax] -= 1
            if s2[i] == kmax:
                n2[kmax] -= 1

    # for nodes with no color attributed, choose a random color
    for i in nodes:
        if new[i] == None:
            new[i] = random.randint(0,K-1)
                
    return new


# def printsol(i,K,obj,sol):
#     """Nicely print solution"""
#     print "element", i, "\tobj=", obj, "(%d colors)" % K, 
#     if len(nodes) <= 30:
#         print sol
#     else:
#         print sol[:30], "..."
