def fun(a, b, c=None, d=None):
    print(a, b, c, d)
    c = c or 0
    d = sum(d or [])

    return a * b + (c * d)