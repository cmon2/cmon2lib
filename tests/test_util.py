from cmon2lib import util
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (1.5, 2.5, 4.0),
])
def test_sum(a, b, expected):
    """Test the sum function."""
    assert util.sum(a, b) == expected

@pytest.mark.parametrize("a, b, expected", [
    (2, 1, 1),
    (0, 0, 0),
    (1, -1, 2),
    (2.5, 1.5, 1.0),
])
def test_subtract(a, b, expected):
    """Test the subtract function."""
    assert util.subtract(a, b) == expected

@pytest.mark.parametrize("a, b, expected", [
    (2, 1, 2),
    (0, 3, 0),
    (1, -1, -1),
    (2.5, 1.5, 3.75),
])
def test_multiply(a, b, expected):
    """Test the subtract function."""
    assert util.multiply(a, b) == expected