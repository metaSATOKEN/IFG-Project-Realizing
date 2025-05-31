import pytest
import importlib.util

# Determine availability of NumPy for optional tests
HAS_NUMPY = importlib.util.find_spec("numpy") is not None

