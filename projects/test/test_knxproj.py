"""Test the projects."""
from pathlib import Path

import pytest

from projects.knxproj import Knxproj


@pytest.mark.skip("no knxproj available atm")
def test_init_path():
    """Load knxproj."""
    # TODO: Add test/minimum knxproj
    project_path = Path("foo")
    knx = Knxproj(project_path)
    assert isinstance(knx, Knxproj)


if __name__ == "__main__":
    pytest.main(["-x"])
