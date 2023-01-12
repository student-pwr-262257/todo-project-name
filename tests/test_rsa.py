#!/usr/bin/python3

# First-party
from todo_project_name import rsa
from todo_project_name.md4 import MD4
from todo_project_name.md5 import MD5

# Third-party
import pytest
from hypothesis import given, strategies as st

ids = st.text(min_size=1).filter(lambda s: s == s.strip())
rsa_keys = st.builds(rsa.RSAKey, id=ids)


@given(key=rsa_keys)
def test_rsa_file_operations(tmp_path_factory, key):
    tmp_path = tmp_path_factory.mktemp("keys")
    key_type = type(key)
    key_path = tmp_path / "test.key"
    rsa.save_key(key, key_path)
    read_key = rsa.read_key(key_path, key_type)
    assert key == read_key, "Written and read keys are not the same."
    assert type(key) is type(
        read_key
    ), "The exact type should be consistent between reads and writes."


def test_rsa_sign():

    # test for example messages, key_lengths, hash methods
    messages = [
        "s",
        "a",
        "*",
        "qwerty",
        "q1w2e3r4t5y6u7i8o9p0",
        "!@#$%^&*()oooooo",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do",
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do 
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim 
    ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut 
    aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui 
    officia deserunt mollit anim id est laborum.""",
    ]
    key_sizes = [32, 64, 64, 128, 256, 128, 256, 256]
    algorithms = [MD4, MD5, MD5, MD4, MD4, MD5, MD4, MD4]
    for message, key_size, algorithm in zip(messages, key_sizes, algorithms):
        keys_pair = rsa.rsa_key_gen(key_size)
        signature = rsa.rsa_sign(message, keys_pair.private, algorithm)
        signature = int(signature, 16)
        assert signature < keys_pair.private.modulus

        # decode and compare
        hashed = algorithm.from_bytes(message.encode("utf-8")).string_digest()
        hashed = int(hashed, 16) % keys_pair.private.modulus
        assert hashed == pow(
            signature, keys_pair.public.key, keys_pair.public.modulus
        )

    # the case of trivial key
    for message, key_size in zip(messages, key_sizes):
        key = rsa.RSAKeyPrivate(1, 2 * key_size)
        hashed = MD4.from_bytes(message.encode("utf-8")).string_digest()
        assert (
            int(rsa.rsa_sign(message, key), 16)
            == int(hashed, 16) % key.modulus
        )


def test_rsa_verify():

    # example messages, key_lengths, hash methods
    messages = [
        "",
        "a",
        "*",
        "qwerty",
        "q1w2e3r4t5y6u7i8o9p0",
        "!@#$%^&*()oooooo",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do",
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do 
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim 
    ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut 
    aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui 
    officia deserunt mollit anim id est laborum.""",
        "LOREM IPSUM",
    ]
    key_sizes = [32, 64, 64, 128, 256, 128, 256, 256, 64]
    algorithms = [MD4, MD5, MD5, MD4, MD4, MD5, MD4, MD4, MD4]
    for message, key_size, algorithm in zip(messages, key_sizes, algorithms):
        key = rsa.rsa_key_gen(key_size)
        signature = rsa.rsa_sign(message, key.private, algorithm)
        assert rsa.rsa_verify(message, signature, key.public, algorithm)


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
