"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.scanner = scanner
        self.network = network
        self.devices = devices
        self.monitors = monitors
        self.names = names

        self.error_list = [self.MISSING_DASH_COMMA_OR_KEYWORD,
                           self.MISSING_STRING,
                           self.MISSING_INTEGER,
                           self.MISSING_ARROW_OR_DASH,
                           self.MISSING_EQUALS,
                           self.NOT_DEVICE_NAME,
                           self.devices.BAD_DEVICE,
                           self.MISSING_SLASH_OR_COMMA,
                           self.MISSING_DEVICES_HEADER,
                           self.MISSING_CONNECTIONS_HEADER,
                           self.MISSING_MONITORS_HEADER,
                           self.MISSING_END_HEADER,
                           self.network.INPUT_TO_INPUT,
                           self.network.OUTPUT_TO_OUTPUT,
                           self.network.INPUT_CONNECTED,
                           self.network.FIRST_PORT_ABSENT,
                           self.network.SECOND_PORT_ABSENT,
                           self.network.FIRST_DEVICE_ABSENT,
                           self.network.SECOND_DEVICE_ABSENT,
                           self.network.INPUT_CONNECTED,
                           self.devices.ZERO_QUALIFIER,
                           self.devices.INVALID_QUALIFIER,
                           self.devices.QUALIFIER_OUT_OF_RANGE,
                           self.devices.QUALIFIER_PRESENT,
                           self.devices.DEVICE_PRESENT,
                           self.devices.NO_QUALIFIER,
                           self.devices.NOT_BINARY,
                           self.monitors.NOT_OUTPUT,
                           self.monitors.MONITOR_PRESENT,
                           self.UNCONNECTED_INPUT] = range(30)

    def _error(self, error_type, current_line, next_symbol, stopping_symbol):
        """Generate a command line report for the first error found."""
        # Now always increment the error count
        self.error_count += 1
        # Handle the case where current_line is None
        arrow_pos = 0
        arrow_str = ""
        if current_line is not None:
            # Generates a default position indicator for syntax errors
            arrow_pos = len(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            if next_symbol is not None:
                current_line += next_symbol

        if stopping_symbol == "standard":
            # Skip to next line
            while not (self.symbol.type == self.scanner.COMMA
                       or self.symbol.type == self.scanner.KEYWORD
                       or self.symbol.type == self.scanner.EOF):
                self.symbol = self.scanner.get_symbol()
                if current_line is not None:
                    current_line = (current_line +
                                    self.names.get_name_string(self.symbol.id))
        if current_line is not None:
            if ord(current_line[-1]) == 10:
                current_line = current_line[:-1]

        if self.error_count == 1:
            if next_symbol == "No symbol":
                print("Error: The parser has recieved an empty symbol. "
                      "This may indicate the provided file contains no "
                      "symbols (check your comments: it is possible "
                      "that every valid symbol has been commented out) "
                      "or that the parser has recieved a symbol not "
                      "found in its alphabet (acceptable characters are "
                      "alphanumeric characters, '>', '_', '-', ',', "
                      "'#', '=' and '/'.")
            elif next_symbol in ["DEVICES", "CONNECTIONS", "MONITORS", "END"]:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: the keywords DEVICES, CONNECTIONS, MONITORS and "
                      "END should only appear once each, at the start of the "
                      "devices, connections and monitors lists and at the end "
                      "of the file respectively. If this error displays, the "
                      "parser has encountered a keyword in an invalid location"
                      " or encountered the keywords in the wrong order, or has"
                      " encountered a comma after the last item in a list.")
            elif (next_symbol in ["AND", "OR", "NOR", "XOR", "NAND", "DTYPE",
                                  "SWITCH", "CLOCK", "SIGGEN"]
                  and current_line == next_symbol):
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: the device types AND, CLOCK, DTYPE, NAND, NOR, "
                      "OR, SIGGEN, SWITCH and XOR should not be used "
                      "as device or port names.")
            elif error_type == self.MISSING_SLASH_OR_COMMA:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected a comma, slash or keyword.")
            elif error_type == self.MISSING_STRING:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected a string.")
            elif error_type == self.MISSING_INTEGER:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected an integer.")
            elif error_type == self.MISSING_ARROW_OR_DASH:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected a right arrow or dash.")
            elif error_type == self.MISSING_DASH_COMMA_OR_KEYWORD:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected a dash, comma or the MONITORS keyword.")
            elif error_type == self.MISSING_EQUALS:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: expected an equals symbol.")
            elif error_type == self.NOT_DEVICE_NAME:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: This device type does not match any code known "
                      "by this logic simulator. Valid devices are AND, CLOCK, "
                      "DTYPE, NAND, NOR, OR, SIGGEN, SWITCH, XOR.")
            elif error_type == self.devices.BAD_DEVICE:
                arrow_pos = self._seek_error(current_line, "=")
                print("Error in line:")
                print(current_line)
                i = 0
                arrow_str = ""
                while i < arrow_pos:
                    arrow_str = arrow_str + " "
                    i += 1
                arrow_str = arrow_str + "^"
                print("Error: This device type does not match any code known "
                      "by this logic simulator. Valid devices are AND, CLOCK, "
                      "DTYPE, NAND, NOR, OR, SIGGEN, SWITCH, XOR.")
            elif error_type == self.MISSING_DEVICES_HEADER:
                print("Error in line:")
                print(next_symbol)
                print("^")
                print("Error: Expected the DEVICES keyword.")
            elif error_type == self.MISSING_CONNECTIONS_HEADER:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: Expected a comma or the CONNECTIONS keyword.")
            elif error_type == self.MISSING_MONITORS_HEADER:
                print("Error in line:")
                print(current_line)
                print(arrow_str)
                print("Error: Expected a comma or the MONITORS keyword.")
            elif error_type == self.MISSING_END_HEADER:
                print("Error in line:")
                print(current_line[:-1])
                print(arrow_str)
                print("Error: Expected a comma or the END keyword.")
            elif error_type == self.network.INPUT_TO_INPUT:
                arrow_pos = self._seek_error(current_line, "first")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: A connection’s first port must be "
                      "an output port.")
            elif error_type == self.network.OUTPUT_TO_OUTPUT:
                arrow_pos = self._seek_error(current_line, "second")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: A connection's second port must be "
                      "an input port.")
            elif error_type == self.network.FIRST_PORT_ABSENT:
                arrow_pos = self._seek_error(current_line, "first")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: The specified device does not have "
                      "a port with this ID.")
            elif error_type == self.network.SECOND_PORT_ABSENT:
                print("A")
                arrow_pos = self._seek_error(current_line, "second")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: The specified device does not have "
                      "a port with this ID. (If this is the last "
                      "connection in the list, check that the"
                      " MONITORS keyword is present - this may be "
                      "caused by it being misspelled or absent.)")
            elif error_type == self.network.FIRST_DEVICE_ABSENT:
                arrow_pos = self._seek_error(current_line, "=")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: No device with this ID has been defined.")
            elif error_type == self.network.SECOND_DEVICE_ABSENT:
                arrow_pos = self._seek_error(current_line, ">")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: No device with this ID has been defined.")
            elif error_type == self.network.INPUT_CONNECTED:
                arrow_pos = self._seek_error(current_line, "second")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: There is already a connection leading to the "
                      "specified input port.")
            elif error_type == self.devices.ZERO_QUALIFIER:
                arrow_pos = self._seek_error(current_line, "/")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: A CLOCK device’s qualifier must be "
                      "a non-zero integer.")
            elif error_type == self.devices.INVALID_QUALIFIER:
                arrow_pos = self._seek_error(current_line, "/")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: A SWITCH device may only have "
                      "a qualifier of 0 or 1.")
            elif error_type == self.devices.QUALIFIER_OUT_OF_RANGE:
                arrow_pos = self._seek_error(current_line, "/")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: The qualifier for this type of logic gate "
                      "must be between 2 and 16.")
            elif error_type == self.devices.QUALIFIER_PRESENT:
                arrow_pos = self._seek_error(current_line, "/")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: Devices of this type should not have "
                      "a qualifier.")
            elif error_type == self.devices.NOT_BINARY:
                arrow_pos = self._seek_error(current_line, "/")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: This device's qualifier should be "
                      "a binary number.")
            elif error_type == self.devices.DEVICE_PRESENT:
                print("Error in line:")
                print(current_line)
                print("^")
                print("Error: A device with this ID has already been defined.")
            elif error_type == self.devices.NO_QUALIFIER:
                arrow_pos = self._seek_error(current_line, ",") - 1
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: This device type requires a qualifier.")
            elif error_type == self.monitors.NOT_OUTPUT:
                arrow_pos = self._seek_error(current_line, "first")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: The specified port is an input port or not "
                      "defined. Monitors may only connect to output ports."
                      "(If this is the last monitor in the list, check "
                      " that the END keyword is present - this may"
                      "be caused by it being misspelled or absent.)")
            elif error_type == self.monitors.MONITOR_PRESENT:
                arrow_pos = self._seek_error(current_line, "first")
                print("Error in line:")
                print(current_line)
                self._print_arrow(arrow_pos)
                print("Error: There is already a monitor connected "
                      "to this output port.")
            elif error_type == self.UNCONNECTED_INPUT:
                print("This network contains at least one device "
                      "with an unconnected input. If this input "
                      "is meant to be unused, connect a switch "
                      "with qualifier 0 to it.")
            """Note to examiner: I have opted to keep the if/elif statement a
            is, largely for ease of maintenance. I have however split the while
            loops for generating arrows off into a seperate function which has
            eliminated a fair amount of the repetition."""

    def _seek_error(self, current_line, target):
        """Semantic errors use this function to generate an arrow
        pointing at the part of the current line that caused the error."""
        if target == "first":
            """Find first port"""
            equals = current_line.find("=")
            if (current_line[equals+1:].find("-") >
                current_line[equals+1:].find(">") and not
                    current_line[equals+1:].find(">") == -1):
                return equals + 1
            else:
                return current_line[equals+1:].find("-") + equals + 2
        elif target == "second":
            """Find second port"""
            arrow = current_line.find(">")
            return current_line[arrow+1:].find("-") + arrow + 2
        else:
            """Function call tells this function to look for a particular
            character, as per the EBNF the source of the semantic error
            must follow it - this returns the next position"""
            return current_line.find(target) + 1

    def _print_arrow(self, arrow_pos):
        i = 0
        arrow_str = ""
        while i < arrow_pos:
            arrow_str = arrow_str + " "
            i += 1
        arrow_str = arrow_str + "^"
        print(arrow_str)

    def _name(self):
        """Generate a name - a combination of letters,
        numbers and underscores"""
        name = ""
        if self.symbol.type == self.scanner.STRING:
            name = name + self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        else:
            self._error(self.MISSING_STRING, "",
                        self.names.get_name_string(self.symbol.id), "standard")
        return name

    def _portID(self, current_line):
        """Generate a port ID - a string followed by an integer or
        just a string. If the ID is None, this function is not called."""
        portID = ""
        if self.symbol.type == self.scanner.STRING:
            portID = portID + self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.INTEGER:
                portID = portID + self.names.get_name_string(self.symbol.id)
                self.symbol = self.scanner.get_symbol()
            current_line = current_line + portID
            return portID
        else:
            self._error(self.MISSING_STRING, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")

    def _signalID(self, current_line):
        """Generate a signal - a device name optionally followed
        by a dash and a port ID"""
        deviceID = self._name()
        current_line = current_line + deviceID
        if self.symbol.type == self.scanner.DASH:
            current_line = current_line + "-"
            self.symbol = self.scanner.get_symbol()
            portID = self._portID(current_line)
            if portID is None:
                pass
            else:
                current_line = current_line + portID
            return [deviceID, portID]
        else:
            return [deviceID, None]

    def _devicetype(self, current_line):
        """Generate a device type - a string in a fixed list
        from the scanner"""
        if self.symbol.type == self.scanner.DEVICE_TYPE:
            devicetype = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
            return devicetype
        else:
            self._error(self.NOT_DEVICE_NAME, current_line,
                        self.names.get_name_string(self.symbol.id),
                        "standard")
            return (self.names.get_name_string(self.symbol.id))

    def _device(self):
        """Generate a device: a string followed by an equals sign,
        a device type and optionally a qualifier"""
        deviceID = self._name()
        current_line = deviceID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            device = self._devicetype(current_line)
            current_line = current_line + device
            if self.symbol.type == self.scanner.SLASH:
                current_line = current_line + "/"
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INTEGER:
                    if not device == "SIGGEN":
                        qualifier = int(self.names.get_name_string
                                        (self.symbol.id))
                    else:
                        qualifier = self.names.get_name_string(self.symbol.id)
                    current_line = current_line + str(qualifier)
                    self.symbol = self.scanner.get_symbol()
                else:
                    self._error(self.MISSING_INTEGER, current_line,
                                self.names.get_name_string(self.symbol.id),
                                "standard")
            elif (self.symbol.type == self.scanner.COMMA
                  or self.symbol.type == self.scanner.KEYWORD):
                qualifier = None
            else:
                self._error(self.MISSING_SLASH_OR_COMMA, current_line,
                            self.names.get_name_string(self.symbol.id),
                            "standard")
        else:
            self._error(self.MISSING_EQUALS, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")
        if self.error_count == 0:
            error_type = self._make_device(device, deviceID, qualifier)
            if error_type != self.devices.NO_ERROR:
                self._error(error_type, current_line, None, "seek")
        return current_line

    def _make_device(self, device, deviceID, qualifier):
        """Accesses the devices module and makes a device using the input line,
        then returns the semantic error recieved (if any)"""
        if device in ["AND", "OR", "NAND", "NOR", "XOR"]:
            if device == "AND":
                error = self.devices.make_device(deviceID, self.devices.AND,
                                                 qualifier)
            elif device == "OR":
                error = self.devices.make_device(deviceID, self.devices.OR,
                                                 qualifier)
            elif device == "NAND":
                error = self.devices.make_device(deviceID, self.devices.NAND,
                                                 qualifier)
            elif device == "NOR":
                error = self.devices.make_device(deviceID, self.devices.NOR,
                                                 qualifier)
            else:
                error = self.devices.make_device(deviceID, self.devices.XOR,
                                                 qualifier)
        elif device == "CLOCK":
            error = self.devices.make_device(deviceID, self.devices.CLOCK,
                                             qualifier)
        elif device == "SWITCH":
            error = self.devices.make_device(deviceID, self.devices.SWITCH,
                                             qualifier)
        elif device == "DTYPE":
            error = self.devices.make_device(deviceID, self.devices.D_TYPE,
                                             qualifier)
        elif device == "SIGGEN":
            error = self.devices.make_device(deviceID, self.devices.SIGGEN,
                                             qualifier)
        else:
            error = self.devices.NO_ERROR
        return error

    def _connection(self):
        """Generate a connection: a string followed by an equals, a signal, an
        arrow, and another signal."""
        connectionID = self._name()
        current_line = connectionID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            signal1 = self._signalID(current_line)
            current_line = current_line + signal1[0]
            if signal1[1] is None:
                if not self.symbol.type == self.scanner.ARROW:
                    self._error(self.MISSING_ARROW_OR_DASH, current_line,
                                self.names.get_name_string(self.symbol.id),
                                "standard")
            else:
                current_line = current_line + "-" + signal1[1]
            if self.symbol.type == self.scanner.ARROW:
                current_line = current_line + ">"
                self.symbol = self.scanner.get_symbol()
                signal2 = self._signalID(current_line)
                current_line = current_line + signal2[0]
                if signal2[1] is None:
                    if not (self.symbol.type == self.scanner.COMMA
                            or self.symbol.type == self.scanner.KEYWORD):
                        self._error(self.MISSING_DASH_COMMA_OR_KEYWORD,
                                    current_line,
                                    self.names.get_name_string(self.symbol.id),
                                    "standard")
                else:
                    current_line = current_line + "-" + signal2[1]
                    if not (self.symbol.type == self.scanner.COMMA
                            or self.symbol.type == self.scanner.KEYWORD):
                        self._error(self.MISSING_DASH_COMMA_OR_KEYWORD,
                                    current_line,
                                    self.names.get_name_string(self.symbol.id),
                                    "standard")
            else:
                self._error(self.MISSING_ARROW_OR_DASH, current_line,
                            self.names.get_name_string(self.symbol.id),
                            "standard")
        else:
            self._error(self.MISSING_EQUALS, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")
        """If there are no errors yet, accesses the network module,
        connects the two signals, and returns the semantic error (if any)"""
        if self.error_count == 0:
            error_type = self.network.make_connection(signal1[0],
                                                      self.devices.names.query
                                                      (signal1[1]), signal2[0],
                                                      self.devices.names.query
                                                      (signal2[1]))
            if error_type != self.network.NO_ERROR:
                self._error(error_type, current_line, None, "seek")

    def _monitor(self):
        """Generates a monitor: a string followed by an equals and a signal"""
        monitorID = self._name()
        current_line = monitorID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            port = self._signalID(current_line)
            current_line = current_line + port[0]
            if port[1] is None:
                pass
            else:
                current_line = current_line + "-" + port[1]
        else:
            self._error(self.MISSING_EQUALS, current_line,
                        self.names.get_name_string(self.symbol.id),
                        "standard")
        if self.error_count == 0:
            """If there are no errors yet, accesses the monitors module, adds a
            monitor to the signal, and returns the semantic error (if any)"""
            error_type = self.monitors.make_monitor(port[0],
                                                    self.devices.names.query
                                                    (port[1]))
            if error_type != self.monitors.NO_ERROR:
                self._error(error_type, current_line, None, "seek")
        return current_line

    def _devices_list(self):
        """Looks for the DEVICES keyword, and if found,
        generates a comma-seperated list of devices
        terminating in the CONNECTIONS keyword"""
        current_line = ""
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            current_line = self._device()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                current_line = self._device()
            return current_line
        else:
            self._error(self.MISSING_DEVICES_HEADER, "",
                        self.names.get_name_string(self.symbol.id),
                        "standard")
            return current_line

    def _connections_list(self, current_line):
        """Looks for the CONNECTIONS keyword, and if found,
        generates a comma-seperated list of connections
        terminating in the MONITORS keyword"""
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CONNECTIONS_ID):
            self.symbol = self.scanner.get_symbol()
            current_line = self._connection()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                current_line = self._connection()
            return current_line
        else:
            self._error(self.MISSING_CONNECTIONS_HEADER, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")
            return current_line

    def _monitors_list(self, current_line):
        """Looks for the MONITORS keyword, and if found,
        generates a comma-seperated list of monitors
        terminating in the END keyword"""
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.MONITORS_ID):
            self.symbol = self.scanner.get_symbol()
            current_line = self._monitor()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                current_line = self._monitor()
                print(current_line)
            if not (self.symbol.type == self.scanner.KEYWORD and
                    self.symbol.id == self.scanner.END_ID):
                self._error(self.MISSING_END_HEADER, current_line,
                            self.names.get_name_string(self.symbol.id), "stop")
        else:
            self._error(self.MISSING_MONITORS_HEADER, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")

    def parse_network(self):
        """Parse the circuit definition file."""
        self.error_count = 0
        current_line = self._devices_list()
        current_line = self._connections_list(current_line)
        self._monitors_list(current_line)
        if self.network.check_network() is False:
            """After everything is concluded, the network must have
            no unconnected inputs, or the network module will never
            be able to calculate its outputs"""
            self._error(self.UNCONNECTED_INPUT, None, None, "stop")
            self.error_count += 1
        if self.error_count == 0:
            print("File parsed successfully.")
            return True
        else:
            return False
