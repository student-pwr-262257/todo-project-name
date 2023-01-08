from .mdn import MDN
from typing import Iterator, List

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest (1991)


class MD4(MDN):
    """Class computing MD4 message digest. Works for little-endian architecture.

    It is recommended to use methods `MD4.from_bytes` or `MD4.from_file`
    to create new objects.

    To get message digest as `str` use `string_digest`.
    To get message digest as `bytes` read `self.digest` attribute.
    """

    # magic constants (high-order digits given first == big endian)
    ROUND_2 = 0x5a827999
    ROUND_3 = 0x6ed9eba1

    def __init__(self, message_bytes: Iterator[bytes]):
        """It is recommended to use methods `MD4.from_bytes` or `MD4.from_file`
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

    # bitwise majority function
    @staticmethod
    def g(X, Y, Z):
        """Function used in round 2 of algorithm."""
        return (X & Y) | (X & Z) | (Y & Z)

    # bitwise XOR for 3 inputs (parity function)
    @staticmethod
    def h(X, Y, Z):
        """Function used in round 3 of algorithm."""
        return X ^ Y ^ Z

    @staticmethod
    def round_1_op(A, B, C, D, X, s):
        """Operation of first round of the algorithm."""
        return MDN.l_roll((A + MD4.f(B, C, D) + X) & MD4.last32, s)

    @staticmethod
    def round_2_op(A, B, C, D, X, s):
        """Operation of second round of the algorithm."""
        return MDN.l_roll((A + MD4.g(B, C, D) + X + MD4.ROUND_2) & MD4.last32, s)

    @staticmethod
    def round_3_op(A, B, C, D, X, s):
        """Operation of third round of the algorithm."""
        return MDN.l_roll((A + MD4.h(B, C, D) + X + MD4.ROUND_3) & MD4.last32, s)

    def _update(self, X: List[int]) -> None:
        """Update internal registers according to MD4 specification:
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
