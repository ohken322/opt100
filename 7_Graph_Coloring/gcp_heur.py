# LOG = True	# whether or not to print intermediate solutions
LOG = False	# whether or not to print intermediate solutions

def seq_assignment(nodes, adj):
    """Sequential color assignment.

    Starting with one color, for the graph represented by 'nodes' and 'adj':
       * go through all nodes, and check if a used color can be assigned;
       * if this is not possible, assign it a new color.
    Returns the solution found and the number of colors used.
       """
    K = 0       # number of colors used
    color = [None for i in nodes]       # solution vector
    for i in nodes:
        # determine colors currently assigned to nodes adjacent to i:
        adj_colors = set([color[j] for j in adj[i] if color[j] != None])
        if LOG:
            print( "adj_colors[%d]:\t%s" % (i, adj_colors),)
        for k in range(K):
            if k not in adj_colors:
                color[i] = k
                break
        else:
            color[i] = K
            K += 1
        if LOG:
            print( "--> color[%d]: %s" % (i, color[i]))
    return color, K


def largest_first(nodes, adj):
    """Sequencially assign colors, starting with nodes with largest degree.

    Firstly sort nodes by decreasing degree, then call sequential
    assignment, and return the solution it determined.
    """
    # sort nodes by decreasing degree (i.e., decreasing len(adj[i]))
    tmp = []    # to hold a list of pairs (degree,i)
    for i in nodes:
        degree = len(adj[i])
        tmp.append((degree,i))
    tmp.sort()          # sort by degree
    tmp.reverse()       # for decreasing degree
    sorted_nodes = [i for degree,i in tmp]      # extract the nodes from the pairs
    return seq_assignment(sorted_nodes, adj)    # sequential assignment on ordered nodes

    # # more efficient (geek) version:
    # nnodes = reversed(sorted([(len(adj[i]),i) for i in nodes]))
    # return seq_assignment([i for _,i in nnodes], adj)


def dsatur(nodes, adj):
    """Dsatur algorithm (Brelaz, 1979).
    
    Dynamically choose the vertex to color next, selecting one that is
    adjacent to the largest number of distinctly colored vertices.
    Returns the solution found and the number of colors used.
    """
    unc_adj = [set(adj[i]) for i in nodes]      # currently uncolored adjacent nodes
    adj_colors = [set([]) for i in nodes]       # set of adjacent colors, for each vertex
    color = [None for i in nodes]       # solution vector

    K = 0
    U = set(nodes)      # yet uncolored vertices
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
        if LOG:
            print( "u*:", u_star,)
            print( "\tadj_colors[%d]:\t%s" % (u_star, adj_colors[u_star]),)

        # find a color for node 'u_star'
        for k in range(K):
            if k not in adj_colors[u_star]:
                k_star = k
                break
        else:   # must use a new color
            k_star = K
            K += 1
        color[u_star] = k_star
        for i in unc_adj[u_star]:
            unc_adj[i].remove(u_star)
            adj_colors[i].add(k_star)

        U.remove(u_star)

        if LOG:
            print( "--> color[%d]:%s" % (u_star, color[u_star]))
    return color, K


def recursive_largest_fit(nodes, adj):
    """Recursive largest fit algorithm (Leighton, 1979).

    Color vertices one color class at a time, in a greedy way.
    Returns the solution found and the number of colors used.
    """
    K = 0               # current color class
    V = set(nodes)      # yet uncolored vertices
    color = [None for i in nodes]       # solution vector
    unc_adj = [set(adj[i]) for i in nodes]      # currently uncolored adjacencies

    while V:
        
        # phase 1: color vertex with max number of connections to uncolored vertices
        max_edges = -1
        for i in V:
            n = len(unc_adj[i])
            if n > max_edges:
                max_edges = n
                u_star = i

        V.remove(u_star)
        color[u_star] = K
        for i in unc_adj[u_star]:
            unc_adj[i].remove(u_star)
        U = set(unc_adj[u_star]) # adj.vertices are uncolorable with current color
        V -= unc_adj[u_star]     # remove them from V
        if LOG:
            print( "phase 1, u* =", u_star, "\tU =", U, "\tV =", V)

        # phase 2: check for other vertices that can have the same color (K)
        while V:
            # determine colorable vertex with maximum uncolorable adjacencies:
            max_edges = -1
            for i in V: 
                v_adj = unc_adj[i] & U  # uncolorable, adjacent vertices 
                n = len(v_adj)
                if n > max_edges:
                    max_edges = n
                    u_star = i
            V.remove(u_star)
            color[u_star] = K
            for i in unc_adj[u_star]:
                unc_adj[i].remove(u_star)
            
            # remove from V all adjacencies not colorable with K
            not_colored = unc_adj[u_star] & V
            V -= not_colored    # remove uncolored adjacencies from V
            U |= not_colored    # add them to U
            if LOG:
                print( "phase 2, u* =", u_star, "\tU =", U, "\tV =", V)

        V = U   # update list of yet uncolored vertices
        K += 1  # switch to next color class

    return color, K


def recursive_largest_fit_2(nodes, adj):
    """Recursive largest fit algorithm (Leighton, 1979).

    Color vertices one color class at a time, in a greedy way.
    Returns the solution found and the number of colors used.
    """
    K = 0               # current color class
    V = set(nodes)      # yet uncolored vertices
    color = [None for i in nodes]       # solution vector
    unc_adj = [set(adj[i]) for i in nodes]      # currently uncolored adjacencies

    while V:
        
        # phase 1: color vertex with max number of connections to uncolored vertices
        max_edges = -1
        for i in V:
            n = len(unc_adj[i])
            if n > max_edges:
                max_edges = n
                u_star = i

        V.remove(u_star)
        color[u_star] = K
        for i in unc_adj[u_star]:
            unc_adj[i].remove(u_star)
        U = set(unc_adj[u_star]) # adj.vertices are uncolorable with current color
        V -= unc_adj[u_star]     # remove them from V
        if LOG:
            print( "phase 1, u* =", u_star, "\tU =", U, "\tV =", V)

        # phase 2: check for other vertices that can have the same color (K)
        while V:
            # determine colorable vertex with maximum uncolorable adjacencies:
            min_edges = len(nodes) + 1
            for i in V: 
                v_adj = unc_adj[i] & U  # uncolorable, adjacent vertices 
                n = len(v_adj)
                if n < min_edges:
                    min_edges = n
                    u_star = i
            V.remove(u_star)
            color[u_star] = K
            for i in unc_adj[u_star]:
                unc_adj[i].remove(u_star)
            
            # remove from V all adjacencies not colorable with K
            not_colored = unc_adj[u_star] & V
            V -= not_colored    # remove uncolored adjacencies from V
            U |= not_colored    # add them to U
            if LOG:
                print( "phase 2, u* =", u_star, "\tU =", U, "\tV =", V)

        V = U   # update list of yet uncolored vertices
        K += 1  # switch to next color class

    return color, K


def check(nodes,adj,color):
    """Auxiliary function, for checking if a coloring is valid."""
    for i in nodes:
        for j in adj[i]:
            if color[i] != None and color[i] == color[j]:
                txt = "nodes %d,%d are connected and have the same color (%d)" % (i,j,color[i])
                raise ValueError(txt)

