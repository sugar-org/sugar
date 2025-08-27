"""Validation functions."""

from __future__ import annotations

import functools
import inspect

from collections.abc import Collection
from typing import Any, Callable, Iterable, Optional, ParamSpec, TypeVar

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
    predicate: Optional[Callable[[Any], bool]] = None,
    error_message: Optional[str] = None,
    error_code: Any | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Validate a single function argument before executing the function.

    Parameters
    ----------
    name
        Name of the argument to validate.
    required
        If True, the argument must be present after defaults are applied.
    allow_none
        If False, ``None`` is considered invalid.
    allow_empty
        If False, empty strings (after optional `strip`) are invalid.
    allow_empty_collections
        If False, empty collections (list/tuple/dict/set) are invalid.
    strip
        If True and the value is a string, whitespace is stripped before
        checks.
    forbidden
        Literal values that are disallowed (checked after optional `strip`).
    predicate
        Custom predicate; if provided it must return True for valid values.
    error_message
        Custom error message. Placeholders ``{param}`` and ``{value}`` are
        allowed.
    error_code
        Optional code passed to ``SugarLogs.raise_error``. If omitted, tries
        ``SugarError.SUGAR_INVALID_PARAMETER`` if available.

    Returns
    -------
    Callable
        A decorator that enforces the validation and aborts on failure.

    Raises
    ------
    ValueError
        Raised if validation fails and ``SugarLogs``/``SugarError`` are
        unavailable.
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
                    if not predicate(value):
                        valid = False
                except Exception:
                    valid = False

            if not valid:
                msg = (error_message or 'Invalid value for "{param}".').format(
                    param=name, value=value
                )
                _emit_error(msg, error_code)

            return func(*args, **kwargs)

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
        Error message. Placeholders ``{param}`` and ``{value}`` are allowed.
    error_code
        Optional code for ``SugarLogs.raise_error``.

    Returns
    -------
    Callable
        A decorator enforcing the non-blank rule.
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


def _emit_error(message: str, error_code: Any | None) -> None:
    """
    Dispatch an error via SugarLogs if available, else raise ValueError.

    Parameters
    ----------
    message
        Error message to report.
    error_code
        Error code to pass to SugarLogs, if available.

    Raises
    ------
    ValueError
        Always raised if SugarLogs is unavailable or does not raise.
    """
    try:
        # Resolve a default code lazily if none was provided.
        if error_code is None:
            try:
                code = getattr(SugarError, 'SUGAR_INVALID_PARAMETER')  # type: ignore[name-defined]
            except Exception:
                code = None
        else:
            code = error_code
        SugarLogs.raise_error(message, code)  # type: ignore[name-defined]
    except NameError:
        raise ValueError(message) from None
    # If SugarLogs didn't raise, still fail here.
    raise ValueError(message)
