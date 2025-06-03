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

        self.error_list = [self.MISSING_ARROW_COMMA_OR_EQUALS,
                           self.MISSING_ARROW_DASH_OR_COMMA,
                           self.MISSING_STRING,
                           self.MISSING_INTEGER,
                           self.MISSING_ARROW,
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
                           self.monitors.NOT_OUTPUT,
                           self.monitors.MONITOR_PRESENT,
                           self.UNCONNECTED_INPUT] = range(30)

    def _error(self, error_type, current_line, next_symbol, stopping_symbol):
        if current_line is None:
            pass
        else:
            arrow_pos = len(current_line)
            arrow_str = ""
            self.error_count += 1
            if next_symbol is None:
                pass
            else:
                current_line = current_line + next_symbol
        if stopping_symbol == "standard":
            while not (self.symbol.type == self.scanner.COMMA
                       or self.symbol.type == self.scanner.KEYWORD
                       or self.symbol.type == self.scanner.EOF):
                self.symbol = self.scanner.get_symbol()
                current_line = (current_line +
                                self.names.get_name_string(self.symbol.id))
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
        elif stopping_symbol == "end":
            while not (self.symbol.ID == self.scanner.END_ID or
                       self.symbol.ID == self.scanner.EOF):
                self.symbol = self.scanner.get_symbol()
        if error_type == self.MISSING_ARROW_COMMA_OR_EQUALS:
            print("Error: expected a right arrow, comma, keyword"
                  " or equals symbol.")
        elif error_type == self.MISSING_ARROW_DASH_OR_COMMA:
            print("Error: expected an arrow, comma or dash.")
        elif error_type == self.MISSING_SLASH_OR_COMMA:
            print("Error: expected a comma, slash or keyword.")
        elif error_type == self.MISSING_STRING:
            print("Error: expected a string.")
        elif error_type == self.MISSING_INTEGER:
            print("Error: expected an integer.")
        elif error_type == self.MISSING_ARROW:
            print("Error: expected a right arrow.")
        elif error_type == self.MISSING_EQUALS:
            print("Error: expected an equals symbol.")
        elif error_type == self.NOT_DEVICE_NAME:
            print("Error: This device type does not match any code known by "
                  "this logic simulator. Valid devices are AND, CLOCK, "
                  "DTYPE, NAND, NOR, OR, SWITCH, XOR.")
        elif error_type == self.devices.BAD_DEVICE:
            arrow_pos = self._seek_error(current_line, "=")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: This device type does not match any code known by "
                  "this logic simulator. Valid devices are AND, CLOCK, "
                  "DTYPE, NAND, NOR, OR, SWITCH, XOR.")
        elif error_type == self.MISSING_DEVICES_HEADER:
            print("Error in format: Missing the section header "
                  "keyword for devices.")
        elif error_type == self.MISSING_CONNECTIONS_HEADER:
            print("Error in format: Missing the section header "
                  "keyword for connections.")
        elif error_type == self.MISSING_MONITORS_HEADER:
            print("Error in format: Missing the section header "
                  "keyword for monitors.")
        elif error_type == self.MISSING_END_HEADER:
            print("Error in format: Missing the end-of-file keyword.")
        elif error_type == self.network.INPUT_TO_INPUT:
            arrow_pos = self._seek_error(current_line, "first")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: A connection’s first port must be an output port.")
        elif error_type == self.network.OUTPUT_TO_OUTPUT:
            arrow_pos = self._seek_error(current_line, "second")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: A connection's second port must be an input port.")
        elif error_type == self.network.FIRST_PORT_ABSENT:
            arrow_pos = self._seek_error(current_line, "first")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: The specified device does not have "
                  "a port with this ID.")
        elif error_type == self.network.SECOND_PORT_ABSENT:
            print("A")
            arrow_pos = self._seek_error(current_line, "second")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: The specified device does not have "
                  "a port with this ID.")
        elif error_type == self.network.FIRST_DEVICE_ABSENT:
            arrow_pos = self._seek_error(current_line, "=")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: No device with this ID has been defined.")
        elif error_type == self.network.SECOND_DEVICE_ABSENT:
            arrow_pos = self._seek_error(current_line, ">")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: No device with this ID has been defined.")
        elif error_type == self.network.INPUT_CONNECTED:
            arrow_pos = self._seek_error(current_line, "second")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: There is already a connection leading to the "
                  "specified input port.")
        elif error_type == self.devices.ZERO_QUALIFIER:
            arrow_pos = self._seek_error(current_line, "/")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: A CLOCK device’s qualifier must be "
                  "a non-zero integer.")
        elif error_type == self.devices.INVALID_QUALIFIER:
            arrow_pos = self._seek_error(current_line, "/")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: A SWITCH device may only have "
                  "a qualifier of 0 or 1.")
        elif error_type == self.devices.QUALIFIER_OUT_OF_RANGE:
            arrow_pos = self._seek_error(current_line, "/")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: The qualifier for this type of logic gate must be "
                  "between 2 and 16.")
        elif error_type == self.devices.QUALIFIER_PRESENT:
            arrow_pos = self._seek_error(current_line, "/")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: Devices of this type should not have a qualifier.")
        elif error_type == self.devices.DEVICE_PRESENT:
            print("Error in line:")
            print(current_line)
            print("^")
            print("Error: A device with this ID has already been defined.")
        elif error_type == self.devices.NO_QUALIFIER:
            arrow_pos = self._seek_error(current_line, ",") - 1
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: This device type requires a qualifier.")
        elif error_type == self.monitors.NOT_OUTPUT:
            arrow_pos = self._seek_error(current_line, "first")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: The specified port is an input port or not defined. "
                  "Monitors may only connect to output ports.")
        elif error_type == self.monitors.MONITOR_PRESENT:
            arrow_pos = self._seek_error(current_line, "first")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: There is already a monitor connected "
                  "to this output port.")
        elif error_type == self.UNCONNECTED_INPUT:
            print("This network contains at least one device "
                  "with an unconnected input. If this input "
                  "is meant to be unused, connect a switch "
                  "with qualifier 0 to it.")

    def _seek_error(self, current_line, target):
        if target == "first":
            equals = current_line.find("=")
            if (current_line[equals+1:].find("-") >
                current_line[equals+1:].find(">") and not
                    current_line[equals+1:].find(">") == -1):
                return equals + 1
            else:
                return current_line[equals+1:].find("-") + equals + 2
        elif target == "second":
            arrow = current_line.find(">")
            return current_line[arrow+1:].find("-") + arrow + 2
        else:
            return current_line.find(target) + 1

    def _name(self):
        name = ""
        while (self.symbol.type == self.scanner.STRING
                or self.symbol.type == self.scanner.INTEGER
                or self.symbol.type == self.scanner.UNDERSCORE):
            name = name + self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        return name

    def _portID(self, current_line):
        portID = ""
        if self.symbol.type == self.scanner.STRING:
            portID = portID + self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.INTEGER:
                portID = portID + self.names.get_name_string(self.symbol.id)
                self.symbol = self.scanner.get_symbol()
            current_line = current_line + portID
            if not (self.symbol.type == self.scanner.ARROW
                    or self.symbol.type == self.scanner.COMMA
                    or self.symbol.type == self.scanner.EQUALS
                    or self.symbol.type == self.scanner.KEYWORD):
                self._error(self.MISSING_ARROW_COMMA_OR_EQUALS, current_line,
                            self.names.get_name_string(self.symbol.id),
                            "standard")
                return portID
            else:
                return portID
        else:
            self._error(self.MISSING_STRING, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")

    def _signalID(self, current_line):
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
            if not [self.symbol.type == self.scanner.COMMA
                    or self.symbol.type == self.scanner.ARROW
                    or self.symbol.type == self.scanner.DASH
                    or self.symbol.type == self.scanner.KEYWORD]:
                self._error(self.MISSING_ARROW_DASH_OR_COMMA, current_line,
                            self.names.get_name_string(self.symbol.id),
                            "standard")
            else:
                return [deviceID, None]

    def _devicetype(self, current_line):
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
                    qualifier = int(self.names.get_name_string(self.symbol.id))
                    current_line = current_line + str(qualifier)
                    self.symbol = self.scanner.get_symbol()
                else:
                    self._error(self.MISSING_INTEGER, current_line,
                                self.names.get_name_string(self.symbol.id),
                                "standard")
            elif self.symbol.type == self.scanner.COMMA:
                qualifier = None
                current_line = current_line + ","
            elif self.symbol.type == self.scanner.KEYWORD:
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

    def _make_device(self, device, deviceID, qualifier):
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
        else:
            error = self.devices.NO_ERROR
        return error

    def _connection(self):
        connectionID = self._name()
        current_line = connectionID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            signal1 = self._signalID(current_line)
            current_line = current_line + signal1[0]
            if signal1[1] is None:
                pass
            else:
                current_line = current_line + "-" + signal1[1]
            if self.symbol.type == self.scanner.ARROW:
                current_line = current_line + ">"
                self.symbol = self.scanner.get_symbol()
                signal2 = self._signalID(current_line)
                current_line = current_line + signal2[0]
                if signal2[1] is None:
                    pass
                else:
                    current_line = current_line + "-" + signal2[1]
            else:
                self._error(self.MISSING_ARROW, current_line,
                            self.names.get_name_string(self.symbol.id),
                            "standard")
        else:
            self._error(self.MISSING_EQUALS, current_line,
                        self.names.get_name_string(self.symbol.id), "standard")
        if self.error_count == 0:
            error_type = self.network.make_connection(signal1[0],
                                                      self.devices.names.query
                                                      (signal1[1]), signal2[0],
                                                      self.devices.names.query
                                                      (signal2[1]))
            if error_type != self.network.NO_ERROR:
                self._error(error_type, current_line, None, "seek")

    def _monitor(self):
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
            error_type = self.monitors.make_monitor(port[0],
                                                    self.devices.names.query
                                                    (port[1]))
            if error_type != self.monitors.NO_ERROR:
                self._error(error_type, current_line, None, "seek")

    def _devices_list(self):
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            self._device()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._device()
        else:
            self._error(self.MISSING_DEVICES_HEADER, None, None, "End")

    def _connections_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CONNECTIONS_ID):
            self.symbol = self.scanner.get_symbol()
            self._connection()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._connection()
        else:
            self._error(self.MISSING_CONNECTIONS_HEADER, None, None, "End")

    def _monitors_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.MONITORS_ID):
            self.symbol = self.scanner.get_symbol()
            self._monitor()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._monitor()
            if not (self.symbol.type == self.scanner.KEYWORD and
                    self.symbol.id == self.scanner.END_ID):
                self._error(self.MISSING_END_HEADER, None, None, "Stop")
        else:
            self._error(self.MISSING_MONITORS_HEADER, None, None, "End")

    def parse_network(self):
        """Parse the circuit definition file."""
        self.error_count = 0
        self._devices_list()
        self._connections_list()
        self._monitors_list()
        if self.network.check_network() is False:
            self._error(self.UNCONNECTED_INPUT, None, None, "Stop")
            self.error_count += 1
        if self.error_count == 0:
            print("File parsed successfully")
            return True
        else:
            return False
