# standard
from collections.abc import Callable
from functools import wraps
from importlib.abc import Loader
from importlib.util import (
    module_from_spec,
    spec_from_file_location,
)
from pathlib import Path
from types import ModuleType
from typing import (
    Literal,
    ParamSpec,
    TypeVar,
)

# third-party
import streamlit as st

P = ParamSpec("P")
R = TypeVar("R")

def st_cache(spinner_text: str, cache_type: Literal["data", "resource"]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Docstring for st_cache

    :param spinner_text: Description
    :type spinner_text: str
    :param cache_type: Description
    :type cache_type: Literal["data", "resource"]
    :return: Description
    :rtype: Callable[[Callable[P, R]], Callable[P, R]]
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        Docstring for decorator

        :param func: Description
        :type func: Callable[P, R]
        :return: Description
        :rtype: Callable[P, R]
        """
        if cache_type == "data":
            cached_func = st.cache_data(show_spinner=spinner_text)(func)
        else:
            cached_func = st.cache_resource(show_spinner=spinner_text)(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return cached_func(*args, **kwargs)

        return wrapper

    return decorator

@st_cache("Loading infographic object", "resource")
def load_infographic(infographic_object_file_path: Path) -> tuple[Loader | None, ModuleType | None]:
    """
    Loads an infographic object from the specified file path.
    """
    spec = spec_from_file_location(
        name=infographic_object_file_path.stem,
        location=infographic_object_file_path,
    )

    return (spec.loader, module_from_spec(spec)) if spec else (None, None)
