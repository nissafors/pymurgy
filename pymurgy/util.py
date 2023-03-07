import inspect


def is_instance_of_name(obj: object, name: str):
    """Returns True if obj is a subclass of a class with given name.

    The rational for this function is that isinstance can not always be trusted when imports get a little complex.
    In our case unit tests get us in trouble.
    """
    for superclass in obj.__class__.__mro__:  # Skip <class 'object'>
        c = str(superclass).lstrip("<class '").rstrip("'>")
        if "." in c:
            c = c.split(".")[-1]
        if c == name:
            return True
    return False


def func_params(function: callable):
    """Returns a list of a functions parameter names.

    If the first parameter is called "self" it is not included.

    Example:
        class MyClass
            def __init__(self, a):
                self.a = a

        def func(a, b, c):
            return a + b + c

        p = func_params(MyClass.__init__)  # p = ["a"]
        p = func_params(func)              # p = ["a", "b", "c"]
    """
    init_sig = inspect.signature(function).parameters
    params = list(init_sig.keys())
    if params and params[0] == "self":
        return params[1:]
    else:
        return params
