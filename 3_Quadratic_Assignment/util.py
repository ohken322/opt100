def read_qap(filename):
    """Read data for a QAP problem from file in QAPLIB format."""
    try:
        if len(filename) > 3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip

            f = gzip.open(filename, "rb")
        else:  # usual, uncompressed file
            f = open(filename)
    except IOError:
        print("could not open file", filename)
        return None

    data = f.read()
    f.close()

    try:
        pass
        data = data.split()
        n = int(data.pop(0))
        f = {}  # for n times n flow matrix
        d = {}  # for n times n distance matrix
        for i in range(n):
            for j in range(n):
                f[i, j] = int(data.pop(0))
        for i in range(n):
            for j in range(n):
                d[i, j] = int(data.pop(0))
    except IndexError:
        print("inconsistent data on QAP file", filename)
        exit(-1)
    return n, f, d
