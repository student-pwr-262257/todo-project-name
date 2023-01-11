from __future__ import annotations
import struct
from abc import ABC, abstractmethod
from typing import Iterator, List

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest


class MDN(ABC):
    """Superclass of MD4 and MD5. Works for little-endian architecture."""

    padding = 0x80.to_bytes(64, "little")  # 10000...000 -- 512 bits in total
    last32 = 0xffffffff
    last64 = 0xffffffffffffffff


    def __init__(self, message_bytes: Iterator[bytes]):
        """All derived classes should have constructor with this signature.

        Parameters
        ==========
        message_bytes
        : Iterator yielding `bytes` of length exactly 64. Last yielded
        byte string must have length strictly less than 64 (empty byte string
        may be sometimes necessary). Class computes message digest of these bytes
        as if they were just single byte string.
        """
        self._A = self._B = self._C = self._D = 0
        self.__digest = b""
        self._run_algoritm(message_bytes)

    def _run_algoritm(self, message_bytes: Iterator[bytes]) -> None:
        """Common structure of md4 and md5 algorithms.

        Parameters
        ==========
        message_bytes
        : Iterator yielding `bytes` of length exactly 64. Last yielded
        byte string must have length strictly less than 64 (empty byte string
        may be sometimes necessary).

        Notes
        =====
        This function uses `_update` method, which should be implemented by
        derived classes.
        """
        # preparing for the algorithm
        self._A = 0x67452301
        self._B = 0xefcdab89
        self._C = 0x98badcfe
        self._D = 0x10325476

        # running the algorithm
        bits_no = 0

        while len(chunk := next(message_bytes)) == 64:
            X = list(struct.unpack("<16I", chunk))  # 16 unsigned integers
            self._update(X)
            bits_no += 512

        # padding and running last iteration (or 2 in the case of empty padding or over 56 bytes left)
        message = chunk  # remaining bytes
        left = len(chunk)
        # b == 8 * left
        # bits to append: 448 - b (mod 512)
        # bytes to append: 56 - left (mod 64)
        add = (56 - left) % 64
        if add == 0:
            add = 64
        message += MDN.padding[:add]
        bits_no += left * 8

        if left + add > 64:  # can be only 56 or 120
            X = list(struct.unpack("<16I", message[:64]))
            self._update(X)
            message = message[64:]  # only 1 unprocessed pack of 16 words

        # appending number of bits
        message += struct.pack(
            "<Q", bits_no & MDN.last64
        )  # Q: unsigned long long (8 bytes)
        X = list(struct.unpack("<16I", message))
        self._update(X)

        # getting the result
        self.__digest = struct.pack("<4I", self._A, self._B, self._C, self._D)
        # done

    def string_digest(self) -> str:
        """Returns string representation of message digest."""
        return "".join(f"{byte:02x}" for byte in self.__digest)

    @property
    def digest(self):
        """The message digest as bytes."""
        return self.__digest

    @staticmethod
    def _bytes_as_generator(byte_string: bytes) -> Iterator[bytes]:
        """Convert `bytes` to generator yielding `bytes` of length 64.
        Last byte string has length strictly less than 64 (may be 0).

        Parameters
        ==========
        byte_string
        : sequence of bytes to be converted to iterator.
        """
        # Works similarly to itertools.batched, but ensures that last returned
        # element has length strictly smaller than 64, which serves as break condition.
        idx = 0
        str_len = len(byte_string)
        while idx + 64 <= str_len:
            yield byte_string[idx : idx + 64]
            idx += 64

        # last one might be empty, but still yield it.
        yield byte_string[idx:]

    @staticmethod
    def _file_bytes_generator(
        filename: str, *, page_size: int = 4096
    ) -> Iterator[bytes]:
        """Create generator yielding pieces of file as `bytes` of length 64.
        Last byte string has length strictly less than 64 (may be 0).

        Parameters
        ==========
        filename
        : path to existing file from which bytes will be read.

        page_size
        : number of bytes read from file at once. Must be positive. This is optimization
        parameter - regardless of its value, created generator always yields byte strings
        of length exactly 64, and last one strictly less than 64. Default value is 4096 (4KiB).
        """
        # Works similarly to itertools.batched, but ensures that last returned
        # element has length strictly smaller than 64, which serves as break condition.
        with open(filename, "rb") as file:
            # reading 4KiB at once is much more efficient than 64 bytes.
            while (buff := file.read(page_size)) != b"":
                if len(buff) < page_size:  # end of file
                    yield from MDN._bytes_as_generator(buff)
                    return

                # Full 4 KiB to divide into chunks
                for idx in range(0, page_size, 64):
                    yield buff[idx : idx + 64]

            yield b""  # in case of file size being divisible by 4 KiB

    @classmethod
    def from_bytes(cls, byte_string: bytes) -> MDN:
        """This function serves as constructor, which allows to compute hash
        of `bytes`.

        Parameters
        ==========
        byte_string
        : message whose digest is to be computed.
        """
        return cls(MDN._bytes_as_generator(byte_string))

    @classmethod
    def from_file(cls, filename: str) -> MDN:
        """This function serves as constructor, which allows to compute hash
        of file under given path.

        Parameters
        ==========
        filename
        : path to existing file whose digest is to be computed.
        """
        return cls(MDN._file_bytes_generator(filename))

    @staticmethod
    def l_roll(X: int, s: int) -> int:
        """Roll (rotate) bits of 32-bit unsigned integer `s` positions
        to the left.

        Parameters
        ==========
        X: integer to be rolled. Its binary representation cannot exceed 32 bits.

        s: number of digits to roll. Must be integer in [0, 32].
        """
        return ((X << s) & MDN.last32) | (X >> (32 - s))

    @abstractmethod
    def _update(self, X: List[int]) -> None:
        """This method should update internal registers according to MD* specification.
        It should do all of the "processing of single 16-word block" from the paper.

        Parameters
        ==========
        X: list of 16 32-bit unsigned integers to be processed.
        """
        raise NotImplementedError("Derived class should implement this method.")
