import inspect


async def call_function(func, *args, **kwargs):
    # Calls function provided with arguments
    if inspect.inspect.iscoroutinefunction:
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)