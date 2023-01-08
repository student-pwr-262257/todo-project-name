from .mdn import MDN
from math import sin, floor
from typing import Iterator, List

# some variable names may seem obscure; they were taken directly from
# the article "The MD5 Message-Digest Algorithm" by Ronald L. Rivest (1992)
# or "The MD4 Message Digest Algorithm" (1991) by the same author.


class MD5(MDN):
    """Class computing MD5 message digest. Works for little-endian architecture.

    It is recommended to use methods `MD5.from_bytes` or `MD5.from_file`
    to create new objects.

    To get message digest as `str` use `string_digest`.
    To get message digest as `bytes` read `self.digest` attribute.
    """

    # magic constants
    T = list(floor(4294967296 * abs(sin(i + 1))) for i in range(64))

    def __init__(self, message_bytes: Iterator[bytes]):
        """It is recommended to use methods `MD5.from_bytes` or `MD5.from_file`
        to create new objects.

        Parameters
        ==========
        message_bytes
        : Iterator yielding `bytes` of length exactly 64. Last yielded
        byte string must have length strictly less than 64 (empty byte string
        may be sometimes necessary).
        """
        super()._run_algoritm(message_bytes)

    # bitwise conditional
    @staticmethod
    def f(X, Y, Z):
        """Function used in round 1 of algorithm."""
        return (X & Y) | ((~X) & Z)

    # bitwise conditional
    @staticmethod
    def g(X, Y, Z):
        """Function used in round 2 of algorithm."""
        return (X & Z) | (Y & (~Z))

    # bitwise XOR for 3 inputs (parity function)
    @staticmethod
    def h(X, Y, Z):
        """Function used in round 3 of algorithm."""
        return X ^ Y ^ Z

    @staticmethod
    def i(X, Y, Z):
        """Function used in round 4 of algorithm."""
        return Y ^ (X | (~Z))

    @staticmethod
    def round_1_op(A, B, C, D, X, s, i):
        """Operation of first round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5.f(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def round_2_op(A, B, C, D, X, s, i):
        """Operation of second round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5.g(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def round_3_op(A, B, C, D, X, s, i):
        """Operation of third round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5.h(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def round_4_op(A, B, C, D, X, s, i):
        """Operation of fourth round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5.i(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    def _update(self, X: List[int]) -> None:
        """Update internal registers according to MD5 specification:
        do all of the "processing of single 16-word block" from the paper.

        Parameters
        ==========
        X: list of 16 32-bit unsigned integers (4-byte words) to be processed.
        """
        A = self.A  # self.A is `AA` from the paper
        B = self.B  # the rest accordingly.
        C = self.C
        D = self.D

        # round 1
        for k in range(4):
            A = MD5.round_1_op(A, B, C, D, X[0 + 4 * k], 7, 0 + 4 * k)
            D = MD5.round_1_op(D, A, B, C, X[1 + 4 * k], 12, 1 + 4 * k)
            C = MD5.round_1_op(C, D, A, B, X[2 + 4 * k], 17, 2 + 4 * k)
            B = MD5.round_1_op(B, C, D, A, X[3 + 4 * k], 22, 3 + 4 * k)

        # round 2
        for k in range(4):
            A = MD5.round_2_op(A, B, C, D, X[(1 + 4 * k) % 16], 5, 16 + 4 * k)
            D = MD5.round_2_op(D, A, B, C, X[(6 + 4 * k) % 16], 9, 17 + 4 * k)
            C = MD5.round_2_op(C, D, A, B, X[(11 + 4 * k) % 16], 14, 18 + 4 * k)
            B = MD5.round_2_op(B, C, D, A, X[(0 + 4 * k) % 16], 20, 19 + 4 * k)

        # round 3
        for k in range(4):
            A = MD5.round_3_op(A, B, C, D, X[(5 - 4 * k) % 16], 4, 32 + 4 * k)
            D = MD5.round_3_op(D, A, B, C, X[(8 - 4 * k) % 16], 11, 33 + 4 * k)
            C = MD5.round_3_op(C, D, A, B, X[(11 - 4 * k) % 16], 16, 34 + 4 * k)
            B = MD5.round_3_op(B, C, D, A, X[(14 - 4 * k) % 16], 23, 35 + 4 * k)

        # round 4
        for k in range(4):
            A = MD5.round_4_op(A, B, C, D, X[(0 - 4 * k) % 16], 6, 48 + 4 * k)
            D = MD5.round_4_op(D, A, B, C, X[(7 - 4 * k) % 16], 10, 49 + 4 * k)
            C = MD5.round_4_op(C, D, A, B, X[(14 - 4 * k) % 16], 15, 50 + 4 * k)
            B = MD5.round_4_op(B, C, D, A, X[(5 - 4 * k) % 16], 21, 51 + 4 * k)

        self.A = (A + self.A) & MDN.last32
        self.B = (B + self.B) & MDN.last32
        self.C = (C + self.C) & MDN.last32
        self.D = (D + self.D) & MDN.last32
