"""Test the knxproj."""
from pathlib import Path
from sys import platform

import pytest

from ..knxproj import KnxprojLoader


@pytest.mark.skipif(
    platform == "win32", reason="knxproj availability."
)  # TODO: Fix this with a minimum knxproj
def test_init_path():
    """Load knxproj."""

    # TODO: Add test/minimum knxproj
    knx = KnxprojLoader(Path.home().joinpath("Downloads/MaxMuellner.knxproj"))
    assert isinstance(knx, KnxprojLoader)


if __name__ == "__main__":
    pytest.main(["-x"])
