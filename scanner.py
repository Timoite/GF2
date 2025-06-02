"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


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
        # Checks file handling error
        print("\nNow opening file...")
        print("Path: " + path)
        try:
            file = open(path, "r")
        except FileNotFoundError:
            print("Error: file not found.")
        conte = file.read()
        self.contents = list(conte)
        print("File opened successfully.")
        # print("File contents: " + self.contents.__str__())
        file.close()
        self.names = names
        self.symbol_type_list = [self.KEYWORD, self.DEVICE_TYPE, self.STRING, self.INTEGER,
                                  self.COMMA, self.ARROW, self.EQUALS, self.SLASH, self.DASH, self.UNDERSCORE, self.EOF] = range(11)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS", "END"]
        self.device_list = ["AND", "OR", "NAND", "NOR", "XOR", "CLOCK", "SWITCH", "DTYPE"]

        # Look up ID from names
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID, self.END_ID] = self.names.lookup(self.keywords_list)
        [self.AND_ID, self.OR_ID, self.NAND_ID, self.NOR_ID, self.CLOCK_ID, self.SWITCH_ID, self.DTYPE_ID] = self.names.lookup(self.device_list)
        self._advance()

        
    
    def _skip_whitespace(self):
        """Calls _advance until the first character is not whitespace or a new line."""
        exit = 0
        while exit == 0:
            if self.current_character not in [" ", "\n"]:
                exit = 1
            else:
                self._advance()

    def _skip_comment(self):
        """skip comment by detecting and remove the line starting with the comment symbol '#'"""
        exit = 0
        while exit == 0:
            self._advance()
            if self.current_character == "#":
                self._advance()
                exit = 1

    def _get_string(self):
        """get the string (seperate by space)"""
        string = ""
        print("initilized string in _get_string: ", string)
        exit = 0 
        while exit == 0:
            if self.current_character == "#":
                self._skip_comment()
            elif self.current_character.isalpha():
                string = string + self.current_character
            else:
                exit = 1
            self._advance()
        return string


    def _get_integer(self):
        '''As with _get_string, but with digits instead of characters.'''
        integer = self.current_character
        exit = 0 
        while exit == 0:
            self._advance()
            if self.current_character == "#":
                self._skip_comment()
            elif self.current_character.isdigit():
                integer = integer + self.current_character
            else:
                exit = 1
        return integer
    # As with __get_string, but with digits instead of characters.

    def _advance(self):
        '''Used to _advance to the next character when the current character has been analyzed.'''
        self.current_character = self.contents[0]
        self.contents = self.contents[1:]

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        print("get_symbol called")
        print("current character:", self.current_character)
        # Create a new symbol to return
        symbol = Symbol()
        self._skip_whitespace()

        # we also need a comment handling if we allow comment 
        if self.current_character == "#":
            self._skip_comment()

        self._skip_whitespace()
        print("current character:",self.current_character)
        if self.current_character.isalpha(): # string
            string = self._get_string()
            print("get_symbol string:", string)
            if string in self.keywords_list:
                symbol.type = self.KEYWORD
            elif string in self.device_list:
                symbol.type == self.DEVICE_TYPE
            else:
                symbol.type = self.STRING
            symbol.id = self.names.lookup([string])[0]
            print("get_symbol id:", symbol.id)
        elif self.current_character.isdigit(): # integer
            integer = self._get_integer()
            symbol.id = self.names.lookup([integer])[0]
            symbol.type = self.INTEGER
        elif self.current_character == "=": # punctuation
            symbol.type = self.EQUALS
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "-": # punctuation
            symbol.type = self.DASH
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "/": # punctuation
            symbol.type = self.SLASH
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == ",": # punctuation
            symbol.type = self.COMMA
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == ">": # punctuation
            symbol.type = self.ARROW
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "_": # punctuation
            symbol.type = self.UNDERSCORE
            symbol.id = self.names.lookup(self.current_character)[0]
            print("underscore")
            self._advance()
        elif self.current_character == "": # end of file
            symbol.type = self.EOF
            symbol.id = self.names.lookup(self.current_character)[0]
        else: # not a valid character
            self._advance()
        
        return symbol


