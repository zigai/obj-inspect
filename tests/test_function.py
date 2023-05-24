import pytest

from objinspect.constants import EMPTY
from objinspect.function import Function


def example_function(a, b=None, c=4) -> int:
    """
    example_function dostring

    Args:
        a: Argument a
        b (optional): Argument b. Defaults to None.
        c (int, optional): Argument c. Defaults to 4.
    """
    return c * 2


func = Function(example_function)


def test_params_len():
    assert len(func._parameters) == 3


def test_getitem():
    assert func.get_param(0).name == "a"
    assert func.get_param(1).name == "b"
    assert func.get_param(2).name == "c"
    assert func.get_param("a").name == "a"
    assert func.get_param("b").name == "b"
    assert func.get_param("c").name == "c"
    assert func.return_type is int
    with pytest.raises(IndexError):
        func.get_param(3)
    with pytest.raises(TypeError):
        func.get_param(3.3)
    with pytest.raises(KeyError):
        func.get_param("d")


def test_type_inference():
    assert func.get_param("a").type is EMPTY
    assert func.get_param("b").type is type(None)
    assert func.get_param("c").type is int


def test_descriptions():
    assert func.has_docstring == True
    assert func.description == "example_function dostring"
    assert func.get_param("a").description == "Argument a"
    assert func.get_param("b").description == "Argument b. Defaults to None."
    assert func.get_param("c").description == "Argument c. Defaults to 4."


def test_is_param_typed():
    assert func.get_param("a").is_typed == False
    assert func.get_param("b").is_typed == True
    assert func.get_param("c").is_typed == True


def test_is_param_optional():
    assert func.get_param("a").is_optional == False
    assert func.get_param("b").is_optional == True
    assert func.get_param("c").is_optional == True


def test_call():
    from math import pow

    assert Function(pow).call(2, 2) == 4
