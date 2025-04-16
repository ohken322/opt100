import random

Infinity = 1.e10000
LOG = True

def evaluate(nodes, adj, sol) -> tuple:
    """解を評価する

    Parameters
    ----------
    nodes : list
        ノード集合
    adj : dict
        各ノードの隣接ノード集合
    sol : set
        解 (頂点集合の部分集合)

    Returns
    -------
    card : int
        解の位数
    infeas : int
        制約違反度合い (存在する辺の数)
    b : list
        元のグラフの各頂点に対する，解の中で隣接する頂点の数
    """
    card = len(sol) # 位数
    b = [0 for i in nodes]
    infeas = 0 # 制約違反度合い (存在する辺の数)
    for i in sol:
        for j in adj[i]:
            b[j] += 1
            if j in sol:
                infeas += 1
    assert infeas%2==0
    return card, infeas//2, b


def construct(nodes, adj) -> set:
    """ランダムに極大な(最大とは限らない)クリークを返す

    Parameters
    ----------
    nodes : list
        ノード集合
    adj : dict
        各ノードの隣接ノード集合

    Returns
    -------
    set
        極大クリーク
    """
    sol = set([])
    b = [0 for i in nodes] # 各頂点に対する，(暫定)解の中で隣接する頂点の数 (つまり，0の頂点は解に加えることができる)
    indices = list(nodes)
    random.shuffle(indices)
    for ii in nodes:
        i = indices[ii]
        if b[i] == 0:
            sol.add(i)
            for j in adj[i]:
                b[j] += 1
    return sol


def find_add(nodes, adj, sol, b, tabu, tabulen, iteration):
    xdelta = Infinity
    istar = []
    for i in set(nodes) - sol:
        if random.random() > float(tabu[i] - iteration)/tabulen:
            delta = b[i]
            if delta < xdelta:
                xdelta = delta
                istar = [i]
            elif delta == xdelta:
                istar.append(i)
    
    if istar != []:
        return random.choice(istar)
    
    print("blocked, no non-tabu move")
    for i in nodes:
        tabu[i] = min(tabu[i], iteration)
    return find_add(nodes, adj, sol, b, tabu, tabulen, iteration)


def find_drop(nodes, adj, sol, b, tabu, tabulen, iteration):
    xdelta = -Infinity
    istar = []
    for i in sol:
        if random.random() > float(tabu[i] - iteration)/tabulen:
            delta = b[i]
            if delta > xdelta:
                xdelta = delta
                istar = [i]
            elif delta == xdelta:
                istar.append(i)

    if istar != []:
        return random.choice(istar)
    
    print("blocked, no non-tabu move")
    for i in nodes:
        tabu[i] = min(tabu[i], iteration)
    
    return find_drop(nodes, adj, sol, b, tabu, tabulen, iteration)


def move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, iteration):
    i = find_add(nodes, adj, sol, b, tabu, tabuOUT, iteration)
    tabu[i] = iteration + tabuIN
    sol.add(i)

    delta_infeas = 0
    for j in adj[i]:
        b[j] += 1
        if j in sol:
            delta_infeas += 1
    return delta_infeas


def move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, iteration):
    i = find_drop(nodes, adj, sol, b, tabu, tabuIN, iteration)

    tabu[i] = iteration + tabuOUT
    sol.remove(i)

    delta_infeas = 0
    for j in adj[i]:
        b[j] -= 1
        if j in sol:
            delta_infeas -= 1
    return delta_infeas


def tabu_search(nodes, adj, sol, max_iter, tabulen, report=None):
    n = len(nodes)
    tabu = [0 for i in nodes]

    card, infeas, b = evaluate(nodes, adj, sol)
    assert infeas == 0 # ここでは実行可能解が出ているはず
    bestsol, bestcard = set(sol), card

    if LOG:
        print(f"iter: 0 \tcard: {card} ({infeas} conflicts) \tbest: {bestcard}")
    
    for it in range(max_iter):
        tabuIN = 1 + int(tabulen/100 * card)
        tabuOUT = 1 + int(tabulen/100 * (n-card))
        if infeas == 0:
            infeas += move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card += 1
        else:
            infeas += move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card -= 1

        if infeas == 0 and card > bestcard:
            bestsol, bestcard = set(sol), card
            if report:
                report(card, "iter:", it)
            
        if LOG:
            print(f"iter: {it+1} \tcard: {card} ({infeas} conflicts) \tbest: {bestcard}")

    # sanity check
    xcard, xinfeas, xb = evaluate(nodes, adj, bestsol)
    assert bestcard == xcard and xinfeas == 0
    return bestsol, bestcard


