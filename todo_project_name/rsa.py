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

def rsa_key_gen(N: int) -> RSAKeyPair:
    """Generate RSA key pair.

    Takes number `N` and RSAKeyPair with (2 * N)-bit modulus.
    
    Parameters
    ==========
    `N`
    : determines the strength of the protocol.
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

    public_key = RSAKeyPublic(e, n)
    private_key = RSAKeyPrivate(d, n)

    return RSAKeyPair(public_key, private_key)

def save_key(key: RSAKey, path: Path) -> Path:
    """Save RSA key to the file."""
    pass  # TODO: IMplement.
    return path


def read_key(path: Path) -> RSAKey:
    """Read RSA key from the file."""
    pass  # TODO: Implement.
