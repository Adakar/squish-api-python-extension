# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, Cyber Alpaca
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import functools
import inspect
import sys
from typing import Any, Callable, List, Tuple, Type


class PrettyLookupError(LookupError):
    def __init__(self, e: LookupError, func: Callable[..., Any], *args: Any, **kwargs: Any):
        self.e = e
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return (
            f"Error in function '{self.func.__name__}': {self.e}\n"
            f"Arguments: {self.args}, Keyword Arguments: {self.kwargs}"
        )


# Example custom error classes
class SpecificLookupError1(PrettyLookupError):
    def __str__(self) -> str:
        return f"Specific Lookup Error 1: {self.e}"


class SpecificLookupError2(PrettyLookupError):
    def __str__(self) -> str:
        return f"Specific Lookup Error 2: {self.e}"


# Registry for custom error mappings
_error_registry: List[Tuple[int, Type[PrettyLookupError], Callable[[str], bool]]] = []


def register_pretty_error(
    error_class: Type[PrettyLookupError],
    condition: Callable[[str], bool],
    priority: int = 0,
) -> None:
    """
    Register a custom error class with a condition function and a priority.
    The condition function takes the error message as input and returns a boolean.
    Lower priority values are checked first.
    """
    _error_registry.append((priority, error_class, condition))
    # Sort the registry by priority (lower values first)
    _error_registry.sort(key=lambda x: x[0])


# Default error mappings
register_pretty_error(PrettyLookupError, lambda msg: True, priority=100)
register_pretty_error(SpecificLookupError1, lambda msg: "specific message 1" in msg, priority=200)
register_pretty_error(SpecificLookupError2, lambda msg: "specific message 2" in msg, priority=300)


def wrap_lookup_error(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except LookupError as e:
            error_msg = str(e)
            for error_class, condition in _error_registry:
                if condition(error_msg):
                    raise error_class(e, func, *args, **kwargs) from e
            raise e

    return wrapper


def pretty_lookup_errors() -> None:
    if "squish" not in sys.modules:
        raise ImportError("The 'squish' module is not imported.")

    module = sys.modules["squish"]
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if inspect.isbuiltin(attr):
            wrapped_function = wrap_lookup_error(attr)
            setattr(module, attr_name, wrapped_function)
            if attr_name in globals():
                globals()[attr_name] = wrapped_function
