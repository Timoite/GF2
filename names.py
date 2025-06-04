"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:
    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0
        self.names = []
        self.names_dict = {}

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        # num_error_codes is a positive integer
        if isinstance(num_error_codes, int) and num_error_codes < 1:
            raise ValueError(
                "Number of error codes must be a positive integer.")
        codes = []
        # loop through the number of error and assign them unique codes
        for i in range(num_error_codes):
            # error code count may not be 0 initially, so accumulate on it
            code = self.error_code_count + i
            codes.append(code)
        # update the error code count
        self.error_code_count += num_error_codes
        # update the error codes to the names list and dict
        for code in codes:
            if code not in self.names_dict:
                self.names.append(code)
                # matches the id definition below
                self.names_dict[code] = len(self.names) - 1
        return codes

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        Return None if the name string is not present in the names list
        """
        if name_string in self.names_dict:
            return self.names_dict[name_string]
        else:
            return None

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        if type(name_string_list) is not list:
            print(type(name_string_list))
            raise TypeError("name_string_list must be a list")
        ids = []
        for name_string in name_string_list:
            if name_string in self.names_dict:
                pass
            else:
                self.names.append(name_string)
                self.names_dict[name_string] = len(self.names) - 1
            ids.append(self.names_dict[name_string])
        return ids

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if name_id < 0 or not isinstance(name_id, int):
            raise ValueError("ID must be a non-negative integer.")
        elif name_id >= len(self.names):
            return None
        else:
            return self.names[name_id]
