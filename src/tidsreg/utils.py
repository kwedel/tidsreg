def skip_n(it, n=1):
    """Skip n elements in iterator"""
    for i, element in enumerate(it):
        if i >= n:
            yield element
