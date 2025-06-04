'''Test the scanner module'''
import pytest
from scanner import Scanner, Symbol
from names import Names


@pytest.fixture
def new_scanner():
    """Return a Scanner class instance."""
    # Assuming 'test_file.txt' is a valid test file in the
    # tests/test_files directory
    def _create_scanner(file_name):
        new_names = Names()
        return Scanner(file_name + ".txt", new_names)
    return _create_scanner


def test_get_symbol(new_scanner):
    # Testing get_symbol properly returns a symbol
    scanner = new_scanner("all_symbols")

    symbol = scanner.get_symbol()
    assert isinstance(symbol, Symbol())

    assert symbol.type is not None
    assert symbol.id is not None


def test_correct_symbols(new_scanner):
    """Testing symbol types returned as expected"""
    scanner = new_scanner("all_symbols")
    i = 0
    symbol_types = []
    while i < 11:
        symbol = scanner.get_symbol()
        symbol_types.append(symbol.type)
        i += 1
    assert symbol_types == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_keywords(new_scanner):
    """Testing keywords and device IDs returned as expected"""
    scanner = new_scanner("keywords")
    i = 0
    symbol_ids = []
    while i < 12:
        symbol = scanner.get_symbol()
        symbol_ids.append(symbol.id)
        symbol = scanner.get_symbol()
        i += 1
    assert symbol_ids == [scanner.DEVICES_ID, scanner.CONNECTIONS_ID,
                          scanner.MONITORS_ID, scanner.END_ID,
                          scanner.AND_ID, scanner.OR_ID,
                          scanner.NAND_ID, scanner.NOR_ID,
                          scanner.XOR_ID, scanner.CLOCK_ID,
                          scanner.SWITCH_ID, scanner.DTYPE_ID]


def test_non_alphabet(new_scanner):
    """Should ignore symbols outside the accepted alphabet"""
    scanner = new_scanner("non_alphabet")
    symbol = scanner.get_symbol()
    assert symbol.type == 3


def test_comment(new_scanner):
    """Should ignore text between two hashtags"""
    scanner = new_scanner("comment")
    symbol = scanner.get_symbol()
    assert symbol.type == 0


def test_whitespace(new_scanner):
    """Should ignore all whitespace and new lines"""
    scanner = new_scanner("whitespace")
    symbol = scanner.get_symbol()
    assert symbol.type == 1
