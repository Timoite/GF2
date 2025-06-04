'''
Test the parse module

It validates:
- A correct network description will parse without errors.
- Every recognized error in the network description raises the expected exception.
'''
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


@pytest.fixture
def parser_factory():
    """Return a fresh Parser wired to a given test-file."""
    def _create_parser(filename: str) -> Parser:
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(f'test_files/{filename}', names)
        return Parser(names, devices, network, monitors, scanner)
    return _create_parser

def _run_and_capture(parser: Parser, capsys):
    """Execute parse_network and return result and stdout_text."""
    result = parser.parse_network()
    captured = capsys.readouterr().out
    return result, captured


def test_valid_file_is_accepted(parser_factory, capsys):
    """Test that a valid network description file is parsed successfully."""
    parser = parser_factory("valid.txt")
    isParsed, output = _run_and_capture(parser, capsys)
    assert isParsed is True
    assert "File parsed successfully" in output


# Define the error cases with their expected messages
ERROR_CASES: dict[str, str] = {
    # Syntax / format errors
    "missing_comma.txt":
        "expected a right arrow, comma, keyword or equals symbol",
    "missing_semicolon.txt":
        "expected an arrow, comma or dash",
    "missing_string.txt": # MISSING_STRING
        "expected a string",
    "missing_integer.txt": # MISSING_INTEGER
        "expected an integer",
    "missing_arrow.txt": # MISSING_ARROW
        "expected a right arrow",
    "missing_equals_symbol.txt": # MISSING_EQUALS
        "expected an equals symbol",
    ""
    
    "missing_devices_keyword.txt": # MISSING_DEVICES_HEADER
        "Missing the section header keyword for devices",
    "missing_connections_keyword.txt": # MISSING_CONNECTIONS_HEADER
        "Missing the section header keyword for connections",
    "missing_monitors_keyword.txt": # MISSING_MONITORS_HEADER
        "Missing the section header keyword for monitors",
    "unknown_keyword.txt": # Tested with wrong keyword
        "Error in format",
    "missing_end_of_file.txt": # MISSING_END_HEADER
        "Missing the end-of-file keyword.",
    # Device-level errors
    "bad_device.txt": # BAD_DEVICE & NOT_DEVICE_NAME
        "device type does not match any code known",
    "switch_error_above_one.txt": # INVALID_QUALIFIER
        "A SWITCH device may only have",
    "clock_error_0.txt": # ZERO_QUALIFIER
        "A CLOCK device’s qualifier must be",
    "gate_qualifier_below_range.txt": # QUALIFIER_OUT_OF_RANGE
        "The qualifier for this type of logic gate",
    "gate_qualifier_above_range.txt": # QUALIFIER_OUT_OF_RANGE
        "The qualifier for this type of logic gate",
    "dtype_with_qualifier.txt": # QUALIFIER_PRESENT
        "Devices of this type should not have a qualifier",
    "not_gate_with_qualifier.txt": # QUALIFIER_PRESENT
        "Devices of this type should not have a qualifier",
    "xor_gate_with_qualifier.txt": # QUALIFIER_PRESENT
        "Devices of this type should not have a qualifier",
    "device_present_error.txt": # DEVICE_PRESENT
        "A device with this ID has already been defined",
    "device_with_no_qualifiers.txt": # NO_QUALIFIER
        "This device type requires a qualifier",

    "input_to_input_connection.txt": # INPUT_TO_INPUT
        "A connection’s first port must be an output port",
    "output_to_output_connection.txt": # OUTPUT_TO_OUTPUT
        "A connection's second port must be an input port",
    "two_connections_same_input.txt": # INPUT_CONNECTED
        "already a connection leading to the specified input port",
    "invalid_port_name.txt": # FIRST_PORT_ABSENT & SECOND_PORT_ABSENT
        "does not have a port with this ID",
    "monitor_connected_to_input.txt": # NOT_OUTPUT
        "Monitors may only connect to output ports",
    "duplicate_monitor.txt": # MONITOR_PRESENT
        "already a monitor connected to this output port",
    "device_has_unconnected_input.txt": # UNCONNECTED_INPUT
        "contains at least one device with an unconnected input",
}

# Test that every error case is handled correctly
@pytest.mark.parametrize("filename, expected_msg",
                         ERROR_CASES.items(),
                         ids=ERROR_CASES.keys())
def test_error_files_are_rejected(parser_factory, capsys, filename, expected_msg):
    """
    Ensure every faulty fixture make parse_network return False and
    print a error message containing <expected_msg>.
    """
    parser = parser_factory(filename)
    ok, output = _run_and_capture(parser, capsys)
    # Check that the parse_network() call returned False
    assert ok is False, f"{filename} unexpectedly parsed with no errors."
    # Use case-fold for accent-insensitive matching (’ vs ')
    assert expected_msg.casefold() in output.casefold(), (
        f"{filename}: expected message fragment not found.\n"
        f"--- Captured output ---\n{output}\n------------------------"
    )
