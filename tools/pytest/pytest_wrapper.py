"""Wrapper around pytest."""

import pytest
import sys

def main():
    return pytest.main(sys.argv[1:])

if __name__ == "__main__":
    raise SystemExit(main())