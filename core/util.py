def clamp(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x

def flatten(x: list | tuple):
    flattened = []
    for e in x:
        if isinstance(e, list) | isinstance(e, tuple):
            flattened += [flatten(e)]
        else:
            flattened += [e]
    if isinstance(x, tuple):
        return tuple(flattened)
    return flattened
