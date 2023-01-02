#!/usr/bin/python3

# Built-in
import math

# First-party
from todo_project_name import core

# Third-party
import pytest
from hypothesis import given, strategies as st


@given(st.integers(), st.integers())
def test_extended_euclid(a, b):
    x, y = core.extended_euclid(a, b)
    assert x * a + y * b == math.gcd(a, b)


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
