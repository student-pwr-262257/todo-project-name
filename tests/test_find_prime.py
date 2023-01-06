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

    @given(st.integers(max_value=1))
    def test_on_definite_false(self, candidate):
        actual = find_prime.is_probable_prime(candidate)
        expected = False
        assert actual == expected


class TestFindPrime:
    # We are required to generate 128-bit keys, this should be enough.
    # TODO: Check thoroughly when ePortal is working.
    @given(st.integers(min_value=2, max_value=129))
    def test_if_is_probable_prime(self, n_bits):
        found = find_prime.find_prime(n_bits)
        assert sp.isprime(found)

    @given(st.integers(min_value=2, max_value=129))
    def test_if_has_correct_number_of_bits(self, n_bits):
        found = find_prime.find_prime(n_bits)
        assert found.bit_length() == n_bits

    @given(st.integers(max_value=1))
    def test_on_invalid(self, n_bits):
        with pytest.raises(ValueError):
            find_prime.find_prime(n_bits)


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
