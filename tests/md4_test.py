from todo_project_name.md4 import MD4

# test cases from the paper
def test_md4():
    # strings encoded as ASCII
    byte_strings = [b"", b"a", b"abc", b"message digest", b"abcdefghijklmnopqrstuvwxyz"]

    md4sums = [
        "31d6cfe0d16ae931b73c59d7e0c089c0",
        "bde52cb31de33e46245e05fbdbd6fb24",
        "a448017aaf21d8525fc10ae87aa6729d",
        "d9130a8164549fe818874806e1c7014b",
        "d79e1c308aa5bbcdeea8ed63df412da9",
    ]

    for byte_string, md4sum in zip(byte_strings, md4sums):
        assert MD4.from_bytes(byte_string).string_digest() == md4sum


# More test cases, comparing to results computed on the following site:
# http://www.unit-conversion.info/texttools/md4/
# I noticed that some sites on the internet produce hashes different than ones
# presented as examples in the paper. The one above however is consistent with it.
# Perhaps it is fault of text encoding. I assume that the paper uses ASCII.
def test_extended_md4():
    # It is important to check byte strings longer than 56 bytes,
    # as well as ones of length mod 64 equal to 56.
    byte_strings = [
        b"This is a short string (shorter than 56 bytes)",
        b"This string is longer that 56 characters, by something 5-ish.",
        b"This string has length of 56 bytes in ASCII. The padding",
        b"This string has length of 120 bytes in ASCII, which is "
        b"exactly 64 bytes more than 56. Here is necessary padding: 1234567",
        b"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
        b"eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim "
        b"ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
        b"aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit "
        b"in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        b"Excepteur sint occaecat cupidatat non proident, sunt in culpa qui "
        b"officia deserunt mollit anim id est laborum.",
    ]

    md4sums = [
        "c606c645ee59abf7a5800092024d7655",
        "a982457b257c736f8d8d1a6e06732337",
        "18985eb17340f55a0277df1ef3c998ca",
        "b548c8ffbaf8612c9b317898a18c0ffb",
        "8db2ba4980fa7d57725e42782ab47b42",
    ]
    for byte_string, md4sum in zip(byte_strings, md4sums):
        assert MD4.from_bytes(byte_string).string_digest() == md4sum


# More test cases, comparing to results computed on the following site:
# https://www.cmtoinchesconvert.com/online-tools/md4_file_hash.html
# It allows to hash files instead of strings of text.
def test_md4_file():
    filenames = ["tests/data/md4_test_file.bin", "tests/data/md4_test_file.txt"]
    md4sums = [
        "732868172cbed3f7916701c3c289d743",
        "d3cb716c9993799d7d30ce118fa8d200",
    ]

    for filename, md4sum in zip(filenames, md4sums):
        assert MD4.from_file(filename).string_digest() == md4sum
