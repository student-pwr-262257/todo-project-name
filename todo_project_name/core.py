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
    n=len(bits)
    b=b%m
    tmp=b
    result=1
    for i in range(n-1,-1,-1):
        if bits[i]=='1':
            result=(result*tmp)%m
        tmp=(tmp*tmp)%m
    return result


def extended_euclid(a:int,b:int)->tuple:
    """
    Function implements extended Euclid algorithm. 
    Given integers a, b returns integers x, y, such that x*a+y*b==GCD(a,b).
    """
    x,y,s,t = 0,1,1,0
    while a != 0:
        q,r = b//a,b%a
        m,n = x-s*q,y-t*q
        b,a,x,y,s,t = a,r,s,t,m,n
    return x,y