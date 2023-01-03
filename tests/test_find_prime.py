#!/usr/bin/python3

# First-party
from todo_project_name import find_prime

# Third-party
import pytest
from hypothesis import HealthCheck, given, assume, strategies as st, settings
import sympy as sp


class TestIsProbablePrime:
    # Primes generation is inherently slow.
    @settings(suppress_health_check=HealthCheck.all())
    @given(st.integers())
    def test_on_prime(self, candidate):
        assume(sp.isprime(candidate))
        actual = find_prime.is_probable_prime(candidate)
        expected = True
        assert actual == expected, "Primes have to pass the test."


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
