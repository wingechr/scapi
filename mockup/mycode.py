def fun(a, b, c=None, d=None):
    c = 100 if c else 1
    d = sum(d) if d else 0
    return a * b + (c * d)


def fun2(b, c=None, d=None):
    c = 100 if c else 1
    d = sum(d) if d else 0
    return b + (c * d)
