'''Test the scanner module (WIP)'''
import pytest
from scanner import Scanner, Symbol
from names import Names


@pytest.fixture
def new_scanner():
    """Return a Scanner class instance."""
    # Assuming 'test_file.txt' is a valid test file in the
    # tests/test_files directory
    return Scanner("tests/test_files/test_file.txt", Names())


def test_get_symbol(new_scanner):
    """Test if get_symbol correctly returns a symbol."""
    # It is preferable not to use scanner.py to write this part

    symbol = new_scanner.get_symbol()
    assert isinstance(symbol, Symbol())

    assert symbol.type is not None
    assert symbol.id is not None


def test_get_symbol_gives_errors():
    """Test if get_symbol returns the correct error."""
    # It is preferable not to use scanner.py to write this part
    # Skeleton for error handling

    # with pytest.raises(SomeExpectedException):
    #     new_scanner.get_symbol()
    assert True  # Placeholder for actual error handling logic

# Things to check:
# * Each returned symbol is the correct format
# * Keyword IDs are correctly returned
# * Non-alphabet symbol ignored
# * Comment ignored
# * Whitespace ignored
# * Returns EOF if given an empty file
