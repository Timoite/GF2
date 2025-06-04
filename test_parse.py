'''Test the parse module (WIP)'''
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


@pytest.fixture
def parser_factory():
    """Fixture to create a Parser instance with custom files."""
    def _create_parser(filename):
        new_names = Names()
        new_devices = Devices(new_names)
        new_network = Network(new_names, new_devices)
        new_monitors = Monitors(new_names, new_devices, new_network)
        new_scanner = Scanner(filename, new_names)
        return Parser(new_names, new_devices, 
                      new_network, new_monitors, new_scanner)
    return _create_parser


def test_parse_network_validity(parser_factory):
    """Test if parse_network will parse for a valid files."""
    parser = parser_factory('valid.txt')
    assert True  # Placeholder for actual parsing logic


def test_parse_network_with_errors(parser_factory):
    """Test if parse_network handles errors correctly."""
    # This test would require a different test file with errors
    # assert new_parser.parse_network() is True
    parser = parser_factory('invalid.txt')
    assert True  # Placeholder, should be False with errors


def test_bad_device_error(parser_factory):
    """Test device with invalid string (bad_device)."""
    parser = parser_factory('bad_device.txt')
    with pytest.raises(BAD_DEVICE):  # Replace Exception with actual error type
        parser.parse_network()


def test_switch_error_above_one(parser_factory):
    """Test switch with qualifier above 1 (invalid_qualifier)."""
    parser = parser_factory('switch_error_above_one.txt')
    with pytest.raises(INVALID_QUALIFIER):  # Replace with actual error type
        parser.parse_network()


def test_clock_zero_error(parser_factory):
    """Test AND/OR/NAND/NOR gate with qualifier < 2 (invalid_qualifier)."""
    parser = parser_factory('clock_error_0.txt')
    with pytest.raises(INVALID_QUALIFIER):  # Replace with actual error type
        parser.parse_network()


def test_gate_qualifier_below_range(parser_factory):
    """Test AND/OR/NAND/NOR gate with qualifier > 16 (invalid_qualifier)."""
    parser = parser_factory('gate_qualifier_below_range.txt')
    with pytest.raises(INVALID_QUALIFIER):
        parser.parse_network()


def test_gate_qualifier_above_range(parser_factory):
    """Test if parse_network raises a GateQualifierError."""
    parser = parser_factory('gate_qualifier_above_range.txt')
    with pytest.raises(INVALID_QUALITFIER):
        parser.parse_network()


def test_dtype_with_qualifier(parser_factory):
    """Test if dtype with qualifier raises an error."""
    parser = parser_factory('dtype_with_qualifier.txt')
    with pytest.raises(QUALIFIER_PRESENT):
        parser.parse_network()


def test_not_gate_with_qualifier(parser_factory):
    """Test NOT gate with qualifier raises an error."""
    parser = parser_factory('not_gate_with_qualifier.txt')
    with pytest.raises(QUALIFIER_PRESENT):
        parser.parse_network()


def test_xor_gate_with_qualifier(parser_factory):
    """Test XOR gate with qualifier raises an error."""
    parser = parser_factory('xor_gate_with_qualifier.txt')
    with pytest.raises(QUALIFIER_PRESENT):
        parser.parse_network()


def test_device_present_error(parser_factory):
    """Test if device ID defined twice raises an error."""
    parser = parser_factory('device_present_error.txt')
    with pytest.raises(DEVICE_PRESENT):
        parser.parse_network()


def test_input_to_input_connection(parser_factory):
    """Test if input to input connection raises an error."""
    parser = parser_factory('input_to_input_connection.txt')
    with pytest.raises(INPUT_TO_INPUT):
        parser.parse_network()


def test_output_to_output_connection(parser_factory):
    """Test if output to output connection raises an error."""
    parser = parser_factory('output_to_output_connection.txt')
    with pytest.raises(OUTPUT_TO_OUTPUT):
        parser.parse_network()


def test_undefined_device_error(parser_factory):
    """Test connection referring to undefined device."""
    parser = parser_factory('undefined_device_error.txt')
    with pytest.raises(DEVICE_ABSENT):
        parser.parse_network()


def test_two_connections_same_input(parser_factory):
    """Test if two connections to the same input raises an error."""
    parser = parser_factory('two_connections_same_input.txt')
    with pytest.raises(INPUT_CONNECTED):
        parser.parse_network()


def test_monitor_connected_to_input(parser_factory):
    """Test if monitor connected to an input raises an error."""
    parser = parser_factory('monitor_connected_to_input.txt')
    with pytest.raises(NOT_INPUT):
        parser.parse_network()


def test_monitor_on_nonexistent_input(parser_factory):
    """Test monitor connected to a nonexistent input raises an error."""
    parser = parser_factory('monitor_connected_to_nonexistent_input.txt')
    with pytest.raises(NOT_INPUT):
        parser.parse_network()


def test_duplicate_monitor(parser_factory):
    """Test two monitors connected to the same input raises an error."""
    parser = parser_factory('two_monitors_connected_to_same_input.txt')
    with pytest.raises(MONITOR_PRESENT):
        parser.parse_network()


def test_input_unconnected_error(parser_factory):
    """Test device with unconnected input raises an error."""
    parser = parser_factory('device_has_unconnected_input.txt')
    with pytest.raises(INPUT_UNCONNECTED):
        parser.parse_network()

# EBNF grammar tests (WIP)


def test_missing_comma(parser_factory):
    """Test if missing semicolon raises an error."""
    parser = parser_factory('missing_comma.txt')
    with pytest.raises(MISSING_COMMA):
        parser.parse_network()


def test_missing_devices(parser_factory):
    """Test if missing device ID raises an error."""
    parser = parser_factory('missing_devices.txt')
    with pytest.raises(MISSING_DEVICES):
        parser.parse_network()


def test_missing_connections(parser_factory):
    """Test if missing connection raises an error."""
    parser = parser_factory('missing_connection.txt')
    with pytest.raises(MISSING_CONNECTIONS):
        parser.parse_network()