# Tabu search with diversification & intensification

def diversify(nodes, adj, v):
    b = [0 for i in nodes]
    sol = set([v])
    for j in adj[v]:
        b[j] += 1
    
    indices = list(nodes)
    random.shuffle(indices)
    for ii in nodes:
        i = indices[ii]
        if i==v: continue
        if b[i] == 0:
            sol.add(i)
            for j in adj[i]:
                b[j] += 1
    return sol


def ts_intens_divers(nodes, adj, sol, max_iter, tabulen, report=None):
    n = len(nodes)
    tabu = [0 for i in nodes]

    card, infeas, b = evaluate(nodes, adj, sol)
    assert infeas == 0

    bestsol, bestcard, bestb = set(sol), card, list(b)

    D = 1
    count = 0
    lastcard = card
    if LOG:
        print(f"iter: 0 \tnon-improved: {count}/{D} \tcard: {card} ({infeas} conflicts) \tbest: {bestcard}")

    for it in range(max_iter):
        tabuIN = 1 + int(tabulen/100 * card)
        tabuOUT = 1 + int(tabulen/100 * (n-card))
        if infeas == 0:
            infeas += move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card += 1
        else:
            infeas += move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card -= 1

        if LOG:
            print(f"iter: {it+1} \tnon-improved: {count}/{D} \tcard: {card} ({infeas} conflicts) \tbest: {bestcard}")

        if infeas == 0 and card > bestcard:
            bestsol, bestcard, bestb = set(sol), card, list(b)
            if report:
                report(card, "iter:", it)
            if LOG:
                print("*** intensifying: clearing tabu list ***")
                tabu = [min(tabu[i], it) for i in nodes]
                count = 0
        elif infeas == 0 and card > lastcard:
            count = 0
        else:
            count += 1
        
        if count > D:
            if D%2==0:
                if LOG:
                    print("*** intensifying: switching to best found solution ***")
                sol, card, b = set(bestsol), bestcard, list(bestb)
                infeas = 0
            else:
                if LOG:
                    print("*** diversifying: constructing maximal clique forom less used vertex ***")
                cand = []
                mintabu = Infinity
                for j in set(nodes) - sol:
                    if tabu[j] < mintabu:
                        cand = [j]
                    if tabu[j] == mintabu:
                        cand.append(j)
                v = random.choice(cand)

                sol = diversify(nodes, adj, v)
                card, infeas, b = evaluate(nodes, adj, sol)
                if infeas == 0 and card > bestcard:
                    bestsol, bestcard, bestb = set(sol), card, list(b)
                    if report:
                        report(card, "iter:", it)
                tabu = [min(tabu[i], it) for i in nodes]
            
            count = 0
            D += 1
        
        if infeas == 0:
            lastcard = card

    # sanity check
    xcard, xinfeas, xb = evaluate(nodes, adj, bestsol)
    assert bestcard == xcard and xinfeas == 0
    return bestsol, bestcard


# Plateau-search
# Escape from large plataeu (set of solutions with same objective) in maximum stable set problem.

def possible_add(rmn: set, b):
    return [i for i in rmn if b[i] == 0]


def one_edge(rmn, b):
    return [i for i in rmn if b[i] == 1]


def add_node(i, adj, sol, rmn, b):
    sol.add(i)
    rmn.remove(i)
    for j in adj[i]:
        b[j] += 1


def expand_rand(add, sol, rmn, b, adj, maxiter, dummy=None):
    iteration = 0
    while add != [] and iteration < maxiter:
        iteration += 1
        i = random.choice(add)
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add, b)
    return iteration


def expand_stat_deg(add, sol, rmn, b, adj, maxiter, degree):
    iteration = 0
    while add != [] and iteration < maxiter:
        iteration += 1
        min_deg = Infinity
        cand = []
        for i in add:
            if degree[i] < min_deg:
                cand = [i]
                min_deg = degree[i]
            elif degree[i] == min_deg:
                cand.append(i)
        i = random.choice(cand)
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add, b)
    return iteration


