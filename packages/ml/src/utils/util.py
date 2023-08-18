import time

from langchain.schema import LLMResult


class Timeless:
    def __init__(self):
        self.start = time.time()

    def end(self, thing: str | None = None):
        end = time.time() - self.start
        # convert to H:M:S
        m, s = divmod(end, 60)
        h, m = divmod(m, 60)
        # get name of function too
        print(f"{f'{thing} ' if thing else ''}took {h:.0f}h:{m:.0f}m:{s:.0f}s")


def time_start() -> Timeless:
    return Timeless()


def atimeit(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time() - start
        # convert to H:M:S
        m, s = divmod(end, 60)
        h, m = divmod(m, 60)
        # get name of function too
        print(f"{func.__name__} took {h:.0f}h:{m:.0f}m:{s:.0f}s")
        return result

    return wrapper


# create a decorator that print time of execution of async function using time.time() in H:M:S
def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time() - start
        # convert to H:M:S
        m, s = divmod(end, 60)
        h, m = divmod(m, 60)
        # get name of function too
        print(f"{func.__name__} took {h:.0f}h:{m:.0f}m:{s:.0f}s")
        return result

    return wrapper

def get_total_tokens(llm_result: LLMResult) -> int:
    token_usage = llm_result.llm_output["token_usage"]
    total_tokens = token_usage["total_tokens"]
    return total_tokens


def create_deeplake():
    pass
