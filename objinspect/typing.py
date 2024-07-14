import types
import typing
import typing as T
from collections.abc import Iterable, Mapping
from enum import EnumMeta

import typing_extensions

from objinspect.constants import EMPTY

ALIAS_TYPES = [typing._GenericAlias, types.GenericAlias]  # type:ignore
UNION_TYPES = [typing._UnionGenericAlias, types.UnionType]  # type:ignore


def type_name(t: T.Any) -> str:
    """
    Convert a Python type to its string representation (without the module name).

    Args:
        t (Any): A Python type.

    Returns:
        str: The string representation of the Python type.

    Example:
        >>> type_to_str(datetime.datetime)
        'datetime'
        >>> type_to_str(int)
        'int'
    """
    type_str = repr(t)
    if "<class '" in type_str:
        type_str = type_str.split("'")[1]
    return type_str.split(".")[-1]


def is_generic_alias(t) -> bool:
    """
    Check if a type is an alias type (list[str], dict[str, int], etc...])

    Example:
    >>> is_generic_alias(list[str])
    True
    >>> is_generic_alias(int)
    False
    >>> String = str
    >>> is_generic_alias(String)
    False
    """
    return type(t) in ALIAS_TYPES


def is_union_type(t) -> bool:
    """
    Check if a type is a union type (float | int, str | None, etc...)

    Examples:
    >>> is_union_type(int | str)
    True
    >>> from typing import Union
    >>> is_union_type(Union[int, str])
    True
    >>> is_union_type(list)
    False
    """
    return type(t) in UNION_TYPES


def is_iterable_type(t) -> bool:
    """
    Check if a type is an iterable type (list, tuple, etc...)

    Examples:
        >>> is_iterable_type(list)
        True
        >>> is_iterable_type(dict)
        True
        >>> is_iterable_type(int)
        False
        >>> is_iterable_type(typing.List)
        True
        >>> is_iterable_type(typing.Dict)
        True
    """
    typing_iterables = [
        typing.List,
        typing.Tuple,
        typing.Dict,
        typing.Set,
        typing.FrozenSet,
        typing.Deque,
        typing.DefaultDict,
        typing.OrderedDict,
        typing.ChainMap,
        typing.Counter,
        typing.Generator,
        typing.AsyncGenerator,
        typing.Iterable,
        typing.Collection,
        typing.AbstractSet,
        typing.MutableSet,
        typing.Mapping,
        typing.MutableMapping,
        typing.Sequence,
        typing.MutableSequence,
    ]
    if isinstance(t, (types.GenericAlias, typing._GenericAlias)):  # type:ignore
        t = t.__origin__
    if t in typing_iterables:
        return True
    return issubclass(t, Iterable)


def is_mapping_type(t) -> bool:
    """
    Check if a type is a mapping type (dict, OrderedDict, etc...)

    Examples:
        >>> is_mapping_type(dict)
        True
        >>> is_mapping_type(list)
        False
        >>> is_mapping_type(typing.Dict)
        True
        >>> is_mapping_type(typing.OrderedDict)
        True
    """
    typing_mappings = [
        typing.Dict,
        typing.Mapping,
        typing.MutableMapping,
        typing.DefaultDict,
        typing.OrderedDict,
        typing.ChainMap,
    ]
    if isinstance(t, (types.GenericAlias, typing._GenericAlias)):  # type:ignore
        t = t.__origin__
    if t in typing_mappings:
        return True
    return issubclass(t, Mapping)


def type_simplified(t: T.Any) -> T.Any | tuple[T.Any, ...]:
    """
    Examples:
    >>> type_simplify(list[str])
    <class 'list'>
    >>> type_simplify(float | list[str])
    (<class 'float'>, <class 'list'>)
    """
    origin = type_origin(t)
    if isinstance(type(origin), types.NoneType) or origin is None:
        return t

    if is_union_type(t):
        args = type_args(t)
        return tuple([type_simplified(i) for i in args])

    return origin


