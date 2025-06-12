"""Test the monitors module."""
import pytest

from final.names import Names
from final.network import Network
from final.devices import Devices
from final.monitors import Monitors


@pytest.fixture
def new_monitors():
    """Return a Monitors class instance with monitors set on three outputs."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = new_names.lookup(["Sw1", "Sw2", "Or1",
                                                        "I1", "I2"])
    # Add 2 switches and an OR gate
    new_devices.make_device("Sw1", new_devices.SWITCH, 0)
    new_devices.make_device("Sw2", new_devices.SWITCH, 0)
    new_devices.make_device("Or1", new_devices.OR, 2)

    # Make connections
    new_network.make_connection("Sw1", None, "Or1", I1)
    new_network.make_connection("Sw2", None, "Or1", I2)

    # Set monitors
    new_monitors.make_monitor("Sw1", None)
    new_monitors.make_monitor("Sw2", None)
    new_monitors.make_monitor("Or1", None)

    return new_monitors


def test_make_monitor(new_monitors):
    """Test if make_monitor correctly updates the monitors dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID] = names.lookup(["Sw1", "Sw2", "Or1"])

    assert new_monitors.monitors_dictionary == {("Sw1", None): [],
                                                ("Sw2", None): [],
                                                ("Or1", None): []}


def test_make_monitor_gives_errors(new_monitors):
    """Test if make_monitor returns the correct errors."""
    names = new_monitors.names
    network = new_monitors.network
    devices = new_monitors.devices
    [SW1_ID, SW3_ID, OR1_ID, I1, SWITCH_ID] = names.lookup(["Sw1", "Sw3",
                                                            "Or1", "I1",
                                                            "SWITCH"])

    assert new_monitors.make_monitor("Or1", I1) == new_monitors.NOT_OUTPUT
    assert new_monitors.make_monitor("Sw1",
                                     None) == new_monitors.MONITOR_PRESENT
    # I1 is not a device_id in the network
    assert new_monitors.make_monitor("I1",
                                     None) == network.FIRST_DEVICE_ABSENT

    # Make a new switch device
    devices.make_device("Sw3", SWITCH_ID, 0)

    assert new_monitors.make_monitor("Sw3", None) == new_monitors.NO_ERROR


def test_remove_monitor(new_monitors):
    """Test if remove_monitor correctly updates the monitors dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID] = names.lookup(["Sw1", "Sw2", "Or1"])

    new_monitors.remove_monitor("Sw1", None)
    assert new_monitors.monitors_dictionary == {("Sw2", None): [],
                                                ("Or1", None): []}


def test_get_signal_names(new_monitors):
    """Test if get_signal_names returns the correct signal name lists."""
    names = new_monitors.names
    devices = new_monitors.devices
    [D_ID] = names.lookup(["D1"])

    # Create a D-type device
    devices.make_device("D1", devices.D_TYPE)

    assert new_monitors.get_signal_names() == [["Sw1", "Sw2", "Or1"],
                                               ["D1.Q", "D1.QBAR"]]


def test_record_signals(new_monitors):
    """Test if record_signals records the correct signals."""
    names = new_monitors.names
    devices = new_monitors.devices
    network = new_monitors.network

    [SW1_ID, SW2_ID, OR1_ID] = names.lookup(["Sw1", "Sw2", "Or1"])

    HIGH = devices.HIGH
    LOW = devices.LOW

    # Both switches are currently LOW
    network.execute_network()
    new_monitors.record_signals()

    # Set Sw1 to HIGH
    devices.set_switch("Sw1", HIGH)
    network.execute_network()
    new_monitors.record_signals()

    # Set Sw2 to HIGH
    devices.set_switch("Sw2", HIGH)
    network.execute_network()
    new_monitors.record_signals()

    assert new_monitors.monitors_dictionary == {
        ("Sw1", None): [LOW, HIGH, HIGH],
        ("Sw2", None): [LOW, LOW, HIGH],
        ("Or1", None): [LOW, HIGH, HIGH]}


def test_get_margin(new_monitors):
    """Test if get_margin returns the length of the longest monitor name."""
    names = new_monitors.names
    devices = new_monitors.devices
    [D_ID, DTYPE_ID, QBAR_ID, Q_ID] = names.lookup(["Dtype1", "DTYPE",
                                                    "QBAR", "Q"])

    # Create a D-type device and set monitors on its outputs
    devices.make_device("Dtype1", DTYPE_ID)
    new_monitors.make_monitor("Dtype1", QBAR_ID)
    new_monitors.make_monitor("Dtype1", Q_ID)

    # Longest name should be Dtype1.QBAR
    assert new_monitors.get_margin() == 11


def test_reset_monitors(new_monitors):
    """Test if reset_monitors clears the signal lists of all the monitors."""
    names = new_monitors.names
    devices = new_monitors.devices
    [SW1_ID, SW2_ID, OR1_ID] = names.lookup(["Sw1", "Sw2", "Or1"])

    LOW = devices.LOW
    new_monitors.record_signals()
    new_monitors.record_signals()
    assert new_monitors.monitors_dictionary == {("Sw1", None): [LOW, LOW],
                                                ("Sw2", None): [LOW, LOW],
                                                ("Or1", None): [LOW, LOW]}
    new_monitors.reset_monitors()
    assert new_monitors.monitors_dictionary == {("Sw1", None): [],
                                                ("Sw2", None): [],
                                                ("Or1", None): []}


def test_display_signals(capsys, new_monitors):
    """Test if signal traces are displayed correctly on the console."""
    names = new_monitors.names
    devices = new_monitors.devices
    network = new_monitors.network

    [SW1_ID, CLOCK_ID, CL_ID] = names.lookup(["Sw1", "CLOCK", "Clock1"])

    HIGH = devices.HIGH

    # Make a clock and set a monitor on its output
    devices.make_device("Clock1", CLOCK_ID, 2)
    new_monitors.make_monitor("Clock1", None)

    # Both switches are currently LOW
    for _ in range(10):
        network.execute_network()
        new_monitors.record_signals()

    # Set Sw1 to HIGH
    devices.set_switch("Sw1", HIGH)
    for _ in range(10):
        network.execute_network()
        new_monitors.record_signals()

    new_monitors.display_signals()

    # Get std_output
    out, _ = capsys.readouterr()

    traces = out.split("\n")
    assert len(traces) == 5
    assert "Sw1   : __________----------" in traces
    assert "Sw2   : ____________________" in traces
    assert "Or1   : __________----------" in traces

    # Clock could be anywhere in its cycle, but its half period is 2
    assert ("Clock1: __--__--__--__--__--" in traces or
            "Clock1: _--__--__--__--__--_" in traces or
            "Clock1: --__--__--__--__--__" in traces or
            "Clock1: -__--__--__--__--__-" in traces)

    assert "" in traces  # additional empty line at the end
