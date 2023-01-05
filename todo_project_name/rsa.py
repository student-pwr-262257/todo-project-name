import secrets
from typing import TypeVar
from .find_prime import find_prime
from pathlib import Path
import math
from dataclasses import dataclass
from .md4 import MD4
from .md5 import MD5

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

    Takes number `N` and returns RSAKeyPair with (2 * N)-bit modulus.
    
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

    public_key = RSAKeyPublic(e, n)
    private_key = RSAKeyPrivate(d, n)

    return RSAKeyPair(public_key, private_key)

def save_key(key: RSAKey, path: Path) -> Path:
    """Save RSA key to the file."""
    kind = key.__class__.__name__
    header = f"-----BEGIN {kind} KEY-----"
    footer = f"-----END {kind} KEY-----"
    contents = "\n".join((header, str(key.key), str(key.modulus), footer))

    path.write_text(contents, encoding="utf8")

    return path


RSAKeyVar = TypeVar("RSAKeyVar", RSAKeyPublic, RSAKeyPrivate)
def read_key(path: Path, key_type: type[RSAKeyVar]) -> RSAKeyVar:
    """Read RSA key from the file."""
    with path.open("r", encoding="utf8") as file:
        file.readline()
        key = file.readline()
        modulus = file.readline()

    return key_type(key=int(key), modulus=int(modulus))

def rsa_sign(message: str, key: RSAKeyPrivate, algorithm: str ='MD4') -> str:
    """
    Function returns a digital singnature based on the RSA protocol.
    
    Parameters
    ==========
    message
    : string message to be singed
    
    key
    : RSA private key

    algorithm
    : string to specify the hashing algorithm. 
    Available algorithms: MD4, MD5
    """
    if algorithm == "MD5":
        hashed = MD5.from_bytes(message.encode('utf-8')).string_digest()
    else:
        hashed = MD4.from_bytes(message.encode('utf-8')).string_digest()
    hashed = int(hashed,16)
    signature = pow(hashed, key.key, key.modulus)
    return hex(signature)

def rsa_verify(message: str, signature: str, key: RSAKeyPublic, algorithm: str ='MD4'):
    """
    Function verifies digital singnature of a message basing on the RSA protocol.
    It compares decoded signature with hashed message 
    and returns True if they are the same, otherwise False.
    
    Parameters
    ==========
    message
    : string message 

    signature
    : signature for verification
    
    key
    : RSA public key

    algorithm
    : string to specify the hashing algorithm. 
    Available algorithms: MD4, MD5
    
    """
    if algorithm == "MD5":
        hashed=MD5.from_bytes(message.encode('utf-8')).string_digest()
    else:
        hashed = MD4.from_bytes(message.encode('utf-8')).string_digest()
    hashed = int(hashed,16)
    uncoded = pow(int(signature,16), key.key, key.modulus)
    if hashed == uncoded:
        return True
    return False
