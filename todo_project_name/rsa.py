import secrets
from .find_prime import find_prime
from pathlib import Path
import math
from dataclasses import dataclass


@dataclass
class RSAKey:
    key: int
    modulus: int


@dataclass
class RSAKeyPublic(RSAKey):
    pass


@dataclass
class RSAKeyPrivate(RSAKey):
    pass


@dataclass
class RSAKeyPair:
    public: RSAKeyPublic
    private: RSAKeyPrivate


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
    while math.gcd(phi,d)!=1:
        d=secrets.randbelow(phi)
    e=pow(d,-1,phi)
    if e<0:
        e=n+e
    return ((n,e),(n,d))

def save_key(key: RSAKey, path: Path) -> Path:
    """Save RSA key to the file."""
    pass  # TODO: IMplement.
    return path


def read_key(path: Path) -> RSAKey:
    """Read RSA key from the file."""
    pass  # TODO: Implement.
