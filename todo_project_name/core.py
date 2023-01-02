#!/usr/bin/python3

"""Objects needed in many different parts of the package."""

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