def is_enum(t: T.Any) -> bool:
    return isinstance(t, EnumMeta)


def get_enum_choices(e) -> tuple[str, ...]:
    """
    Get the options of a Python Enum.

    Args:
        e (enum.Enum): A Python Enum.

    Returns:
        tuple: A tuple of the names of the Enum options.

    Example:
        >>> import enum
        >>> class Color(enum.Enum):
        ...     RED = 1
        ...     GREEN = 2
        ...     BLUE = 3
        >>> get_enum_choices(Color)
        ('RED', 'GREEN', 'BLUE')
    """
    if not is_enum(e):
        raise TypeError(f"'{e}' is not an Enum")
    return tuple(e.__members__.keys())


def is_direct_literal(t: T.Any) -> bool:
    """
    Determine if the given type is a 'pure' Literal type.
    It checks if the input type is a direct instance of Literal,not including the Literal class itself.
    This function distinguishes between the 'Literal' class itself and instantiated Literal types. It returns True only for the latter.

    Args:
        t (Any): The type to check.

    Returns:
        bool: True if the type is a pure Literal, False otherwise.

    Examples:
        >>> from typing_extensions import Literal
        >>> is_direct_literal(Literal[1, 2, 3])
        True
        >>> is_direct_literal(Literal)
        False
        >>> is_direct_literal(int)
        False
        >>> is_direct_literal(Union[str, Literal[1, 2]])
        False
    """
    if t is typing_extensions.Literal:
        return False
    if hasattr(t, "__origin__") and t.__origin__ is typing_extensions.Literal:
        return True
    return False


def is_or_contains_literal(t: T.Any) -> bool:
    """
    Determine if the given type is a Literal type or contains a Literal type.

    Examples:
    >>> from typing import Union, Optional
    >>> from typing_extensions import Literal
    >>> is_or_contains_literal(Literal[1, 2, 3])
    True
    >>> is_or_contains_literal(Union[int, Literal[1, 2]])
    True
    >>> is_or_contains_literal(Optional[Literal['a', 'b']])
    True
    >>> is_or_contains_literal(int)
    False
    """
    if is_direct_literal(t):
        return True

    for i in T.get_args(t):
        if is_or_contains_literal(i):
            return True
    return False


def get_literal_choices(literal_t) -> tuple[str, ...]:
    """
    Get the options of a Python Literal.
    """
    if is_direct_literal(literal_t):
        return T.get_args(literal_t)
    for i in T.get_args(literal_t):
        if is_direct_literal(i):
            return T.get_args(i)
    raise ValueError(f"{literal_t} is not a literal")


def literal_contains(literal_t, value: T.Any) -> bool:
    """
    Check if a value is in a Python Literal.
    """
    if not is_direct_literal(literal_t):
        raise ValueError(f"{literal_t} is not a literal")

    values = get_literal_choices(literal_t)
    if not len(values):
        raise ValueError(f"{literal_t} has no values")
    return value in values


def type_origin(t: T.Any) -> T.Any:
    """
    A wrapper for typing.get_origin to get the origin of a type.

    Example:
        >>> type_args(list[list[str]])
        <class 'list'>
        >>> type_origin(float | int)
        <class 'types.UnionType'>
    """
    return typing.get_origin(t)


def type_args(t: T.Any) -> tuple[T.Any, ...]:
    """
    A wrapper for typing.get_args to get the arguments of a type.

    Example:
        >>> type_args(list[str])
        (<class 'str'>,)
        >>> type_args(dict[str, int])
        (<class 'str'>, <class 'int'>)
        >>> type_args(list[list[str]])
        (list[str],)
    """
    return typing.get_args(t)


__all__ = [
    "type_name",
    "is_generic_alias",
    "is_union_type",
    "is_iterable_type",
    "is_mapping_type",
    "type_simplified",
    "is_enum",
    "get_enum_choices",
    "is_direct_literal",
    "is_or_contains_literal",
    "get_literal_choices",
    "literal_contains",
    "type_origin",
    "type_args",
]
