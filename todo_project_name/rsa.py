import secrets
from typing import Any, TypeVar, Union, Type, Optional
from .find_prime import find_prime
from pathlib import Path
import math
from dataclasses import dataclass
from .md4 import MD4
from .md5 import MD5
from abc import ABC


class RSAKey(ABC):
    def __init__(
        self, key: int, modulus: int, id: Optional[str] = None
    ) -> None:
        """Create a new instance.

        Parameters
        ==========
        id:
            cannot have white space at its ends or be an empty string.
        """
        if id is not None:
            if id == "":
                raise ValueError("The string cannot be empty.")
            if id != id.strip():
                # TODO: Consider lifting this constraint with a more flexible
                # serialization. Is it needed?
                raise ValueError("`id` cannot have white space at its ends.")

        self.key = key
        self.modulus = modulus
        self.id = id

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(key={self.key!r}, modulus={self.modulus!r}, id={self.id!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, RSAKey):
            return NotImplemented
        if not isinstance(other, type(self)):
            return False
        return self.key == other.key and self.modulus == other.modulus


class RSAKeyPublic(RSAKey):
    pass


class RSAKeyPrivate(RSAKey):
    pass


@dataclass
class RSAKeyPair:
    public: RSAKeyPublic
    private: RSAKeyPrivate


def rsa_key_gen(N: int) -> RSAKeyPair:
    """Generate RSA key pair.

    Takes number `N` and returns RSAKeyPair with (2 * N)-bit modulus.

    Parameters
    ==========
    `N`
    : determines the strength of the protocol.
    """
    p, q = find_prime(N), find_prime(N)
    while p == q:  # make sure that p!=q
        q = find_prime(N)
    n = p * q
    phi = (p - 1) * (q - 1)
    d = phi
    while math.gcd(phi, d) != 1:
        d = secrets.randbelow(phi - 2) + 2  # rand d in range 2, 3,..., phi-1
    e = pow(d, -1, phi)

    public_key = RSAKeyPublic(e, n)
    private_key = RSAKeyPrivate(d, n)

    return RSAKeyPair(public_key, private_key)


def save_key(key: RSAKey, path: Path) -> Path:
    """Save RSA key to the file."""
    kind = key.__class__.__name__
    header = f"-----BEGIN {kind} KEY-----"
    footer = f"-----END {kind} KEY-----"
    # TODO: Consider serialization method allowing white space in `RSAKey.id`. Is
    # it needed?
    contents = "\n".join(
        (header, str(key.key), str(key.modulus), str(key.id), footer)
    )

    path.write_text(contents, encoding="utf8")

    return path


RSAKeyVar = TypeVar("RSAKeyVar", RSAKeyPublic, RSAKeyPrivate)


def read_key(path: Path, key_type: Type[RSAKeyVar]) -> RSAKeyVar:
    """Read RSA key from the file."""
    with path.open("r", encoding="utf8") as file:
        # Skip the heading.
        file.readline()
        key = file.readline().strip()
        modulus = file.readline().strip()
        id = file.readline().strip()

    return key_type(
        key=int(key),
        modulus=int(modulus),
        id=str(id) if id != "None" else None,
    )


def rsa_sign(
    message: str, key: RSAKeyPrivate, algorithm: Type[Union[MD4, MD5]] = MD4
) -> str:
    """
    Function returns a digital singnature based on the RSA protocol.

    Parameters
    ==========
    message
    : string message to be singed

    key
    : RSA private key

    algorithm
    : hash method. Default: MD4.
    Available algorithms: MD4, MD5.
    """
    hashed: Any = algorithm.from_bytes(message.encode("utf-8")).string_digest()
    hashed = int(hashed, 16)
    signature = pow(hashed, key.key, key.modulus)
    return hex(signature)[2:]


def rsa_sign_file(
    filename: str, key: RSAKeyPrivate, algorithm: Type[Union[MD4, MD5]] = MD4
) -> str:
    """
    Function returns a digital singnature based on the RSA protocol.

    Parameters
    ==========
    filename
    : path to existing file to sign

    key
    : RSA private key

    algorithm
    : hash method. Default: MD4.
    Available algorithms: MD4, MD5.
    """
    hashed: Any = algorithm.from_file(filename).string_digest()
    hashed = int(hashed, 16)
    signature = pow(hashed, key.key, key.modulus)
    return hex(signature)[2:]


def rsa_verify(
    message: str,
    signature: str,
    key: RSAKeyPublic,
    algorithm: Type[Union[MD4, MD5]] = MD4,
):
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
    : hash algorithm. Default: MD4.
    Available algorithms: MD4, MD5.

    """
    hashed: Any = algorithm.from_bytes(message.encode("utf-8")).string_digest()
    hashed = int(hashed, 16) % key.modulus
    uncoded = pow(int(signature, 16), key.key, key.modulus)
    if hashed == uncoded:
        return True
    return False


def rsa_verify_file(
    filename: str,
    signature: str,
    key: RSAKeyPublic,
    algorithm: Type[Union[MD4, MD5]] = MD4,
):
    """
    Function verifies digital singnature of a message basing on the RSA protocol.
    It compares decoded signature with hashed message
    and returns True if they are the same, otherwise False.

    Parameters
    ==========
    filename
    : path to file against which signature is being checked

    signature
    : signature for verification

    key
    : RSA public key

    algorithm
    : hash algorithm. Default: MD4.
    Available algorithms: MD4, MD5.

    """
    hashed: Any = algorithm.from_file(filename).string_digest()
    hashed = int(hashed, 16) % key.modulus
    uncoded = pow(int(signature, 16), key.key, key.modulus)
    if hashed == uncoded:
        return True
    return False
