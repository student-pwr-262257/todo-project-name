import struct
import sys
from abc import ABC, abstractmethod

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest


class MDN(ABC):
    padding = 0x00000080.to_bytes(64, "little")  # 10000...000 -- 512 bits in total
    last32 = 0xffffffff
    last64 = 0xffffffffffffffff

    def run_algoritm(self, message_bytes):
        self.digest = None
        # preparing for the algorithm
        self.A = 0x67452301
        self.B = 0xefcdab89
        self.C = 0x98badcfe
        self.D = 0x10325476

        # running the algorithm
        # in the future it must be converted to operate on stream, in order
        # to handle hashing large files (idx variable should disappear)
        idx = 0
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
        self.digest = struct.pack("<4I", self.A, self.B, self.C, self.D)
        # done

    def string_digest(self):
        return "".join(f"{byte:02x}" for byte in self.digest)

    @staticmethod
    def _bytes_as_generator(byte_string):
        idx = 0
        str_len = len(byte_string)
        while idx + 64 <= str_len:
            yield byte_string[idx : idx + 64]
            idx += 64

        # last one might be empty, but still yield it.
        yield byte_string[idx:]

    @staticmethod
    def _file_bytes_generator(filename):
        with open(filename, "rb") as file:
            # could be optimized; reading only 64 bytes at a time is quite inefficient.
            # introducing some buffer in this function should help.
            while (chunk := file.read(64)) != b"":
                yield chunk
            yield b""  # in case of

    @classmethod
    def from_bytes(cls, byte_string: bytes):
        return cls(MDN._bytes_as_generator(byte_string))

    @classmethod
    def from_file(cls, filename: str):
        return cls(MDN._file_bytes_generator(filename))

    @staticmethod
    def l_roll(X, s):
        return ((X << s) & MDN.last32) | (X >> (32 - s))

    @abstractmethod
    def _update(self, X) -> bytes:
        raise NotImplementedError

