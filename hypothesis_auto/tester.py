from inspect import isfunction, signature
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    get_type_hints,
)

from hypothesis.strategies import SearchStrategy, builds, just
from pydantic import BaseModel


class Parameters(NamedTuple):
    """Represents the parameters meant to passed into a callable."""

    args: List[Any]
    kwargs: Dict[str, Any]


class TestCase(NamedTuple):
    """Represents an individual auto generated test case. To run the test case simply call() it."""

    parameters: Parameters
    test_function: Callable

    def __call__(self) -> Any:
        """Calls the given test case returning the called functions result on success or
        Raising an exception on error
        """
        return self.test_function(*self.parameters.args, **self.parameters.kwargs)


def _test_function(
    _auto_function: Callable,
    _auto_verify: Callable = None,
    _auto_allow_exceptions: Union[Tuple[BaseException], Tuple] = (),
) -> Callable:
    return_type = get_type_hints(_auto_function).get("return", None)

    return_model = None
    if return_type:

        class ReturnModel(BaseModel):
            __annotations__ = {"returns": return_type}

        return_model = ReturnModel

    def test_function(*args, **kwargs) -> Any:
        try:
            result = _auto_function(*args, **kwargs)
        except _auto_allow_exceptions:  # type: ignore
            return

        if return_model:
            return_model(returns=result)
        if _auto_verify:
            _auto_verify(result)

        return result

    return test_function


def auto_parameters(
    _auto_function: Callable, *args, _auto_limit: int = 50, **kwargs
) -> Generator[Parameters, None, None]:
    """Generates parameters from the given callable up to the specified limit
    (`_auto_limit` parameter).

    By default auto_parameters uses type annotations to automatically decide on strategies via the
    hypothesis builds strategy. You can override individual strategies by passing them in under
    the corresponding `*arg` or `**kwarg` OR you can pass in specific values that must be used for
    certain parameters while letting others be auto generated.

    All `*arg` and `**kwargs` are automatically passed along to
    `hypothesis.strategies.builds` to enable this. Non strategies are automatically converted
    to strategies using `hypothesis.strategies.just`.

    Except for the following option:

    - *_auto_limit*: Number of strategies combinations to run the given function against.
    """
    strategy_args = [arg if isinstance(arg, SearchStrategy) else just(arg) for arg in args]
    strategy_kwargs = {
        name: value if isinstance(value, SearchStrategy) else just(value)
        for name, value in kwargs.items()
    }

    def pass_along_variables(*args, **kwargs):
        return Parameters(args=args, kwargs=kwargs)

    pass_along_variables.__signature__ = signature(_auto_function)  # type: ignore
    pass_along_variables.__annotations__ = getattr(_auto_function, "__annotations__", {})
    strategy = builds(pass_along_variables, *strategy_args, **strategy_kwargs)

    for _ in range(_auto_limit):
        yield strategy.example()


def auto_test_cases(
    _auto_function: Callable,
    *args,
    _auto_allow_exceptions: Union[Tuple[BaseException], Tuple] = (),
    _auto_limit: int = 50,
    _auto_verify: Optional[Callable] = None,
    **kwargs
) -> Generator[TestCase, None, None]:
    """Generates test cases from the given callable up to the specified limit
    (`_auto_limit` parameter).

    By default auto_test_cases uses type annotations to automatically decide on strategies via the
    hypothesis builds strategy. You can override individual strategies by passing them in under
    the corresponding `*arg` or `**kwarg` OR you can pass in specific values that must be used for
    certain parameters while letting others be auto generated.

    All `*arg` and `**kwargs` are automatically passed along to
    `hypothesis.strategies.builds` to enable this. Non strategies are automatically converted
    to strategies using `hypothesis.strategies.just`.

    Except for the following options:

    - *_auto_allow_exceptions*: A tuple of exceptions that are acceptable for the function to raise
      and will no be considered a test error.
    - *_auto_limit*: Number of strategies combinations to run the given function against.
    - *_auto_verify*: An optional callback function that will be called to allow custom verification
      of the functions return value. The callback function should raise an AssertionError if the
      return value does not match expectations.
    """
    test_function = _test_function(
        _auto_function, _auto_verify=_auto_verify, _auto_allow_exceptions=_auto_allow_exceptions
    )
    for parameters in auto_parameters(_auto_function, *args, _auto_limit=_auto_limit, **kwargs):
        yield TestCase(parameters=parameters, test_function=test_function)


def auto_test(
    _auto_function: Callable,
    *args,
    _auto_allow_exceptions: Union[Tuple[BaseException], Tuple] = (),
    _auto_runs: int = 50,
    _auto_verify: Optional[Callable] = None,
    **kwargs
) -> None:
    """A simple utility function for hypothesis that enables fully automatic testing for a
    type hinted callable, including return type verification.

    By default auto_test uses type annotations to automatically decide on strategies via the
    hypothesis builds strategy. You can override individual strategies by passing them in under
    the corresponding `*arg` or `**kwarg` OR you can pass in specific values that must be used for
    certain parameters while letting others be auto generated.

    All `*arg` and `**kwargs` are automatically passed along to
    `hypothesis.strategies.builds` to enable this. Non strategies are automatically converted
    to strategies using `hypothesis.strategies.just`.

    Except for the following options:

    - *_auto_allow_exceptions*: A tuple of exceptions that are acceptable for the function to raise
      and will no be considered a test error.
    - *_auto_runs*: Number of strategies combinations to run the given function against.
    - *_auto_verify*: An optional callback function that will be called to allow custom verification
      of the functions return value. The callback function should raise an AssertionError if the
      return value does not match expectations.
    """
    for test_case in auto_test_cases(
        _auto_function,
        *args,
        _auto_allow_exceptions=_auto_allow_exceptions,
        _auto_limit=_auto_runs,
        _auto_verify=_auto_verify,
        **kwargs
    ):
        test_case()


def auto_test_module(module: ModuleType) -> None:
    """Attempts to automatically test every public function within a module. For the brave only."""
    for attribute_name in dir(module):
        if not attribute_name.startswith("_"):
            attribute = getattr(module, attribute_name)
            if isfunction(attribute):
                auto_test(attribute)