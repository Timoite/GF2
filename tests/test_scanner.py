'''Test the scanner module (WIP)'''
import pytest
from scanner import Scanner, Symbol
from names import Names

@pytest.fixture
def test_get_symbol():
    """Test if get_symbol correctly returns a symbol."""
    # It is preferable not to use scanner.py to write this part
    new_scanner = Scanner("tests/test_files/test_file.txt", Names()) # assuming test_file.txt is a valid test file
    symbol = new_scanner.get_symbol()
    assert isinstance(symbol, Symbol)
    assert symbol.type is not None
    assert symbol.id is not None

def test_get_symbol_gives_errors(new_scanner):
    """Test if get_symbol returns the correct error."""
    # It is preferable not to use scanner.py to write this part
    # Skeleton for error handling
    return True

    





