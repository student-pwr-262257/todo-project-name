from bitarray import bitarray

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest

# the following two functions should probably be private

# I didn't found impl of roll, only shifts.
def l_roll(buff: bitarray, s: int):
    """ Roll bits `buff` to the left s times.
    It is assumed that buff length is bigger than s """
    return buff[s:] + buff[:s]

# Adding bitarrays is concatenating them, we need addition modulo 2**32 as well.
def add(*args):
    """ Arguments are little endian bitarrays of length 4 * 8 = 32;
    the function returns sum of numbers they are representing modulo 2**32."""
    def retreat_int(bits):
        return int.from_bytes(bits.tobytes(), byteorder='little')
    summed = sum(map(retreat_int , args)) % (1 << 32)
    result = bitarray(endian='little')
    result.frombytes(summed.to_bytes(4, 'little'))
    return result


# magic constants (high-order digits given first).
# TODO: check if I didn't mess up byte order
ROUND_2 = bitarray(endian='little')
ROUND_3 = bitarray(endian='little')
ROUND_2.frombytes(0x5A827999.to_bytes(4, 'little'))
ROUND_3.frombytes(0x6ED9EBA1.to_bytes(4, 'little'))


def pad(bits: bitarray):
    """
    This function adds padding necessary for MD4 to the bits,
    including trailing length of the message.

    ---
    returns:
       (bits, N) -- (modified bitarray, number of 4-byte words).
    """
    # number of bits
    b = len(bits)

    # calculating padding length
    pad_len = (488 - b) % 512
    if pad_len == 0:
        pad_len = 512

    padding = bitarray('1' + '0' * (pad_len - 1))
    # appending original length (only last 64 bits of its representation)
    padding.frombytes((b % 2**64).to_bytes(8, 'little'))

    bits += padding

    # number of 4-byte words
    # it actually could be easily calculated just from bits (len(bits) // 16)
    N = (b + pad_len + 64) // 32

    return bits, N



# bitwise conditional
def f(X, Y, Z):
    return (X & Y) | ((~X) & Z)
# bitwise majority function
def g(X, Y, Z):
    return (X & Y) | (X & Z) | (Y & Z)
# bitwise XOR for 3 inputs (parity function)
def h(X, Y, Z):
    return X ^ Y ^ Z


def round_1_op(A, B, C, D, X, s):
    return l_roll(add(A, f(B, C, D), X), s)

def round_2_op(A, B, C, D, X, s):
    return l_roll(add(A, g(B, C, D), X, ROUND_2), s)

def round_3_op(A, B, C, D, X, s):
    return l_roll(add(A, h(B, C, D), X, ROUND_3), s)


def md4(bits: bitarray):
    bits, N = pad(bits)

    # initialization of buffers
    # TODO: check if I didn't mess up byte order
    A = bitarray(endian='little')
    B = bitarray(endian='little')
    C = bitarray(endian='little')
    D = bitarray(endian='little')
    A.frombytes( 0x_01_23_45_67 .to_bytes(4, 'little'))
    B.frombytes( 0x_89_ab_cd_ef .to_bytes(4, 'little'))
    C.frombytes( 0x_fe_dc_ba_98 .to_bytes(4, 'little'))
    D.frombytes( 0x_76_54_32_10 .to_bytes(4, 'little'))

    X = [None] * 16
    for i in range(N // 16): # process each 16-word block
        # reassigning X[.]
        for k in range(16):
            X[k] = bits[256 * i + 32 * k : 256 * i + 32 * (k + 1)]

        AA = A
        BB = B
        CC = C
        DD = D

        # round 1
        for k in range(4):
            A = round_1_op(A, B, C, D, X[ 0 + 4 * k],  3)
            D = round_1_op(D, A, B, C, X[ 1 + 4 * k],  7)
            C = round_1_op(C, D, A, B, X[ 2 + 4 * k], 11)
            B = round_1_op(D, A, B, C, X[ 3 + 4 * k], 19)

        # round 2
        for k in range(4):
            A = round_2_op(A, B, C, D, X[ 0 + k],  3)
            D = round_2_op(D, A, B, C, X[ 4 + k],  5)
            C = round_2_op(C, D, A, B, X[ 8 + k],  9)
            B = round_2_op(D, A, B, C, X[12 + k], 13)

        # round 3
        for k in (0, 2, 1, 3):
            A = round_2_op(A, B, C, D, X[ 0 + k],  3)
            D = round_2_op(D, A, B, C, X[ 4 + k],  9)
            C = round_2_op(C, D, A, B, X[ 8 + k], 11)
            B = round_2_op(D, A, B, C, X[12 + k], 15)

        A = add(A, AA)
        B = add(B, BB)
        C = add(C, CC)
        D = add(D, DD)

    # and of loop on i

    return A + B + C + D
