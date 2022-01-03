def fun(a, b, c=False, d=None):
    return a * b * (2 if c else 1) * (d or 1)