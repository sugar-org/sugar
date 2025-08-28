"""Validation helpers for function parameters.

This module provides decorators to validate function arguments before the
wrapped function is executed.
"""

from __future__ import annotations

import functools
import inspect

from collections.abc import Collection
from typing import Any, Callable, Iterable, NoReturn, TypeVar, cast

from typing_extensions import ParamSpec

from sugar.logs import SugarError, SugarLogs

P = ParamSpec('P')
R = TypeVar('R')


def validate_param(
    name: str,
    *,
    required: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    allow_empty_collections: bool = False,
    strip: bool = True,
    forbidden: Iterable[Any] = ('',),
    predicate: Callable[[Any], bool] | None = None,
    error_message: str | None = None,
    error_code: Any | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Validate a single function argument before running the function.

    Parameters
    ----------
    name
        Name of the argument to validate.
    required
        If True, the argument must be provided after defaults are applied.
    allow_none
        If False, ``None`` is invalid.
    allow_empty
        If False, empty strings (after optional stripping) are invalid.
    allow_empty_collections
        If False, empty collections (list/tuple/dict/set) are invalid.
    strip
        If True and the value is a string, apply ``str.strip()`` before checks.
    forbidden
        Literal values that are disallowed (checked after optional ``strip``).
    predicate
        Custom validator that returns ``True`` for valid values.
    error_message
        Custom error message; may use ``{param}`` and ``{value}`` placeholders.
    error_code
        Optional code forwarded to ``SugarLogs.raise_error``.

    Returns
    -------
    Callable
        A decorator that enforces the validation and aborts on failure.

    Raises
    ------
    ValueError
        If validation fails and no logger raises a custom error.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if name not in bound.arguments:
                _emit_error(
                    (error_message or 'Missing argument "{param}".').format(
                        param=name, value=None
                    ),
                    error_code,
                )

            value = bound.arguments[name]
            v = value.strip() if isinstance(value, str) and strip else value

            valid = True

            if required and name not in bound.arguments:
                valid = False
            elif not allow_none and v is None:
                valid = False
            elif isinstance(v, str):
                if not allow_empty and v == '':
                    valid = False
                elif v in forbidden:
                    valid = False
            elif any(v == f for f in forbidden):
                valid = False

            if (
                not allow_empty_collections
                and isinstance(v, Collection)
                and not isinstance(v, (str, bytes))
                and len(v) == 0
            ):
                valid = False

            if predicate is not None:
                try:
                    if not predicate(v):
                        valid = False
                except Exception:
                    valid = False

            if not valid:
                msg = (error_message or 'Invalid value for "{param}".').format(
                    param=name, value=value
                )
                _emit_error(msg, error_code)

            result = func(*args, **kwargs)
            return result  # mypy knows this is R from Callable[P, R]

        return wrapper

    return decorator


def require_not_blank(
    name: str,
    *,
    error_message: str = 'Value for "--{param}" is required.',
    error_code: Any | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Require that an argument is present, not None, and not blank/whitespace.

    Parameters
    ----------
    name
        Name of the argument to validate.
    error_message
        Error message; may use ``{param}`` and ``{value}`` placeholders.
    error_code
        Optional code for ``SugarLogs.raise_error``.

    Returns
    -------
    Callable
        Decorator enforcing the non-blank rule.
    """
    return validate_param(
        name,
        required=True,
        allow_none=False,
        allow_empty=False,
        allow_empty_collections=False,
        strip=True,
        forbidden=('',),
        predicate=None,
        error_message=error_message,
        error_code=error_code,
    )


def _emit_error(message: str, error_code: Any | None) -> NoReturn:
    """
    Emit an error via SugarLogs if available; otherwise raise ``ValueError``.

    Parameters
    ----------
    message
        Error message to report.
    error_code
        Optional code to pass to ``SugarLogs.raise_error``.

    Raises
    ------
    ValueError
        Always raised if no logger raises.
    """
    try:
        # Ensure we pass a SugarError (not Optional[Any]) to the logger.
        if error_code is None:
            default = getattr(SugarError, 'SUGAR_INVALID_PARAMETER', None)
            if default is None:
                raise ValueError(message)
            code_to_use: SugarError = cast('SugarError', default)
        else:
            code_to_use = cast('SugarError', error_code)

        SugarLogs.raise_error(message, code_to_use)
    except Exception:
        raise ValueError(message) from None

    # If the logger returns without raising, still fail explicitly.
    raise ValueError(message)
