def fun(a, b, c=None, d=None):
    c = 100 if c else 1
    d = sum(d) if d else 0
    return a * b + (c * d)
