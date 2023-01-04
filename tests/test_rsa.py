#!/usr/bin/python3

# First-party
from todo_project_name import rsa

# Third-party
import pytest


def test_rsa_file_operations(tmp_path):
    key = None  # TODO: Generate a key. Mock?
    key_path = tmp_path / "test.key"
    rsa.save_key(key, key_path)
    read_key = rsa.read_key(key_path)
    assert key == read_key


def main():
    pytest.main([__file__])


if __name__ == "__main__":
    main()
