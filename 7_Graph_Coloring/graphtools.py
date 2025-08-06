"""
graphtools.py: functions for making, or reading graphs in several formats

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""
import random, math

def rnd_graph(n, prob):
    """Make a random graph with 'n' nodes, and edges created between
       pairs of nodes with probability 'prob'.
       Returns a pair, consisting of the list of nodes and the list of edges.
    """
    nodes = range(n)
    edges = []
    for i in range(n-1):
        for j in range(i+1,n):
            if random.random() < prob:
                edges.append((i,j))
    return nodes, edges


def rnd_adj(n, prob):
    """Make a random graph with 'n' nodes and 'nedges' edges.
       return node list [nodes] and adjacency list (list of list) [adj] """
    nodes = range(n)
    adj = [set([]) for i in nodes]
    for i in range(n-1):
        for j in range(i+1,n):
            if random.random() < prob:   
                adj[i].add(j)
        adj[j].add(i)
    return nodes, adj


def rnd_adj_fast(n, prob):
    """Make a random graph with 'n' nodes, and edges created between
       pairs of nodes with probability 'prob', running in  O(n+m)
       [n is the number of nodes and m is the number of edges].
       Returns a pair, consisting of the list of nodes and the list of edges.
      """
    nodes = range(n)
    adj = [set([]) for i in nodes]

    if prob == 1:
        return nodes, [[j for j in nodes if j != i] for i in nodes]

    i = 1   # the first node index
    j = -1
    logp = math.log(1.0-prob)  	#

    while i < n:
        logr = math.log(1.0-random.random())
        j += 1+int(logr/logp)
        while j >= i and i < n:
            j -= i
            i += 1
        if i < n:	# else, graph is ready
            #print( "add edge", (i,j))
            adj[i].add(j)
            adj[j].add(i)
    return nodes, adj


def adjacent(nodes, edges):
    """Determine the adjacent nodes on the graph."""
    adj = [set([]) for i in nodes]
    for (i,j) in edges:
        adj[i].add(j)
        adj[j].add(i)
    return adj


def complement(nodes, edges):
    """determine the complement of 'edges'"""
    compl = []
    edgeset = set(edges)
    for i in range(len(nodes)-1):
        for j in range(i+1,len(nodes)):
            if (i,j) not in edgeset:
                # assert (i,j) not in compl
                compl.append((i,j))
    return compl


def shuffle(nodes, adj):
    """randomize graph: exchange labels of two vertices, a number of times"""
    n = len(nodes)
    order = range(n)
    random.shuffle(order)

    newadj = [None for i in nodes]
    for i in range(n):
        newadj[order[i]] = [order[j] for j in adj[i]]
        newadj[order[i]].sort()
    return newadj



def read_gpp_graph(filename):
    """Read a file in the format specified by David Johnson for the DIMACS
    graph partitioning challenge.
    Instances are available at ftp://dimacs.rutgers.edu/pub/dsj/partition
    """
    try:
        if len(filename)>3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip
            f = gzip.open(filename, "rb")
        else:   # usual, uncompressed file
            f = open(filename)
    except IOError:
        print( "could not open file", filename)
        exit(-1)

    lines = f.readlines()
    f.close()
    n = len(lines)
    nodes = range(n)
    edges = set([])
    adj = [[] for i in nodes]
    pos = [None for i in nodes]

    for i in nodes:
        lparen = lines[i].find("(")
        rparen = lines[i].find(")")+1
        x, y = None, None
        exec("x,y = %s" % lines[i][lparen:rparen])
        pos[i] = (x,y)
        paren = lines[i].find(")")+1
        remain = lines[i][paren:].split()
        for j_ in remain[1:]:
            j = int(j_)-1 # -1 for having nodes index starting on 0
            if j>i:
                edges.add((i,j))
            adj[i].append(j)
    for (i,j) in edges:
        assert i in adj[j] and j in adj[i]
    return nodes, adj


def read_gpp_coords(filename):
    """Read coordinates for a graph in the format specified by David Johnson
    for the DIMACS graph partitioning challenge.
    Instances are available at ftp://dimacs.rutgers.edu/pub/dsj/partition
    """
    try:
        if len(filename)>3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip
            f = gzip.open(filename, "rb")
        else:   # usual, uncompressed file
            f = open(filename)
    except IOError:
        print( "could not open file", filename)
        exit(-1)

    lines = f.readlines()
    f.close()
    n = len(lines)
    nodes = range(n)
    pos = [None for i in nodes]
    for i in nodes:
        lparen = lines[i].find("(")
        rparen = lines[i].find(")")+1
        x, y = None, None
        exec("x,y = %s" % lines[i][lparen:rparen])
        pos[i] = (x,y)
    return pos



def read_graph(filename):
    """Read a graph from a file in the format specified by David Johnson
    for the DIMACS clique challenge.
    Instances are available at
    ftp://dimacs.rutgers.edu/pub/challenge/graph/benchmarks/clique
    """
    try:
        if len(filename)>3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip
            f = gzip.open(filename, "rb")
        else:   # usual, uncompressed file
            f = open(filename)
    except IOError:
        print( "could not open file", filename)
        exit(-1)

    for line in f:
        if line[0] == 'e':
            e, i, j = line.split()
            i,j = int(i)-1, int(j)-1 # -1 for having nodes index starting on 0
            adj[i].add(j)
            adj[j].add(i)
        elif line[0] == 'c':
            continue
        elif line[0] == 'p':
            p, name, n, nedges = line.split()
            # assert name == 'clq'
            n, nedges = int(n), int(nedges)
            nodes = range(n)
            adj = [set([]) for i in nodes]
    f.close()
    return nodes, adj



def read_compl_graph(filename):
    """Produce complementary graph with respect to the one define in a file,
    in the format specified by David Johnson for the DIMACS clique challenge.
    Instances are available at
    ftp://dimacs.rutgers.edu/pub/challenge/graph/benchmarks/clique
    """
    nodes,adj = read_graph(filename)
    nset = set(nodes)
    for i in nodes:
        adj[i] = nset - adj[i] - set([i])
    return nodes, adj



