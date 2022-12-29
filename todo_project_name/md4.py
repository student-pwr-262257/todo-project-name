from bitarray import bitarray
import sys # sys.byteorder

# some variable names may seem obscure; they were taken directly from
# the article "The MD4 Message Digest Algorithm" by Ronald L. Rivest

# the following two functions should probably be private

# I didn't found impl of roll, only shifts.
def l_roll(buff: bitarray, s: int):
    """ Roll bits `buff` to the left s times.
    It is assumed that buff length is bigger than s """
    # return buff[s:] + buff[:s]
    # return (buff << s) | (buff >> (32 - s))
    buff2 = bitarray()
    buff2.frombytes(bytes(reversed(buff.tobytes())))
    buff2 = (buff2 << s) | (buff2 >> (32 - s))
    buff3 = bitarray()
    buff3.frombytes(bytes(reversed(buff2.tobytes())))
    return buff3

# Adding bitarrays is concatenating them, we need addition modulo 2**32 as well.
def add(*args):
    """ Arguments are little endian bitarrays of length 4 * 8 = 32;
    the function returns sum of numbers they are representing modulo 2**32."""
    def retreat_int(bits):
        assert len(bits) == 32
        return int.from_bytes(bits.tobytes(), byteorder='little')
    summed = sum(map(retreat_int , args)) % (1 << 32)
    # print(bin(summed))
    result = bitarray()
    # FIXME: setting big instead of little fixes first iteration for some reason
    # But it should be little, shouldn't it?
    result.frombytes(summed.to_bytes(4, 'big'))
    return result


# magic constants (high-order digits given first == big endian)
ROUND_2 = bitarray()
ROUND_3 = bitarray()
ROUND_2.frombytes(0x5A827999.to_bytes(4, 'big'))
ROUND_3.frombytes(0x6ED9EBA1.to_bytes(4, 'big'))


def pad(bits: bitarray):
    """
    This function adds padding necessary for MD4 to the bits,
    including trailing length of the message.

    ---
    returns:
       (bits, N) -- (modified bitarray, number of 4-byte words).
    """
    # number of bits modulo 2**64
    b = len(bits) % (1 << 64)

    # calculating padding length
    pad_len = (488 - b) % 512
    if pad_len == 0:
        pad_len = 512

    # splitting b into 2 4-byte words
    b1 = b >> 32
    b2 = b & 0xffffffff

    padding = bitarray('1' + '0' * (pad_len - 1))
    # appending original length in 2 separate words
    padding.frombytes(b1.to_bytes(4, 'little'))
    padding.frombytes(b2.to_bytes(4, 'little'))

    bits += padding

    # number of 4-byte words
    # it actually could be easily calculated just from bits (len(bits) // 16)
    N = (b + pad_len + 64) >> 5

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


# import pudb
# SO FAR: this function seems to do exactly what I want.
# BUT results differ from standard impl. Therefore I need to read that one instead.
def round_1_op(A, B, C, D, X, s):
    # pudb.set_trace()
    a = f(B, C, D) # worked for case 1
    b = add(A, a, X) # worked for case 1
    print_regs(b, a, X, A)
    return l_roll(b, s) # tested, works. What is it then????????

def round_2_op(A, B, C, D, X, s):
    return l_roll(add(A, g(B, C, D), X, ROUND_2), s)

def round_3_op(A, B, C, D, X, s):
    return l_roll(add(A, h(B, C, D), X, ROUND_3), s)

def print_regs(A, B, C, D):
    A = int.from_bytes(A.tobytes(), 'big') # printing as-is
    B = int.from_bytes(B.tobytes(), 'big')
    C = int.from_bytes(C.tobytes(), 'big')
    D = int.from_bytes(D.tobytes(), 'big')
    print('{:08x} {:08x} {:08x} {:08x}'.format(A, B, C, D))


def md4(bits: bitarray):
    bits, N = pad(bits)

    # initialization of buffers
    A = bitarray()
    B = bitarray()
    C = bitarray()
    D = bitarray()
    # "low-order bytes first" - little endian
    A.frombytes(0x01234567.to_bytes(4, 'little'))
    B.frombytes(0x89abcdef.to_bytes(4, 'little'))
    C.frombytes(0xfedcba98.to_bytes(4, 'little'))
    D.frombytes(0x76543210.to_bytes(4, 'little'))

    X = [None] * 16
    for i in range(N // 16): # process each 16-word block
        # reassigning X[.]
        for k in range(16):
            X[k] = bits[256 * i + 32 * k : 256 * i + 32 * (k + 1)]
        # print(X) # list of birarrays checked.

        AA = A
        BB = B
        CC = C
        DD = D

        print_regs(A, B, C, D)
        # round 1
        for k in range(4):
            A = round_1_op(A, B, C, D, X[ 0 + 4 * k],  3)
            print_regs(A, B, C, D)
            D = round_1_op(D, A, B, C, X[ 1 + 4 * k],  7)
            print_regs(A, B, C, D)
            C = round_1_op(C, D, A, B, X[ 2 + 4 * k], 11)
            B = round_1_op(B, C, B, A, X[ 3 + 4 * k], 19)
        print_regs(A, B, C, D)

        # round 2
        for k in range(4):
            A = round_2_op(A, B, C, D, X[ 0 + k],  3)
            D = round_2_op(D, A, B, C, X[ 4 + k],  5)
            C = round_2_op(C, D, A, B, X[ 8 + k],  9)
            B = round_2_op(B, C, B, A, X[12 + k], 13)
        print_regs(A, B, C, D)

        # round 3
        for k in (0, 2, 1, 3):
            A = round_2_op(A, B, C, D, X[ 0 + k],  3)
            D = round_2_op(D, A, B, C, X[ 4 + k],  9)
            C = round_2_op(C, D, A, B, X[ 8 + k], 11)
            B = round_2_op(B, C, B, A, X[12 + k], 15)
        print_regs(A, B, C, D)

        A = add(A, AA)
        B = add(B, BB)
        C = add(C, CC)
        D = add(D, DD)
        print_regs(A, B, C, D)

    # and of loop on i

    return A + B + C + D

if __name__ == '__main__':
    # print(add(bitarray('00001101000000000000000000000000'), bitarray('00001011000000000000000000000000')))
    print(md4(bitarray())) # ""
