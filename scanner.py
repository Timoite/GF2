"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

import sys


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names
        try:
            self.file = open(path, 'r')
        except FileNotFoundError:
            print(f"File {path} not found.")
            sys.exit()
        self.contents = self.file.read()
        self.file.close()

        '''
        # define
        self.self.devices_found = 0
        self.self.devices_index = 0
        self.connection_found = 0
        self.connection_index = 0
        self.monitors_found = 0
        self.monitors_index = 0
        '''

        self._find()

        self.devices = self.contents[self.devices_index+7:self.connections_index].replace(" ", "").replace("\n", "")
        self.connections = self.contents[self.connections_index+11:self.monitors_index].replace(" ", "").replace("\n", "")
        self.monitors = self.contents[self.monitors_index+8:].replace(" ", "").replace("\n", "")

        '''
        print(self.devices)
        print("")
        print(self.connections)
        print("")
        print(self.monitors)
        '''


    
    def _find(self):

        self.self.devices_found = self.connections_found = self.monitors_found = 0
        self.self.devices_index = self.connections_index = self.monitors_index = -1 # not found yet
        i = 0
        
        while i < len(self.contents) - 10:
            if self.contents[i:i+7] == "DEVICES":
                if self.devices_found == 1:
                    print("File self.contents Error! There should only be one DEVICES header.")
                    sys.exit()
                else:
                    self.devices_found = 1
                    self.devices_index = i
            elif self.contents[i:i+11] == "CONNECTIONS":
                if self.connections_found == 1:
                    print("File self.contents Error! There should only be one CONNECTIONS header.")
                    sys.exit()
                else:
                    self.connections_found = 1
                    self.connections_index = i
            elif self.contents[i:i+8] == "MONITORS":
                if self.monitors_found == 1:
                    print("File self.contents Error! There should only be one MONITORS header.")
                    sys.exit()
                else:
                    self.monitors_found = 1
                    self.monitors_index = i
            i += 1
        
        if self.devices_found == 0:
            print("File Contents Error! The file must include a DEVICES header.")
            sys.exit()
        if self.connections_found == 0:
            print("File Contents Error! The file must include a CONNECTIONS header.")
            sys.exit()
        if self.monitors_found == 0:
            print("File Contents Error! The file must include a MONITORS header.")
            sys.exit()
        if (self.devices_index > self.connections_index or self.devices_index > self.monitors_index or self.connections_index > self.monitors_index):
            print("File Contents Error! The file's headings must be in the order DEVICES, CONNECTIONS, MONITORS.")
            sys.exit()
        

        

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
