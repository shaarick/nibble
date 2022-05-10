from time import perf_counter

def timer(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"Time taken by {func.__name__}: {end - start:0.4f} seconds")
        return result
    return wrapper