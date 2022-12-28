#!/usr/bin/python3

"""Objects needed in many different parts of the package."""

def mod_exp(b:int, e:int, m:int)->int:
    """
    Function that performs fast modular exponentiation with given 
    -b -- base,
    -e -- exponent,
    -m -- modulus.
    """
    bits=bin(e)[2:]
    b=b%m
    tmp=b
    result=1
    for i in range(len(bits)):
        if bits[len(bits)-1-i]=='1':
            result=(result*tmp)%m
        tmp=(tmp*tmp)%m
    return result