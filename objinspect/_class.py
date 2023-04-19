import functools
import inspect
from typing import Any

import docstring_parser

from objinspect.function import _get_docstr_desc, _has_docstr
from objinspect.method import Method, MethodFilter


class Class:

    """
    Class for wrapping a class or class instance and providing information about its methods.

    Args:
        cls (type or object): The class or class instance to wrap.
        init (bool, optional): Include the class's __init__ method. Defaults to True.
        public (bool, optional): Include public methods. Defaults to True.
        inherited (bool, optional): Include inherited methods. Defaults to True.
        static_methods (bool, optional): Include static methods. Defaults to True.
        protected (bool, optional): Include protected methods. Defaults to False.
        private (bool, optional): Include private methods. Defaults to False.

    Attributes:
        cls (type or object): The class or class instance that was passed as an argument.
        is_initialized (bool): Whether the class has been initialized as an instance.
        name (str): The name of the class.
        instance (object | None): The instance of the class if it has been initialized, otherwise None.
        docstring (str | None): The docstring of the class if it exists, otherwise None.
        has_docstring (bool): Whether the class has a docstring.
        extractor_kwargs (dict): The keyword arguments used to initialize the MethodExtractor object.
        has_init (bool): Whether the class has an __init__ method.
        description (str): The description of the class from its docstring.
    """

    def __init__(
        self,
        cls,
        init=True,
        public=True,
        inherited=True,
        static_methods=True,
        protected=False,
        private=False,
    ) -> None:
        self.cls = cls
        self.is_initialized = False
        try:
            self.name: str = self.cls.__name__
        except AttributeError:
            self.name = f"{self.cls.__class__.__name__} instance"
            self.is_initialized = True
        self.instance = None if not self.is_initialized else self.cls
        self.docstring = inspect.getdoc(self.cls)
        self.has_docstring = _has_docstr(self.docstring)
        self.extractor_kwargs = {
            "init": init,
            "public": public,
            "inherited": inherited,
            "static_methods": static_methods,
            "protected": protected,
            "private": private,
        }
        self._methods = self._find_methods()
        self.has_init = "__init__" in self._methods
        self._parsed_docstring = (
            docstring_parser.parse(self.docstring) if self.has_docstring else None  # type: ignore
        )
        self.description = _get_docstr_desc(self._parsed_docstring)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', methods={len(self._methods)}, has_init={self.has_init}, description={self.description})"

    @functools.cached_property
    def _get_class_base(self):
        if self.is_initialized:
            return self.cls.__class__
        return self.cls

    def _find_methods(self):
        method_filter = MethodFilter(**self.extractor_kwargs)
        members = inspect.getmembers(self.cls, inspect.isfunction)
        methods = {}
        for i in method_filter.extract([Method(i[1], self._get_class_base) for i in members]):
            methods[i.name] = i
        return methods

    def init(self, *args, **kwargs) -> None:
        """
        Initializes the class as an instance using the provided arguments.

        Raises:
            ValueError: If the class is already initialized.

        """
        if self.is_initialized:
            raise ValueError(f"Class {self.cls} is already initialized")
        self.instance = self.cls(*args, **kwargs)
        self.is_initialized = True

    def call_method(self, method: str | int, *args, **kwargs) -> Any:
        """
        Calls the specified method on the class or instance.

        Args:
            method (str | int): The name or index of the method to call.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.

        Returns:
            Any: The result of calling the specified method.

        Raises:
            ValueError: If the class has not been initialized.
        """
        method_obj = self.get_method(method)
        if not self.is_initialized and not method_obj.is_static:
            raise ValueError(f"Class {self.cls} is not initialized")
        return method_obj.call(self.instance, *args, **kwargs)

    def get_method(self, method: str | int) -> Method:
        """
        Retrieves a method from the list of methods of the class or instance.

        Args:
            method (str | int): The method name or index to retrieve.

        Returns:
            Method: The :class:`Method` object representing the requested method.
        """
        match method:
            case str():
                return self._methods[method]
            case int():
                return self.methods[method]
            case _:
                raise TypeError(type(method))

    @property
    def methods(self) -> list[Method]:
        """
        Returns the list of methods of the class or instance as a list of :class:`Function` objects.
        """
        return list(self._methods.values())

    @property
    def dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "methods": [i.dict for i in self.methods],
            "description": self.description,
            "initialized": self.is_initialized,
            "docstring": self.docstring,
        }


__all__ = ["Class"]
