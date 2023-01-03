#!/usr/bin/python3

"""Objects needed in many different parts of the package."""

def extended_euclid(a: int, b: int, /) -> tuple[int, int]:
    """Return integers x and y, such that x * a + y * b == gcd(a, b).

    Parameters
    ==========
    a, b
    : not all equal to 0

    Notes
    =====
    This function uses extended Euclidean algorithm.
    """
    if a == 0 and b == 0:
        raise ValueError("Greatest common divisor is not defined if all arguments equal 0.")

    x,y,s,t = 0,1,1,0
    while a != 0:
        q,r = b//a,b%a
        m,n = x-s*q,y-t*q
        b,a,x,y,s,t = a,r,s,t,m,n
    return x,y