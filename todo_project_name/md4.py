import struct
import sys

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest


class MD4:
    # magic constants (high-order digits given first == big endian)
    ROUND_2 = 0x5A827999
    ROUND_3 = 0x6ED9EBA1

    padding = 0x00000080.to_bytes(64, "little")  # 10000...000 -- 512 bits in total
    last32 = 0xffffffff
    last64 = 0xffffffffffffffff

    def __init__(self, message_bytes):
        self.digest = None
        # preparing for the algorithm
        if sys.byteorder == "little":
            self.A = 0x67452301
            self.B = 0xefcdab89
            self.C = 0x98badcfe
            self.D = 0x10325476
        else:  # sys.byteorder == "big"
            self.A = 0x01234567
            self.B = 0x89abcdef
            self.C = 0xfedcba98
            self.D = 0x76543210
        # TODO: do we have to invert byte order in message on big endian?

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
        message += MD4.padding[:add]
        bits_no += left * 8

        if left + add > 64:  # can be only 56 or 120
            X = list(struct.unpack("<16I", message[:64]))
            self._update(X)
            message = message[64:]  # only 1 unprocessed pack of 16 words

        # appending number of bits
        message += struct.pack(
            "<Q", bits_no & MD4.last64
        )  # Q: unsigned long long (8 bytes)
        print(f"{len(message) = }")
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

    @staticmethod
    def from_bytes(byte_string: bytes):
        return MD4(MD4._bytes_as_generator(byte_string))

    @staticmethod
    def from_file(filename: str):
        return MD4(MD4._file_bytes_generator(filename))

    # bitwise conditional
    @staticmethod
    def f(X, Y, Z):
        return (X & Y) | ((~X) & Z)

    # bitwise majority function
    @staticmethod
    def g(X, Y, Z):
        return (X & Y) | (X & Z) | (Y & Z)

    # bitwise XOR for 3 inputs (parity function)
    @staticmethod
    def h(X, Y, Z):
        return X ^ Y ^ Z

    @staticmethod
    def l_roll(X, s):
        return ((X << s) & MD4.last32) | (X >> (32 - s))

    @staticmethod
    def round_1_op(A, B, C, D, X, s):
        return MD4.l_roll((A + MD4.f(B, C, D) + X) & MD4.last32, s)

    @staticmethod
    def round_2_op(A, B, C, D, X, s):
        return MD4.l_roll((A + MD4.g(B, C, D) + X + MD4.ROUND_2) & MD4.last32, s)

    @staticmethod
    def round_3_op(A, B, C, D, X, s):
        return MD4.l_roll((A + MD4.h(B, C, D) + X + MD4.ROUND_3) & MD4.last32, s)

    # X is array with 16 '4-byte words', that is
    # integers whose representation is at most 4 bytes.
    def _update(self, X) -> bytes:
        A = self.A  # self.A is `AA` from the paper
        B = self.B  # the rest accordingly.
        C = self.C
        D = self.D

        # round 1
        for k in range(4):
            A = MD4.round_1_op(A, B, C, D, X[0 + 4 * k], 3)
            D = MD4.round_1_op(D, A, B, C, X[1 + 4 * k], 7)
            C = MD4.round_1_op(C, D, A, B, X[2 + 4 * k], 11)
            B = MD4.round_1_op(B, C, D, A, X[3 + 4 * k], 19)

        # round 2
        for k in range(4):
            A = MD4.round_2_op(A, B, C, D, X[0 + k], 3)
            D = MD4.round_2_op(D, A, B, C, X[4 + k], 5)
            C = MD4.round_2_op(C, D, A, B, X[8 + k], 9)
            B = MD4.round_2_op(B, C, D, A, X[12 + k], 13)

        # round 3
        for k in (0, 2, 1, 3):
            A = MD4.round_3_op(A, B, C, D, X[0 + k], 3)
            D = MD4.round_3_op(D, A, B, C, X[8 + k], 9)
            C = MD4.round_3_op(C, D, A, B, X[4 + k], 11)
            B = MD4.round_3_op(B, C, D, A, X[12 + k], 15)

        self.A = (A + self.A) & MD4.last32
        self.B = (B + self.B) & MD4.last32
        self.C = (C + self.C) & MD4.last32
        self.D = (D + self.D) & MD4.last32


if __name__ == "__main__":
    # quick test for syntax errors
    x = MD4.from_bytes(b"abcdefghijklmnopqrstuvwxyz")
    print(x.string_digest())
