import random
Infinity = 1.e10000
LOG = False


#
# general-purpose, utility functions
#

def evaluate(nodes, adj, color):
    """Evaluate the number of conflicts of solution 'color'."""
    total = 0
    for i in nodes:
        for j in adj[i]:
            if color[i] == color[j]:
                total += 1
    return total


def calc_bad_degree(nodes, adj, color, K):
    """Calculate the number of conflicts for each node switching to each color.

    Returns two structures:
      * dictionary 'bad_degree[i,k]', which contains the conflicts
        that will be obtained if node 'i' switches to color k
      * list 'best_color', holding, for each node, index 'k' of color that will
        produce the minimum of conflicts is assigned to the node.
    """
    n = len(nodes)
    bad_degree = {}
    for i in nodes:
        for k in range(K):
            bad_degree[i,k] = 0

    # calculate bad degree for each node
    for i in nodes:
        for j in adj[i]:
            kj = color[j]
            bad_degree[i,kj] += 1

    # calculate the best color for each node, on the current setting
    best_color = [None for i in nodes]
    for i in nodes:
        min_bd = Infinity
        for k in range(K):
            if color[i] != k and bad_degree[i,k] < min_bd:
                min_bd = bad_degree[i,k]
                best_color[i] = k
    
    return bad_degree, best_color

#
# functions related to tabu-search
#

def tabu_search(nodes, adj, K, color, tabulen, max_iter, report = None):
    """Execute a tabu search for Graph Coloring starting from solution 'color'.

    The number of colores allowed is fixed to 'K'.  This function will search
    a coloring such that the number of conflicts (adjacent nodes with the same
    color) is minimum.  If a solution with no conflicts is found, it is
    returned immediately.
    
    Parameters:
     * nodes, adj - graph definition
     * K - number of colors allowed
     * colors - initial solution
     * tabulen - lenght of the tabu status
     * max_iter - allowed number of iterations
     * report - function used for output of best found solutions

    Returns the best solution found and its number of conflicts.
    """
    tabu = {}
    for i in nodes:
        for k in range(K):
            tabu[i,k] = 0

    best_sol = list(color)
    sum_bad_degree = evaluate(nodes, adj, color)
    bad_degree,best_color = calc_bad_degree(nodes,adj,color,K)
    best_obj = sum_bad_degree

    for it in range(max_iter):
        try:
            i_star, delta = find_move(nodes, adj, K, color, bad_degree, best_color)
        except UnboundLocalError:            # search blocked
            if report:
                print( "search blocked, returning")
            return best_sol, best_obj

        move(nodes, adj, K, color, bad_degree, best_color, i_star, it, tabu, tabulen)
        sum_bad_degree += delta

        if LOG:
            print( "color:", color)
            print( "iteration", it+1, "\tsum_bad_degree:", sum_bad_degree)
            print()

        if sum_bad_degree < best_obj:	# update best found solution
            best_obj = sum_bad_degree
            best_sol = list(color)
            if report:
                report(best_obj, "\t%d colors\titer:%d" % (K,it))
        if sum_bad_degree == 0:
            break       # found a feasible solution for this K, no need to continue
    
    # report final solution
    if report:
        report(best_obj, "\t%d colors\titer:%d" % (K,it))
    assert best_obj == evaluate(nodes, adj, best_sol)
    return best_sol, best_obj


def find_move(nodes, adj, K, color, bad_degree, best_color):
    """Find a non-tabu color exchange in a node on solution 'color'.

    Tabu information is implicit in 'best_color': tabu indices are
    have value 'None'.  The non-tabu neigbor solution (node and respective
    color) with largest improvement on the 'bad_degree' is selected.

    Returns the chosen node (color is implicit in 'best_color'), and the
    improvement on bad degree to which the movement leads.
    """
    min_bd = Infinity
    n = len(nodes)
    init = random.randint(0,n)

    for i_ in nodes:
        i = (i_ + init) %  n    # randomize initial search position
        ki = color[i]
        kb = best_color[i]
        if bad_degree[i,ki] > 0 and kb != None: # search only nodes with bad degree > 0
            delta = bad_degree[i,kb] - bad_degree[i,ki]
            if delta < min_bd:
                min_bd = delta
                i_star = i
            # if delta < 0:     # use this for first-improve
            #     return i_star, 2*min_bd

    # raises exception if search is blocked (as i_star is not instantiated)
    return i_star, 2*min_bd


def move(nodes, adj, K, color, bad_degree, best_color, i_star, it, tabu, tabulen):
    """Execute a movement on solution 'color', and update the tabu information.

    Node 'i_star' is changed from its previous color to its 'best_color'.
    """
    old_color = color[i_star]
    new_color = best_color[i_star]

    # update bad_degree table
    for j in adj[i_star]:
        bad_degree[j,old_color] -= 1
        bad_degree[j,new_color] += 1

    # do the move
    color[i_star] = new_color
    if LOG:
        print( 'color[%d]  %d --> %d' % (i_star, old_color, color[i_star]) )

    # update tabu list
    tabu[i_star, old_color] = it + int(tabulen * random.random()) + 1

    # update best color for i_star and each node adjacent
    changed = list(adj[i_star])
    changed.append(i_star)
    for j in changed:
        min_bd = Infinity
        kj = color[j]
        best_color[j] = None
        for k in range(K):
            if bad_degree[j,k] == 0:    # aspiration criterion
                best_color[j] = k
                break
            if kj != k and tabu[j,k] < it:
                if bad_degree[j,k] < min_bd:
                    min_bd = bad_degree[j,k]
                    best_color[j] = k
                # if min_bd == 0:       # not necessary with aspiration
                #     break
    

#
# construction methods
#

def rsatur(nodes, adj, K):
    """Saturation algorithm adapted to produce K classes.

    Dynamically choose the vertex to color next, selecting one that is
    adjacent to the largest number of distinctly colored vertices.
    If a non-conflicting color cannot be found, randomly choose a color
    from the K classes.    
    Returns the solution constructed.
    """
    unc_adj = [set(adj[i]) for i in nodes]      # currently uncolored adjacent nodes
    adj_colors = [set([]) for i in nodes]       # colors adjacent to each vertex
    color = [None for i in nodes]       # solution vector

    U = set(nodes)
    while U:
        # choose vertex with maximum saturation degree
        max_colors = -1
        for i in U:
            n = len(adj_colors[i])
            if n > max_colors:
                max_colors = n
                max_uncolored = -1
            # break ties: get index of node with maximal degree on uncolored nodes
            if n == max_colors:
                adj_uncolored = len(unc_adj[i])
                if adj_uncolored > max_uncolored:
                    u_star = i
                    max_uncolored = adj_uncolored

        # find a color for node 'u-star'
        colors = range(K)
        random.shuffle(colors)
        for k in colors:
            if k not in adj_colors[u_star]:
                k_star = k
                break
        else:   # must use a conflicting color
            k_star = random.randint(0,K-1)
        color[u_star] = k_star
        for i in unc_adj[u_star]:
            unc_adj[i].remove(u_star)
            adj_colors[i].add(k_star)

        U.remove(u_star)

    return color


def rand_color(nodes, K):
    """Randomly assign a color from K classes to a set of nodes.

    Returns the solution constructed.
    """
    n = len(nodes)
    color = [random.randint(0,K-1) for i in nodes]
    return color

