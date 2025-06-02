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
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

    def _error(self, error_type, current_line, stopping_symbol):
        arrow_pos = len(current_line)
        arrow_str = ""
        self.error_count += 1
        if stopping_symbol == "standard":
            while not (self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF):
                self.symbol = self.scanner.get_symbol()
                current_line = current_line + self.symbol.id
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
        elif stopping_symbol == "end":
            while not self.symbol.ID == self.scanner.END_ID or self.symbol.ID == self.scanner.EOF:
                self.symbol = self.scanner.get_symbol()
        if error_type == self.MISSING_DASH_OR_EQUALS:
            print("Error: expected a dash or equals symbol.")
        elif error_type == self.MISSING_ARROW_OR_EQUALS:
            print("Error: expected a right arrow or equals symbol.")
        elif error_type == self.MISSING_DASH_OR_COMMA:
            print("Error: expected a comma or dash.")
        elif error_type == self.MISSING_STRING:
            print("Error: expected a string.")
        elif error_type == self.MISSING_INTEGER:
            print("Error: expected an integer.")
        elif error_type == self.MISSING_ARROW:
            print("Error: expected a right arrow.")
        elif error_type == self.MISSING_EQUALS:
            print("Error: expected an equals symbol.")
        elif error_type == self.NOT_DEVICE_NAME or error_type == self.devices.BAD_DEVICE:
            arrow_pos = self._seek_error(current_line, "=")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: This device type does not match any code known by this logic simulator. " \
            "Valid devices are AND, CLOCK, DTYPE, NAND, NOR, OR, SWITCH, XOR.")
        elif error_type == self.MISSING_COMMA:
            print("Error: expected a comma.")
        elif error_type == self.MISSING_DEVICES_HEADER:
            print("Error in format: Missing the section header keyword for devices.")
        elif error_type == self.MISSING_CONNECTIONS_HEADER:
            print("Error in format: Missing the section header keyword for connections.")
        elif error_type == self.MISSING_MONITORS_HEADER:
            print("Error in format: Missing the section header keyword for monitors.")
        elif error_type == self.MISSING_END_HEADER:
            print("Error in format: Missing the end-of-file keyword.")
        elif error_type == self.network.INPUT_TO_INPUT:
            arrow_pos = self._seek_error(current_line, "=")
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
            arrow_pos = self._seek_error(current_line, ">")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: A connection's second port must be an input port.")
        elif error_type == self.network.INPUT_CONNECTED:
            arrow_pos = self._seek_error(current_line, ">")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: There is already a connection leading to the specified input port.")
        elif error_type == self.network.PORT_ABSENT:
            print("Error: The specified device does not have a port with this ID.")
        elif error_type == self.network.DEVICE_ABSENT or error_type == self.network.DEVICE_ABSENT:
            print("Error: No device with this ID has been defined.")
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
            print("Error: A CLOCK device’s qualifier must be a non-zero integer.")
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
            print("Error: A SWITCH device may only have an qualifier of 0 or 1.")
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
            print("Error: The qualifier for this type of logic gate must be between 2 and 16.")
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
            arrow_pos = self._seek_error(current_line, ",")
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
            arrow_pos = self._seek_error(current_line, "=")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: The specified port is an input port or not defined." \
            " Monitors may only connect to output ports.")
        elif error_type == self.monitors.MONITOR_PRESENT:
            arrow_pos = self._seek_error(current_line, "=")
            print("Error in line:")
            print(current_line)
            i = 0
            while i < arrow_pos:
                arrow_str = arrow_str + " "
                i += 1
            arrow_str = arrow_str + "^"
            print(arrow_str)
            print("Error: There is already a monitor connected to this output port.")

    def _seek_error(current_line,target):
        return current_line.find(target)

    def _name(self, current_line):
        name = ""
        while (self.symbol.type == self.scanner.STRING or self.symbol.type == self.scanner.INTEGER
                or self.symbol.type == self.scanner.UNDERSCORE):
            name = name + self.symbol.id
            self.symbol = self.scanner.get_symbol()
        current_line = current_line + name
        if not (self.symbol.type == self.scanner.EQUALS or self.symbol.type == self.scanner.DASH):
            self._error(self.MISSING_DASH_OR_EQUALS, current_line, "standard")
        else:
            return name
        
    def _portID(self, current_line):
        portID = ""
        if self.symbol.type == self.STRING:
            portID = portID + self.symbol.id
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.INTEGER:
                portID = portID + str(self.symbol.ID)
                self.symbol = self.scanner.get_symbol()
            current_line = current_line + portID
            if not (self.symbol.type == self.scanner.ARROW or self.symbol.type == self.scanner.EQUALS):
                self._error(self.MISSING_ARROW_OR_EQUALS, current_line, "standard")
            else:
                return portID
        else:
            self._error(self.MISSING_STRING, current_line, "standard")

    def _signalID(self, current_line):
        deviceID = self._name("")
        current_line = current_line + deviceID
        if self.symbol.type == self.scanner.DASH:
            self.symbol = self.scanner.get_symbol()
            portID = self._portID(current_line)
            return [deviceID, portID]
        else:
            if not self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.ARROW:
                self._error(self.MISSING_DASH_OR_COMMA, current_line, "standard")
            else:
                return [deviceID, ""] #Not quite sure what this needs to be yet?
            
    def _devicetype(self, current_line):
        if self.symbol.type == self.scanner.DEVICE_TYPE:
            devicetype = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            return devicetype
        else:
            self._error(self.NOT_DEVICE_TYPE, current_line, "standard")
    
    def _device(self):
        deviceID = self._name("")
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
                    qualifier = self.symbol.ID()
                    current_line = current_line + qualifier
                    self.symbol = self.scanner.get_symbol()
                else:
                    self._error(self.MISSING_INTEGER, current_line, "standard") 
            elif self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                current_line = current_line + ","
                qualifier = None
            else:
                self._error(self.MISSING_SLASH, current_line, "standard") 
        else:
            self._error(self.MISSING_EQUALS, current_line, "standard") 
        if self.error_count == 0:
            error_type = self._make_device(device, deviceID, qualifier)
            if error_type != self.devices.NO_ERROR:
                self._error(error_type, current_line, "seek")

    def _make_device(self, device, deviceID, qualifier):
        if device in ["AND", "OR", "NAND", "NOR", "XOR"]:
            error = self.devices.make_gate(deviceID, device, qualifier)
        elif device == "CLOCK":
            error = self.devices.make_clock(deviceID, qualifier)
        elif device == "SWITCH":
            error = self.devices.make_clock(deviceID, qualifier)
        elif device == "DTYPE":
            error = self.devices.make_d_type(deviceID)
        else:
            error = self.devices.NO_ERROR
        return error
    

    def _connection(self):
        connectionID = self._name("")
        current_line = connectionID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            signal1 = self._signalID(current_line)
            current_line = current_line + signal1
            if self.symbol.type == self.scanner.ARROW:
                current_line = current_line + ">"
                self.symbol = self.scanner.get_symbol()
                signal2 = self._signalID(current_line)
                current_line = current_line + signal2
            else:
                self._error(self.MISSING_ARROW, current_line, "standard")
        else:
            self._error(self.MISSING_EQUALS, current_line, "standard") 
        if self.error_count == 0:
            error_type = self.network.make_connection(signal1[0], signal1[1], signal2[0], signal2[1])
            if error_type != self.network.NO_ERROR:
                self._error(error_type, current_line, "seek")
    
    def _monitor(self):
        monitorID = self._name("")
        current_line = current_line + monitorID
        if self.symbol.type == self.scanner.EQUALS:
            current_line = current_line + "="
            self.symbol = self.scanner.get_symbol()
            port = self._signalID(current_line)
            current_line = current_line + port
        else:
            self._error(self.MISSING_EQUALS, current_line, "standard") 
        if self.error_count == 0:
            error_type = self.monitors.make_monitor(port[0], port[1])
            if error_type != self.monitors.NO_ERROR:
                self._error(error_type, current_line, "seek")

    def _devices_list(self):
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            self._device()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._device()
        else:
            self._error(self.MISSING_DEVICES_HEADER, None, "end")

    def _connections_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS_ID):
            self.symbol = self.scanner.get_symbol()
            self._connection()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._connection()
        else:
            self._error(self.MISSING_CONNECTIONS_HEADER, None, "end")

    def _monitors_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITORS_ID):
            self.symbol = self.scanner.get_symbol()
            self._monitor()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._monitor()
            if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID):
                self._error(self.MISSING_END_HEADER, None, "stopped")
        else:
            self._error(self.MISSING_MONITORS_HEADER, None, "end")     
    
    def parse_network(self):
        """Parse the circuit definition file."""
        self.error_count = 0
        self._devices_list()
        self._connections_list()
        self._monitors_list()
        if self.error_count == 0:
            return True
        else:
            return False
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.


