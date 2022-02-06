"""Wrapper around pytest."""


import sys

import pytest


def main():
    """Wrap pytest."""
    return pytest.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
