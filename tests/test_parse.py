'''Test the parse module (WIP)'''
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

def new_parser():
    """Return a Parser class instance."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    new_scanner = Scanner("tests/test_files/test_file.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors, new_scanner)
    return new_parser



    
def test_parse_network():
    """Test if parse_network correctly parses the test file."""
    parser = new_parser()
    assert parser.parse_network() is True

def test_parse_network_with_errors():
    """Test if parse_network handles errors correctly."""
    # This test would require a different test file with errors
    parser = new_parser()
    assert parser.parse_network() is True  # Placeholder, should be False with errors