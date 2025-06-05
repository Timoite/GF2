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
        file.close()
        self.names = names
        self.symbol_type_list = [
            self.KEYWORD, self.DEVICE_TYPE, self.STRING,
            self.INTEGER, self.COMMA, self.ARROW,
            self.EQUALS, self.SLASH, self.DASH,
            self.UNDERSCORE, self.EOF
        ] = range(11)
        """These two lists are for keywords and device IDs,
        two special case string types from the EBNF that
        directly influence parser behaviour."""
        self.keywords_list = [
            "DEVICES", "CONNECTIONS",
            "MONITORS", "END"
        ]
        self.device_list = [
            "AND", "OR", "NAND", "NOR",
            "XOR", "CLOCK", "SWITCH", "DTYPE"
        ]

        # Look up ID from names
        [self.DEVICES_ID, self.CONNECTIONS_ID,
         self.MONITORS_ID, self.END_ID] = \
            self.names.lookup(self.keywords_list)
        [self.AND_ID, self.OR_ID, self.NAND_ID,
         self.NOR_ID, self.XOR_ID, self.CLOCK_ID,
         self.SWITCH_ID, self.DTYPE_ID] = \
            self.names.lookup(self.device_list)
        self._advance()

    def _skip_whitespace(self):
        """Skip whitespace and newlines in the file contents."""
        while True:
            if self.current_character not in [" ", "\n"]:
                break
            self._advance()

    def _skip_comment(self):
        """Skip a comment line starting and ending with '#'.
        This can be anywhere, including in the middle of a symbol."""
        while True:
            self._advance()
            if self.current_character == "#":
                self._advance()
                break
            elif self.current_character == "":
                # Prints an error if the comment is not closed.
                print("Error: comment not closed.")
                break

    def _get_string(self):
        """Return a string of consecutive letters.

        Skips comments if encountered.
        """
        string = ""
        while True:
            if self.current_character == "#":
                self._skip_comment()
            elif self.current_character.isalpha():
                string += self.current_character
                self._advance()
            else:  # Stop at the first non-letter character
                break
        return string

    def _get_integer(self):
        """Return a string of consecutive digits.

        Skips comments and whitespace if encountered.
        """
        integer = self.current_character
        while True:
            self._advance()
            if self.current_character == "#":
                self._skip_comment()
            elif self.current_character.isdigit():
                integer += self.current_character
            else:
                break
        return integer

    def _advance(self):
        """Advance to the next character in the file contents.
        If there are no characters left, return the end of file character."""
        try:
            self.current_character = self.contents[0]
            self.contents = self.contents[1:]
        except IndexError:
            self.current_character = ""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        # Create a new symbol to return
        symbol = Symbol()
        self._skip_whitespace()
        # Skip comments, if found, and leading whitespace
        if self.current_character == "#":
            self._skip_comment()
        self._skip_whitespace()
        if self.current_character.isalpha():  # Strings, keywords, device types
            string = self._get_string()
            if string in self.keywords_list:
                symbol.type = self.KEYWORD
            elif string in self.device_list:
                symbol.type = self.DEVICE_TYPE
            else:
                symbol.type = self.STRING
            symbol.id = self.names.lookup([string])[0]
        elif self.current_character.isdigit():  # Integers
            integer = self._get_integer()
            symbol.id = self.names.lookup([integer])[0]
            symbol.type = self.INTEGER
        elif self.current_character == "=":  # Singular punctuation
            symbol.type = self.EQUALS
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "-":  # And so forth
            symbol.type = self.DASH
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "/":
            symbol.type = self.SLASH
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == ",":
            symbol.type = self.COMMA
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == ">":
            symbol.type = self.ARROW
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "_":
            symbol.type = self.UNDERSCORE
            symbol.id = self.names.lookup(self.current_character)[0]
            self._advance()
        elif self.current_character == "":  # End of file
            symbol.type = self.EOF
        else:  # Out-of-alphabet characters do not have a defined type
            self._advance()
        print(f"Symbol created: {symbol.type}, ID: {symbol.id}")
        return symbol