def expand_dyn_deg(add, sol, rmn, b, adj, maxiter, dummy=None):
    iteration = 0
    degree = {}
    for i in add:
        degree[i] = len(set(add) & adj[i])
    while add != [] and iteration < maxiter:
        iteration += 1
        min_deg = Infinity
        cand = []
        for i in add:
            if degree[i] < min_deg:
                cand = [i]
                min_deg = degree[i]
            elif degree[i] == min_deg:
                cand.append(i)
        i = random.choice(cand)

        # update degree
        for j in set(add) & adj[i]:
            for k in set(add) & adj[i]:
                degree[k] -= 1
        
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add, b)

    return iteration


def iterated_expansion(nodes, adj, expand_fn, niterations, report=None):
    degree = [len(adj[i]) for i in nodes]
    bestcard = 0
    iteration = 0
    while iteration < niterations:
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]
        add = list(nodes)
        iteration += expand_fn(add, sol, rmn, b, adj, niterations-iteration, degree)
        if len(sol) > bestcard:
            bestcard = len(sol)
            bestsol = list(sol)
            bestrmn = list(rmn)
            if report:
                report(bestcard, "sol:", sol)
        if LOG:
            print(f"iter: {iteration} \t{len(sol)}/{bestcard}")
    return bestsol, bestrmn, bestcard


def node_replace(v, sol, rmn, b, adj):
    connected = adj[v].intersection(sol) # intersection は set function?
    i = connected.pop()
    rmn.add(i)
    sol.remove(i)
    expand_nodes = []
    for j in adj[i]:
        b[j] -= 1
        if b[j] == 0 and j not in sol:
            expand_nodes.append(j)
    return expand_nodes


def plateau(sol, rmn, b, adj, maxiter):
    iteration = 0
    while iteration < maxiter:
        one = one_edge(rmn, b)
        if one == []:
            return iteration, []
        v = random.choice(one)
        iteration += 2
        add_node(v, adj, sol, rmn, b)
        expand_nodes = node_replace(v, sol, rmn, b, adj)
        if expand_nodes != []:
            return iteration, expand_nodes
        
    return iteration, []


def multistart_local_search(nodes, adj, expand_fn, niterations, length, report=None):
    degree = [len(adj[i]) for i in nodes]
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    while iteration < niterations:
        if LOG:
            print("New plateau search")
        add = list(nodes)
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]

        while add != []:
            iteration += expand_fn(add, sol, rmn, b, adj, niterations-iteration, degree)
            if LOG:
                print("expanding...", len(sol))
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol:", sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol, rmn, b, adj, maxiter)
            iteration += usediter
            if LOG:
                print("plateau phase...", len(sol))
                print(f"\t\titer:{iteration}\t{len(sol)}/{bestcard}")
    
    return bestsol, bestrmn, bestcard


def expand_through(add, sol, rmn, expand_fn, b, adj, maxiter, degree):
    """Expand the current stable set ('sol').
    Initially use nodes in 'add' for the expansion;
    then, try with all the unselected nodes (those in 'rmn')."""
    # expand first through nodes sugested in 'add' only
    iteration = expand_fn(add, sol, rmn, b, adj, maxiter, degree)
    # check if expansion is possible through any node
    add = possible_add(rmn,b)
    return iteration + expand_fn(add, sol, rmn, b, adj, maxiter-iteration, degree)



