#!/usr/bin/python3

# First-party
from todo_project_name import rsa

# Third-party
import pytest


def test_rsa_file_operations(tmp_path):
    KEY_TYPE = rsa.RSAKeyPublic

    key = KEY_TYPE(123, 200)  # TODO: Generate a key. Mock?
    key_path = tmp_path / "test.key"
    rsa.save_key(key, key_path)
    read_key = rsa.read_key(key_path, KEY_TYPE)
    assert key == read_key, "Written and read keys are not the same."


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
