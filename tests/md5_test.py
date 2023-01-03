from todo_project_name.md5 import MD5

# test cases from the paper
def test_md5():
    # strings encoded as ASCII
    byte_strings = [b"", b"a", b"abc", b"message digest", b"abcdefghijklmnopqrstuvwxyz",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                    "12345678901234567890123456789012345678901234567890123456789012345678901234567890"]

    md5sums = [
        "d41d8cd98f00b204e9800998ecf8427e",
        "0cc175b9c0f1b6a831c399e269772661",
        "900150983cd24fb0d6963f7d28e17f72",
        "f96b697d7cb7938d525a2f31aaf161d0",
        "c3fcd3d76192e4007dfb496cca67e13b",
        "d174ab98d277d9f5a5611c2c9f419d9f",
        "57edf4a22be3c955ac49da2e2107b67a",
    ]

    for byte_string, md5sum in zip(byte_strings, md5sums):
        assert MD5.from_bytes(byte_string).string_digest() == md5sum


# More test cases, comparing to results computed on the following site:
# http://www.unit-conversion.info/texttools/md5/
# I noticed that some sites on the internet produce hashes different than ones
# presented as examples in the paper. The one above however is consistent with it.
# Perhaps it is fault of text encoding. I assume that the paper uses ASCII.
def test_extended_md5():
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

    md5sums = [
        "e091d19bae97ef36e24ae8dfd698eb12",
        "b1efc0fd1c2e6cf52b14a802a855b3c9",
        "e95e613fc32fb3872bfcaea1bb51d207",
        "f4be2750a0c444a4f27aabc0eacca237",
        "956e325fdbfd27759281590bc08315e0",
    ]
    for byte_string, md5sum in zip(byte_strings, md5sums):
        assert MD5.from_bytes(byte_string).string_digest() == md5sum


# More test cases, comparing to results computed on the following site:
# https://www.cmtoinchesconvert.com/online-tools/md5_file_hash.html
# It allows to hash files instead of strings of text.
def test_md5_file():
    filenames = ["md_test_file.bin", "md_test_file.txt"]
    md5sums = [
        "4d413baa3b076bd64e4416a75ca9292f",
        "9718dafc53ef7fdd3da31171b8706ea3",
    ]

    for filename, md5sum in zip(filenames, md5sums):
        assert MD5.from_file(filename).string_digest() == md5sum
