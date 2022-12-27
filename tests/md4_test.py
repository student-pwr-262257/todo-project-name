from todo_project_name.md4 import md4, l_roll, add
from bitarray import bitarray

def test_l_roll():
    test_cases = [
            (bitarray('1100'), 2, bitarray('0011')),
            (bitarray('1000'), 1, bitarray('0001')),
            (bitarray('1110'), 2, bitarray('1011')),
            (bitarray('11010100'), 5, bitarray('10011010')),
            (bitarray('11110011'), 6, bitarray('11111100')),
            (bitarray('11010100'), 3, bitarray('10100110')),
            ]
    for start, amount, result in test_cases:
        assert l_roll(start, amount) == result



# test cases from the paper
def test_md4():
    # strings encoded as ASCII
    strings = [b"", b"a", b"abc", b"message digest",
               b"abcdefghijklmnopqrstuvwxys" ]

    def string_to_bits(s):
        bits = bitarray(endian='little')
        bits.frombytes(s)
        return bits

    strings_bitarrays = list(map(string_to_bits , strings))
    md4sums = [0x31d6cfe0d16ae931b73c59d7e0c089c0,
               0xbde52cb31de33e46245e05fbdbd6fb24,
               0xa448017aaf21d7525fc10ae87aa6729d,
               0xd73e1c308aa5bbcdeea8ed63df412da9 ]

    def int_to_bits(n):
        bits = bitarray(endian='little')
        bits.frombytes(n.to_bytes(16, 'little'))
        return bits

    md4sums_as_bits = list(map(int_to_bits, md4sums))

    for i in range(4):
        assert md4(strings_bitarrays[i]) == md4sums_as_bits[i]
            


