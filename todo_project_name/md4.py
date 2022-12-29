# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest


class MD4:
    # magic constants (high-order digits given first == big endian)
    ROUND_2 = 0x5A827999
    ROUND_3 = 0x6ED9EBA1
    padding = 0x00000080.to_bytes(64, "little")  # 10000...000 -- 512 bits in total

    def __init__(self, message: bytes):
        self.digest = None
        # preparing for the algorithm
        # self.A = 0x01234567 #.to_bytes(4, 'little')
        # self.B = 0x89abcdef #.to_bytes(4, 'little')
        # self.C = 0xfedcba98 #.to_bytes(4, 'little')
        # self.D = 0x76543210 #.to_bytes(4, 'little')
        self.A = 0x67452301  # this should work on little-endian machines
        self.B = 0xEFCDAB89
        self.C = 0x98BADCFE
        self.D = 0x10325476

        # running the algorithm
        # in the future it must be converted to operate on stream, in order
        # to handle hashing large files.
        X = [None] * 16
        idx = 0
        bits_no = 0
        byte_no = len(message)

        while idx + 64 <= byte_no:
            for i in range(16):
                X[i] = int.from_bytes(
                    message[idx + 4 * i : idx + 4 * (i + 1)], byteorder="little"
                )
            self._update(X)
            bits_no += 512

        # padding and running last iteration (or 2 in the case of empty padding)
        message = message[idx:]  # remaining bytes
        left = byte_no - idx
        # b == 8 * left
        # bits to append: 448 - b (mod 512)
        # bytes to append: 56 - left (mod 64)
        if left == 56:  # appending 512 bits.
            message += MD4.padding
            for i in range(16):
                X[i] = int.from_bytes(message[4 * i : 4 * (i + 1)], byteorder="little")
            self._update(X)
            message = message[64:]  # only 1 unprocessed pack of 16 words
        else:
            message += MD4.padding[0 : (56 - left) % 64]
            bits_no += left * 8
        # appending number of bits
        message += (bits_no & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
        for i in range(16):
            X[i] = int.from_bytes(message[4 * i : 4 * (i + 1)], byteorder="little")
        self._update(X)

        # getting the result
        self.digest = b""
        for chunk in [self.A, self.B, self.C, self.D]:
            self.digest += chunk.to_bytes(4, "little")
        # done

    def string_digest(self):
        def convert(val):
            high = val >> 4  # first 4 bits
            low = val & 0xF  # last  4 bits
            return "{:x}{:x}".format(high, low)

        return "".join(map(convert, self.digest))

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
        return ((X << s) & 0xFFFFFFFF) | (X >> (32 - s))

    @staticmethod
    def round_1_op(A, B, C, D, X, s):
        return MD4.l_roll(A + MD4.f(B, C, D), s)

    @staticmethod
    def round_2_op(A, B, C, D, X, s):
        return MD4.l_roll(A + MD4.g(B, C, D) + X + MD4.ROUND_2, s)

    @staticmethod
    def round_3_op(A, B, C, D, X, s):
        return MD4.l_roll(A + MD4.h(B, C, D) + X + MD4.ROUND_3, s)

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
            A = MD4.round_2_op(A, B, C, D, X[0 + k], 3)
            D = MD4.round_2_op(D, A, B, C, X[4 + k], 9)
            C = MD4.round_2_op(C, D, A, B, X[8 + k], 11)
            B = MD4.round_2_op(B, C, D, A, X[12 + k], 15)

        self.A = (A + self.A) % (1 << 32)
        self.B = (B + self.B) % (1 << 32)
        self.C = (C + self.C) % (1 << 32)
        self.D = (D + self.D) % (1 << 32)


if __name__ == "__main__":
    # quick test for syntax errors
    x = MD4(b"")
    print(x.string_digest())
