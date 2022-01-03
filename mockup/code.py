def fun(a, b, c=False, d=None):
    print(a, b, c, d)
    c = 100 if c else 1
    d = sum(d or [])
    return a * b + (c * d)
