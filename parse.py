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

    def _error(self, error_type, stopping_symbol):
        self.error_count += 1

    def _name(self):
        name = ""
        while (self.symbol.type == self.scanner.STRING or self.symbol.type == self.scanner.INTEGER
                or self.symbol.type == self.scanner.UNDERSCORE):
            name = name + self.symbol.id
            self.symbol = self.scanner.get_symbol()
        if not (self.symbol.type == self.scanner.EQUALS or self.symbol.type == self.scanner.DASH):
            self._error()
        else:
            return name
        
    def _portID(self):
        portID = ""
        if self.symbol.type == self.STRING:
            portID = portID + self.symbol.id
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.INTEGER:
                portID = portID + str(self.symbol.ID)
                self.symbol = self.scanner.get_symbol()
            if not (self.symbol.type == self.scanner.ARROW or self.symbol.type == self.scanner.EQUALS):
                self._error()
            else:
                return portID
        else:
            self._error()

    def _signalID(self):
        deviceID = self._name()
        if self.symbol.type == self.scanner.DASH:
            self.symbol = self.scanner.get_symbol()
            portID = self._portID()
            return [deviceID, portID]
        else:
            if not self.symbol.type == self.scanner.COMMA:
                self._error()
            else:
                return [deviceID, ""] #Not quite sure what this needs to be yet?
            
    def _devicetype(self):
        if self.symbol.type == self.scanner.DEVICE_TYPE:
            devicetype = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            return devicetype
        else:
            self._error()
    
    def _device(self):
        deviceID = self._name()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            device = self._devicetype()
            if self.symbol.type == self.scanner.SLASH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INTEGER:
                    qualifier = self.symbol.ID()
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.error()
            elif self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                qualifier = None
            else:
                self._error()
        else:
            self._error() 
        if self.error_found == 0:
            error_type = self._make_device(device, deviceID, qualifier)
            if error_type != self.devices.NO_ERROR():
                self._error()

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
            error = self.error()
        return error
    

    def _connection(self):
        connectionID = self._name()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            signal1 = self._signalID()
            if self.symbol.type == self.scanner.ARROW:
                self.symbol = self.scanner.get_symbol()
                signal2 = self._signalID()
            else:
                self._error()
        else:
            self._error() 
        if self.error_found == 0:
            error_type = self.network.make_connection(signal1[0], signal1[1], signal2[0], signal2[1])
            if error_type != self.network.NO_ERROR():
                self._error()
    
    def _monitor(self):
        monitorID = self._name()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            port = self._signalID()
        else:
            self._error() 
        if self.error_found == 0:
            error_type = self.monitors.make_monitor(port[0], port[1])
            if error_type != self.monitors.NO_ERROR():
                self._error()

    def _devices_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            self._device()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._device()
            if not self.symbol.type == self.scanner.KEYWORD:
                self._error()
        else:
            self._error()

    def _connections_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS_ID):
            self.symbol = self.scanner.get_symbol()
            self._connection()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._connection()
            if not self.symbol.type == self.scanner.KEYWORD:
                self._error()
        else:
            self._error()

    def _monitors_list(self):
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITORS_ID):
            self.symbol = self.scanner.get_symbol()
            self._monitor()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._monitor()
            if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID):
                self._error()
        else:
            self._error()     
    
    def parse_network(self):
        self.error_count = 0
        self._devices_list()
        self._connections_list()
        self._monitors_list()
        if self.error_count == 0:
            """Parse the circuit definition file."""
            return True
        else:
            return False
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.


