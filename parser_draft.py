devices_string = "SWITCH_1=SWITCH/1,SWITCH_2=SWITCH/0,CLK_1=CLOCK/3,NOT_1=NOT,NOR_1=NOR/2,DTYPE_1=DTYPE,"
connections_string = "WIRE_1=SWITCH_1-O1>NOT_1-I1,WIRE_2=NOT_1-O1>NOR_1-I1,WIRE_3=SWITCH_2-O1>NOR_1-I2,WIRE_4=NOR_1-O1>DTYPE_1-I1,WIRE_5=CLK_1-O1>DTYPE_1-I2,"
monitors_string = "MONITOR_1=DTYPE_1-O1,"

def device_parser(string):
    i = 0
    device_names = []
    device_types = []
    device_qualifiers = []
    name_found = 0
    current_name = ""
    underscores = 0
    type_found = 0
    current_type = ""
    current_substring = ""
    error_string = ""
    error_code = 0
    errors = ["", "Device name invalid: expected an alphabetical string followed by a single _ , a number, and a =", 
              "Device type invalid: expected an uppercase alphabetical string followed by a / or ,", 
              "Device qualifier invalid: expected a numerical string followed by a ,"]
    while i < len(string):
        if error_code != 0:
            error_string = error_string + string[i]
            if string[i] == ",":
                print("Error in  following string: " + error_string)
                print(errors[error_code])
                error_string = ""
                error_code = 0
        else:
            current_substring = current_substring + string[i]
            if name_found == 0:
                if not ((string[i].isalpha() and string[i].isupper()) or string[i].isdigit() or string[i] == "=" or string[i] == "_"):
                    error_code = 1
                    error_string = current_substring
                    current_substring = ""
                elif string[i].isalpha():
                    if underscores == 1:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                elif string[i].isdigit():
                    if underscores == 0:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                elif string[i] == "_":
                    if underscores == 0:
                        underscores += 1
                    else:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                elif string[i] == "=":
                    if underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[1])
                        current_substring = ""
                    else:
                        current_name = current_substring[:-1]
                        current_substring = ""
                        name_found = 1
            elif type_found == 0:
                if not ((string[i].isalpha() and string[i].isupper()) or string[i] == "/" or string[i] == ","):
                    error_code = 2
                    error_string = current_substring
                    current_substring = ""
                    name_found = 0
                    underscores = 0
                    current_name = ""
                elif string[i] == "/":
                    if current_substring == "/":
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_found = 0
                        underscores = 0
                        current_name = ""
                    else:
                        current_type = current_substring[:-1]
                        current_substring = ""
                        type_found = 1
                elif string[i] == ",":
                    if current_substring == ",":
                        print("Error in following string: " + current_substring)
                        print(errors[2])
                        current_substring = ""
                        name_found = 0
                        underscores = 0
                        current_name = ""
                    else:
                        device_names.append(current_name)
                        device_types.append(current_substring[:-1])
                        device_qualifiers.append(None)
                        current_substring = ""
                        name_found = 0
                        underscores = 0
                        current_name = ""
            else:
                if not (string[i].isdigit() or string[i] == ","):
                    error_code = 3
                    error_string = current_substring
                    current_substring = ""
                    name_found = 0
                    underscores = 0
                    current_name = ""
                    type_found = 0
                    current_type = ""
                elif string[i] == ",":
                    if current_substring == ",":
                        print("Error in following string: " + current_substring)
                        print(errors[3])
                        current_substring = ""
                        name_found = 0
                        underscores = 0
                        current_name = ""
                        type_found = 0
                        current_type = ""
                    else:
                        device_names.append(current_name)
                        device_types.append(current_type)
                        device_qualifiers.append(current_substring[:-1])
                        current_substring = ""
                        name_found = 0
                        underscores = 0
                        type_found = 0
                        current_name = ""
                        current_type = ""
        i += 1
    return(device_names, device_types, device_qualifiers)

results = device_parser(devices_string)
print(results[0])
print(results[1])
print(results[2])