def multidict(d: dict):
  ret = [list(d.keys())]
  for k, arr in d.items():
    if type(arr) is not list:
      arr = [arr]
    append_num = (1 + len(arr)) - len(ret)
    if append_num > 0:
      ret += [{} for _ in range(append_num)]

    for i, val in enumerate(arr):
      ret[i+1][k] = val

  return ret