import struct
import sys
from todo_project_name.mdn import MDN

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest


class MD4(MDN):
    # magic constants (high-order digits given first == big endian)
    ROUND_2 = 0x5A827999
    ROUND_3 = 0x6ED9EBA1

    def __init__(self, message_bytes):
        super().run_algoritm(message_bytes)

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
    def round_1_op(A, B, C, D, X, s):
        return MDN.l_roll((A + MD4.f(B, C, D) + X) & MD4.last32, s)

    @staticmethod
    def round_2_op(A, B, C, D, X, s):
        return MDN.l_roll((A + MD4.g(B, C, D) + X + MD4.ROUND_2) & MD4.last32, s)

    @staticmethod
    def round_3_op(A, B, C, D, X, s):
        return MDN.l_roll((A + MD4.h(B, C, D) + X + MD4.ROUND_3) & MD4.last32, s)

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

