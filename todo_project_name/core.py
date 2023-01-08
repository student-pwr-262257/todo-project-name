#!/usr/bin/python3
from .md4 import MD4
from .md5 import MD5

"""Objects needed in many different parts of the package."""


def md4_string(message: str) -> str:
    """Returns md4 digest of given string encoded as UTF-8 byte strings.

    Parameters
    ==========
    message
    : string whose hash is to be computed.
    """
    return MD4.from_bytes(message.encode("utf-8")).string_digest()


def md5_string(message: str) -> str:
    """Returns md5 digest of given string encoded as UTF-8 byte strings.

    Parameters
    ==========
    message
    : string whose hash is to be computed.
    """
    return MD5.from_bytes(message.encode("utf-8")).string_digest()
