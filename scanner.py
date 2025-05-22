import sys

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
        print("\nNow opening file...")
        print("Path: " + path)
        try:
            file = open(path, "r")
        except FileNotFoundError:
            print("Error: file not found.")
        self.contents = file.read()
        file.close()
        self.names = names
        self.symbol_type_list = [self.KEYWORD, self.STRING, self.INTEGER,
                                  self.COMMA, self.ARROW, self.EQUALS, self.SLASH, self.DASH, self.UNDERSCORE]
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS"]
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID, self.END_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""

    def get_symbol(self):
        symbol = Symbol()
        self.skip_whitespace()
        if self.current_character.isalpha(): # string
            string = self.get_string()
            if string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.STRING
            symbol.id = self.names.lookup(string)
        elif self.current_character.isdigit(): # integer
            symbol.id = self.get_integer()
            symbol.type = self.INTEGER
        elif self.current_character == "=": # punctuation
            symbol.type = self.EQUALS
            self.advance()
        elif self.current_character == "-": # punctuation
            symbol.type = self.DASH
            self.advance()
        elif self.current_character == "/": # punctuation
            symbol.type = self.SLASH
            self.advance()
        elif self.current_character == ",": # punctuation
            symbol.type = self.COMMA
            self.advance()
        elif self.current_character == ">": # punctuation
            symbol.type = self.ARROW
            self.advance()
        elif self.current_character == "_": # punctuation
            symbol.type = self.UNDERSCORE
            self.advance()
        elif self.current_character == "": # end of file
            symbol.type = self.EOF
        else: # not a valid character
            self.advance()
        return symbol
        """Translate the next sequence of characters into a symbol."""
    
    def skip_whitespace(self):
    #Calls advance until the first character is not whitespace or a new line.
        exit = 0
        while exit == 0:
            self.advance()
            if self.current_character not in [" ", "/n"]:
                exit = 1

    def get_string(self):
        string = self.current_character
        exit = 0 
        while exit == 0:
            self.advance()
            if self.current_character.isalpha():
                string = string + self.current_character
            else:
                exit = 1
        return string


    def get_integer(self):
        integer = self.current_character
        exit = 0 
        while exit == 0:
            self.advance()
            if self.current_character.isdigit():
                integer = integer + self.current_character
            else:
                exit = 1
        return integer
    # As with get_string, but with digits instead of characters.

    def advance(self):
        self.current_character = self.contents[0]
        self.contents = self.contents[1]
        return(None)

