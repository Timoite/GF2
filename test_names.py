"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a Names class instance."""
    return Names()


def test_unique_error_codes(new_names):
    """Test if unique_error_codes returns a list of unique error codes."""
    assert new_names.unique_error_codes(3) == [0, 1, 2]


def test_unique_error_codes_gives_errors(new_names):
    """Test if unique_error_codes returns the correct errors."""
    # This test would require a specific implementation of unique_error_codes
    with pytest.raises(ValueError):
        new_names.unique_error_codes(0)
        # Assuming it raises an error for 0 codes

    with pytest.raises(ValueError):
        new_names.unique_error_codes(-1)


def test_query(new_names):
    """Test if query returns the correct error codes."""
    new_names.names_dict["hello"] = 15
    assert new_names.query("hello") == 15
    assert new_names.query("I am not in the dictionary") is None


def test_lookup(new_names):
    """Test if lookup returns the correct device IDs."""
    new_names.names_dict["hello"] = 15
    assert new_names.lookup(["hello"]) == [15]
    assert new_names.lookup(["I am not in the dictionary"]) == [0]


def test_get_name_string(new_names):
    """Test if get_name_string returns the correct name string."""
    num = new_names.lookup(["hello"])[0]
    assert new_names.get_name_string(num) == "hello"
    assert new_names.get_name_string(100) is None
