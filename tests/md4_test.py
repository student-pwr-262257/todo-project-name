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
        print( MD4(byte_string).string_digest())
        print( md4sum)
        assert MD4(byte_string).string_digest() == md4sum
