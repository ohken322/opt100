import numpy as np

def read_mkp(filename, use_print=False):
    """
    問題インスタンス: https://www.researchgate.net/publication/271198281_Benchmark_instances_for_the_Multidimensional_Knapsack_Problem
    各MKPデータセットの問題は
    n: 変数の数
    m: 制約の数
    lb: 最適値の下限(0の場合が多い)
    として

    n m lb
    v_1 ... v_n
    w_11 ... w_1n
    ...
    w_m1 ... w_mn
    C_1 ... C_m

    の形式で書かれており、
    制約 w_j1 x_1 + ... + w_jn x_n \le C_j  (j=1,...,m)
    の下で
    v_1 x_1 + ... + v_n x_n 
    を最大化する問題となる。

    一つのファイル内に複数の問題インスタンスが書いてあることもあり、その場合には問題数が1行目に書いてある
    """
    with open(filename, 'r') as f:
        txts = f.read().lstrip('\n ')
    header_check = txts.split('\n')[0].split()
    if len(header_check)==1:
        txts = txts.lstrip(header_check[0])
    txts = txts.replace('\n', ' ')
    splitted = txts.split()
    mkps = []

    while splitted:
        n = int(splitted[0])
        m = int(splitted[1])
        optimal = float(splitted[2])
        offset = 3

        values = []
        for i in range(n):
            values.append(float(splitted[offset+i]))
        offset += n
        if use_print: print("values:", values)

        weights = []
        for j in range(m):
            weight = []
            for i in range(n):
                weight.append(int(splitted[offset+i]))
            weights.append(weight)
            #print(weight)
            offset += n

        capacities = []
        for i in range(m):
            capacities.append(int(splitted[offset+i]))
        offset += m
        #print(capacities)

        if use_print: 
            print("constraints:")
            for i in range(m):
                print(f"weights {weights[i]} with capacity {capacities[i]}")
        
        mkps.append((values, weights, capacities, optimal))
        splitted = splitted[offset:]

    return mkps
