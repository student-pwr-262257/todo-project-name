import secrets
from find_prime import find_prime
from core import extended_euclid

def euclid(a:int,b:int)->int:
    """
    Function implements Euclid algorithm.
    Given integers a, b returns GCD(a,b).
    """
    while b:
        a,b=b,a%b
    return a

def rsa_key_gen(N:int)->tuple:
    """
    Generation of RSA protocol keys. 

    Takes number `N` and returns tuple (public key, private key).
    Public key is in the form of (n, e) 
    and private one is in the form of (n, d), where n is a 2*N-bit modulus.
    
    Notes
    =====
    Argument `N` determines the strength of the protocol.
    """
    p,q=find_prime(N),find_prime(N)
    n=p*q
    phi=(p-1)*(q-1)
    d=phi
    while euclid(phi,d)!=1:
        d=secrets.randbelow(phi)
    e=extended_euclid(phi,d)[1] #because phi*r+d*e==1 for some integers r,e
    if e<0:
        e=n+e
    return ((n,e),(n,d))

