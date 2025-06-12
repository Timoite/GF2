'''Test the scanner module'''
import pytest
from final.scanner import Scanner, Symbol
from final.names import Names
import os


@pytest.fixture
def new_scanner():
    """Return a Scanner class instance."""
    def _create_scanner(file_name):
        new_names = Names()
        # Resolve path to test_files directory at base level
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "GF2/test_files",
                                 file_name + ".txt")
        return Scanner(file_path, new_names)
    return _create_scanner


def test_get_symbol(new_scanner):
    # Testing get_symbol properly returns a symbol
    scanner = new_scanner("all_symbols")

    symbol = scanner.get_symbol()
    assert isinstance(symbol, Symbol)

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
    assert symbol_types == [0, 4, 1, 5, 2, 6, 3, 7, 8, 9, None]
    # In normal operation EOF is now skipped as whitespace


def test_keywords(new_scanner):
    """Testing keywords and device IDs returned as expected"""
    scanner = new_scanner("keywords")
    i = 0
    symbol_ids = []
    while i < 13:
        symbol = scanner.get_symbol()
        symbol_ids.append(symbol.id)
        print(symbol_ids)
        symbol = scanner.get_symbol()
        i += 1
    assert symbol_ids == [scanner.DEVICES_ID, scanner.CONNECTIONS_ID,
                          scanner.MONITORS_ID, scanner.END_ID,
                          scanner.AND_ID, scanner.OR_ID,
                          scanner.NAND_ID, scanner.NOR_ID,
                          scanner.XOR_ID, scanner.CLOCK_ID,
                          scanner.SWITCH_ID, scanner.DTYPE_ID,
                          scanner.SIGGEN_ID]


def test_non_alphabet(new_scanner):
    """Should ignore symbols outside the accepted alphabet"""
    scanner = new_scanner("non_alphabet")
    symbol = scanner.get_symbol()
    assert symbol.type is None


def test_comment(new_scanner):
    """Should ignore text between two hashtags"""
    scanner = new_scanner("comment")
    symbol = scanner.get_symbol()
    assert symbol.type == 0


def test_whitespace(new_scanner):
    """Should ignore all whitespace and new lines"""
    scanner = new_scanner("whitespace")
    symbol = scanner.get_symbol()
    assert symbol.type == 2
