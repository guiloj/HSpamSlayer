#############################
# ======== IMPORTS ======== #
#############################

import typing as t  # don't want to pollute the namespace
from pathlib import Path as p

###########################
# ======== TYPES ======== #
###########################

T = t.TypeVar("T")


class NONE:
    ...


############################
# ======== ERRORS ======== #
############################


class ExpectedValue(Exception):
    pass


#############################
# ======== CLASSES ======== #
#############################


class __Result(t.Generic[T]):
    def __init__(
        self,
        result: t.Union[T, t.Type[NONE]],
        error: t.Union[BaseException, t.Type[NONE]],
    ):
        self._result = result
        self._error = error

    def unwrap(self):
        """Unwrap the result. If the result is NONE panic."""
        ...

    def expect(self, msg: str):
        """Unwrap the result. If the result is NONE panic with custom message."""
        ...

    def is_err(self):
        """Check if the result is an Err instance."""
        ...

    def is_ok(self):
        """Check if the result is an Ok instance."""
        ...

    @property
    def err(self):
        """Get the error value for the result."""
        ...


class Ok(__Result[T]):
    def __init__(self, result: T):
        super().__init__(result, NONE)

    def unwrap(self) -> T:
        return self._result  # type: ignore - I know it will not be NONE for sure

    def expect(self, _: str) -> T:
        return self._result  # type: ignore - I know it will not be NONE for sure

    def is_err(self):
        return False

    def is_ok(self):
        return True

    @property
    def err(self):
        return NONE


class Err(__Result[t.Type[NONE]]):
    def __init__(self, error: BaseException):
        super().__init__(NONE, error)

    def unwrap(self) -> t.NoReturn:
        panic(ExpectedValue("Value expected, got NONE."))

    def expect(self, msg: str) -> t.NoReturn:
        panic(ExpectedValue("Value expected, got NONE."), msg)

    def is_err(self):
        return True

    def is_ok(self):
        return False

    @property
    def err(self) -> BaseException:
        return self._error  # type: ignore - I know it will be an error for sure


###########################


class __Option(t.Generic[T]):
    def __init__(self, value: T):
        self._value = value

    def unwrap(self) -> T:
        """Unwrap the option. If the option is NONE panic."""
        ...

    def unwrap_or(self, _: T):
        """Unwrap the option. If the option is NONE return a default value."""
        ...

    def expect(self, _: str):
        """Unwrap the result. If the result is NONE panic with custom message."""
        ...


class Some(__Option[T]):
    def __init__(self, value: T):
        super().__init__(value)
        assert type(T) != NONE, "Some() type can't be NONE"

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, _: T) -> T:
        return self._value

    def expect(self, _: str) -> T:
        return self._value


class Nothing(__Option[t.Type[NONE]]):
    def __init__(self):
        super().__init__(NONE)

    def unwrap(self) -> t.NoReturn:
        panic(ExpectedValue("Value expected, got NONE."))

    def unwrap_or(self, default: T) -> T:
        return default

    def expect(self, msg: str) -> t.NoReturn:
        panic(ExpectedValue("Value expected, got NONE."), msg)


###############################
# ======== FUNCTIONS ======== #
###############################


def panic(err: BaseException, msg: str = f"{p(__file__).name} panicked!"):
    print(msg)
    raise err


#################################
# ======== UNION TYPES ======== #
#################################

Option = t.Union[Some[T], Nothing]
Result = t.Union[Ok[T], Err]