def ltm_search(nodes, adj, expand_fn, niterations, length, report=None):
    """Plateau search including long-term memory,
    using 'expand_fn' for the expansion.

    Long-term memory 'ltm' keeps the number of times each node
    was used after successful expansions.
    
    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
     * length -- number of searches to do attempt on the each plateau
    """
    degree = [len(adj[i]) for i in nodes]   # used on 'expand_stat_deg'
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    ltm = [0 for i in nodes]
    while iteration < niterations:

        if LOG:
            print("New plateau search")
        # select nodes for staring expansion
        # starting solution
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]

        # alternate between using intensification and diversification, using ltm
        if random.random() < 0.5:
            # # insert one of the most used nodes in stable set
            # maxsel = -1
            # for i in rmn:
            #     if ltm[i] > maxsel:
            #         maxsel = ltm[i]
            #         cand = [i]
            #     elif ltm[i] == maxsel:
            #         cand.append(i)
            # other possibility: insert one of the nodes from the best solution into the stable set
            if bestsol != []:
                cand = list(bestsol)
            else:
                cand = list(rmn)
        else:
            # insert one of the least used nodes in stable set
            minsel = Infinity
            for i in rmn:
                if ltm[i] < minsel:
                    minsel = ltm[i]
                    cand = [i]
                elif ltm[i] == minsel:
                    cand.append(i)

        # start expansion through intensification/diversification selected nodes
        add = cand

        while add != []:
            if LOG:
                print ("expanding...", len(sol))
            iteration += expand_through(add,sol,rmn,expand_fn,b,adj,niterations-iteration,degree)
            for i in sol:
                ltm[i] += 1
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol: %r" % sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol,rmn,b,adj,maxiter)
            iteration += usediter
            if LOG:
                print( "plateau phase...", len(sol))
                print( '\t\titer:%d\t%d/%d' % (iteration, len(sol), bestcard))


    return bestsol, bestrmn, bestcard



def rm_node(i, adj, sol, rmn, b):
    """Move node 'i' from 'sol' into 'rmn', and update 'b' accordingly."""
    rmn.add(i)
    sol.remove(i)
    for j in adj[i]:
        b[j] -= 1



def hybrid(nodes, adj, niterations, length, report=None):
    """Plateau search, using a hybrid approach.
    
    The solution is partially kept after each plateau search:
    a node from the unselected 'rmn' set is chosen and added to
    the stable set, and then the conflicting nodes are removed.

    Plateau expansions are done through a randomly selected method,
    from random expansion, dynamic-degree-based expansion, or
    static-degree expansion.

    Long-term memory 'ltm' keeps the number of times each node
    was used after successful expansions.
    
    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
     * length -- number of searches to do attempt on the each plateau
    """
    expand_fns = [expand_rand, expand_stat_deg, expand_dyn_deg]

    degree = [len(adj[i]) for i in nodes]   # used on 'expand_stat_deg'
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    rmn = set(nodes)
    sol = set([])
    b = [0 for i in nodes]
    ltm = [0 for i in nodes]
    while iteration < niterations:

        if LOG:
            print( "New plateau search")
        # alternate between using intensification and diversification, using ltm
        if random.random() < 0.5:
            # # insert one of the most used nodes in stable set
            # maxsel = -1
            # for i in rmn:
            #     if ltm[i] > maxsel:
            #         maxsel = ltm[i]
            #         cand = [i]
            #     elif ltm[i] == maxsel:
            #         cand.append(i)
            # add = random.choice(cand)
            # other possibility: pick a currently unselected node from best solution
            cand = rmn & set(bestsol)
            if len(cand) != 0:
                add = random.choice(list(cand))
            else:
                add = random.choice(list(rmn))
        else:
            # insert one of the least used nodes in stable set
            minsel = Infinity
            for i in rmn:
                if ltm[i] < minsel:
                    minsel = ltm[i]
                    cand = [i]
                elif ltm[i] == minsel:
                    cand.append(i)
            add = random.choice(cand)

        ### for some problems ltm causes losses in solution quality;
        ### in these cases (e.g. san400_0.7_1.clq), it is better to do
        # add = random.choice(rmn)

        # remove nodes on the set that would cause conflicts
        for i in sol & adj[add]:
            rm_node(i, adj, sol, rmn, b)
            iteration += 1

        add_node(add, adj, sol, rmn, b)
        iteration += 1

        add = possible_add(rmn,b)
        # expand_fn = random.choice(expand_fns)
        while add != []:
            expand_fn = random.choice(expand_fns)
            iteration += expand_through(
                add,sol,rmn,expand_fn,b,adj,niterations-iteration,degree
            )
            for i in sol:
                ltm[i] += 1
            if LOG:
                print( "expanding...", len(sol))
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol: %r" % sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol,rmn,b,adj,maxiter)
            iteration += usediter 
            if LOG:
                print( "plateau phase...", len(sol))
                print( '\t\titer:%d\t%d/%d' % (iteration, len(sol), bestcard))

    return bestsol, bestrmn, bestcard