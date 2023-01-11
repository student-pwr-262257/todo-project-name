from math import sin, floor
from typing import Iterator, List
from .mdn import MDN

# some variable names may seem obscure; they were taken directly from
# the article "The MD5 Message-Digest Algorithm" by Ronald L. Rivest (1992)
# or "The MD4 Message Digest Algorithm" (1991) by the same author.


class MD5(MDN):
    """Class computing MD5 message digest. Works for little-endian architecture.

    It is recommended to use methods `MD5.from_bytes` or `MD5.from_file`
    to create new objects.

    To get message digest as `str` use `string_digest` method.
    To get message digest as `bytes` read `digest` property.
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
        super().__init__(message_bytes)

    # bitwise conditional
    @staticmethod
    def _f(X, Y, Z):
        """Function used in round 1 of algorithm."""
        return (X & Y) | ((~X) & Z)

    # bitwise conditional
    @staticmethod
    def _g(X, Y, Z):
        """Function used in round 2 of algorithm."""
        return (X & Z) | (Y & (~Z))

    # bitwise XOR for 3 inputs (parity function)
    @staticmethod
    def _h(X, Y, Z):
        """Function used in round 3 of algorithm."""
        return X ^ Y ^ Z

    @staticmethod
    def _i(X, Y, Z):
        """Function used in round 4 of algorithm."""
        return Y ^ (X | (~Z))

    @staticmethod
    def _round_1_op(A, B, C, D, X, s, i):
        """Operation of first round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5._f(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def _round_2_op(A, B, C, D, X, s, i):
        """Operation of second round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5._g(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def _round_3_op(A, B, C, D, X, s, i):
        """Operation of third round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5._h(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    @staticmethod
    def _round_4_op(A, B, C, D, X, s, i):
        """Operation of fourth round of the algorithm."""
        return (
            B + MDN.l_roll((A + MD5._i(B, C, D) + X + MD5.T[i]) & MDN.last32, s)
        ) & MDN.last32

    def _update(self, X: List[int]) -> None:
        """Update internal registers according to MD5 specification:
        do all of the "processing of single 16-word block" from the paper.

        Parameters
        ==========
        X: list of 16 32-bit unsigned integers (4-byte words) to be processed.
        """
        A = self._A  # self._A is `AA` from the paper
        B = self._B  # the rest accordingly.
        C = self._C
        D = self._D

        # round 1
        for k in range(4):
            A = MD5._round_1_op(A, B, C, D, X[0 + 4 * k], 7, 0 + 4 * k)
            D = MD5._round_1_op(D, A, B, C, X[1 + 4 * k], 12, 1 + 4 * k)
            C = MD5._round_1_op(C, D, A, B, X[2 + 4 * k], 17, 2 + 4 * k)
            B = MD5._round_1_op(B, C, D, A, X[3 + 4 * k], 22, 3 + 4 * k)

        # round 2
        for k in range(4):
            A = MD5._round_2_op(A, B, C, D, X[(1 + 4 * k) % 16], 5, 16 + 4 * k)
            D = MD5._round_2_op(D, A, B, C, X[(6 + 4 * k) % 16], 9, 17 + 4 * k)
            C = MD5._round_2_op(C, D, A, B, X[(11 + 4 * k) % 16], 14, 18 + 4 * k)
            B = MD5._round_2_op(B, C, D, A, X[(0 + 4 * k) % 16], 20, 19 + 4 * k)

        # round 3
        for k in range(4):
            A = MD5._round_3_op(A, B, C, D, X[(5 - 4 * k) % 16], 4, 32 + 4 * k)
            D = MD5._round_3_op(D, A, B, C, X[(8 - 4 * k) % 16], 11, 33 + 4 * k)
            C = MD5._round_3_op(C, D, A, B, X[(11 - 4 * k) % 16], 16, 34 + 4 * k)
            B = MD5._round_3_op(B, C, D, A, X[(14 - 4 * k) % 16], 23, 35 + 4 * k)

        # round 4
        for k in range(4):
            A = MD5._round_4_op(A, B, C, D, X[(0 - 4 * k) % 16], 6, 48 + 4 * k)
            D = MD5._round_4_op(D, A, B, C, X[(7 - 4 * k) % 16], 10, 49 + 4 * k)
            C = MD5._round_4_op(C, D, A, B, X[(14 - 4 * k) % 16], 15, 50 + 4 * k)
            B = MD5._round_4_op(B, C, D, A, X[(5 - 4 * k) % 16], 21, 51 + 4 * k)

        self._A = (A + self._A) & MDN.last32
        self._B = (B + self._B) & MDN.last32
        self._C = (C + self._C) & MDN.last32
        self._D = (D + self._D) & MDN.last32
