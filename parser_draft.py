devices_string = "SWITCH_1=SWITCH/1,SWITCH_2=SWITCH/0,CLK_1=CLOCK/3,NOT_1=NOT,NOR_1=NOR/2,DTYPE_1=DTYPE,"
connections_string = "WIRE_1=SWITCH_1>NOT_1,WIRE_2=NOT_1>NOR_1-I1,WIRE_3=SWITCH_2>NOR_1-I2,WIRE_4=NOR_1>DTYPE_1-DATA,WIRE_5=CLK_1>DTYPE_1-CLK,"
monitors_string = "MONITOR_1=DTYPE_1-Q,"

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
    errors = ["", "Device name invalid: expected an alphabetical string followed by a single '_' , a number, and a '='", 
              "Device type invalid: expected an alphabetical string followed by a '/' or ','", 
              "Device qualifier invalid: expected a numerical string followed by a ','"]
    while i < len(string):
        if error_code != 0:
            error_string = error_string + string[i]
            if string[i] == ",":
                print("Error in following string: " + error_string)
                print(errors[error_code])
                error_string = ""
                error_code = 0
        else:
            current_substring = current_substring + string[i]
            if name_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "=" or string[i] == "_"):
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
                if not (string[i].isalpha() or string[i] == "/" or string[i] == ","):
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

def connection_parser(string):
    i = 0
    connection_names = []
    connection_output_devices = []
    connection_output_ports = []
    connection_input_devices = []
    connection_input_ports = []
    name_found = 0
    current_name = ""
    name_underscores = 0
    input_name_found = 0
    current_input_name = ""
    input_underscores = 0
    input_port_found = 0
    current_input_port = 0
    output_name_found = 0
    current_output_name = ""
    output_underscores = 0
    output_letters = 0
    current_substring = ""
    error_string = ""
    error_code = 0
    errors = ["", "Connection name invalid: expected an alphabetical string followed by a single '_' , a number, and a '='", 
              "Device type invalid: expected an alphabetical string followed by a single '_' , a number, and a '-' or '>'", 
              "Port type invalid: expected either an alphanumeric string followed by a '>', or simply a '>' for a single-port device", 
              "Device type invalid: expected an alphabetical string followed by a single '_' , a number, and a '-' or ','",
              "Port type invalid: expected either an alphanumeric string followed by an ',', or a blank field for a single-port device"]
    while i < len(string):
        if error_code != 0:
            error_string = error_string + string[i]
            if string[i] == ",":
                print("Error in following string: " + error_string)
                print(errors[error_code])
                error_string = ""
                error_code = 0
        else:
            current_substring = current_substring + string[i]
            if name_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "=" or string[i] == "_"):
                    error_code = 1
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                elif string[i].isalpha():
                    if name_underscores == 1:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                elif string[i].isdigit():
                    if name_underscores == 0:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                elif string[i] == "_":
                    if name_underscores == 0:
                        name_underscores += 1
                    else:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                elif string[i] == "=":
                    if name_underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[1])
                        current_substring = ""
                        name_underscores = 0
                    else:
                        current_name = current_substring[:-1]
                        current_substring = ""
                        name_found = 1
            elif input_name_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "_" or string[i] == ">" or string[i] == "-"):
                    error_code = 2
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                    name_found = 0
                    current_name = ""
                    input_underscores = 0
                elif string[i].isalpha():
                    if input_underscores == 1:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        input_underscores = 0
                elif string[i].isdigit():
                    if input_underscores == 0:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        input_underscores = 0
                elif string[i] == "_":
                    if input_underscores == 0:
                        input_underscores += 1
                    else:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        input_underscores = 0
                elif string[i] == ">" or string[i] == "-":
                    if input_underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[2])
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        input_underscores = 0
                    else:
                        current_input_name = current_substring[:-1]
                        current_substring = ""
                        input_name_found = 1
                        if string[i] == ">":
                            input_port_found = 1
                            current_input_port = None
            elif input_port_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == ">"):
                    error_code = 3
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                    name_found = 0
                    current_name = ""
                    name_underscores = 0   
                    input_name_found = 0
                    current_input_name = ""
                    input_underscores = 0
                elif string[i] == ">":
                    if current_substring == ">":
                        current_input_port = None
                        input_port_found = 1
                        current_substring = ""
                    else:
                        current_input_port = current_substring[:-1]
                        current_substring = ""
                        input_port_found = 1
            elif output_name_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "-" or string[i] == "_" or string[i] == ","):
                    error_code = 4
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                    name_found = 0
                    current_name = ""
                    name_underscores = 0   
                    input_name_found = 0
                    current_input_name = ""
                    input_underscores = 0
                    current_input_port = ""
                    input_port_found = 0
                    output_underscores = 0
                elif string[i].isalpha():
                    if output_underscores == 1:
                        error_code = 4
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""  
                        input_name_found = 0
                        current_input_name = ""
                        input_underscores = 0
                        current_input_port = ""
                        input_port_found = 0
                        output_underscores = 0
                elif string[i].isdigit():
                    if output_underscores == 0:
                        error_code = 4
                        error_string = current_substring
                        current_substring = ""
                        name_found = 0
                        current_name = ""
                        name_underscores = 0   
                        input_name_found = 0
                        current_input_name = ""   
                        input_port_found = 0
                        input_underscores = 0
                        current_input_port = ""
                        output_underscores = 0
                elif string[i] == "_":
                    if output_underscores == 0:
                        output_underscores += 1
                    else:
                        error_code = 4
                        error_string = current_substring
                        current_substring = ""
                        name_found = 0
                        current_name = ""
                        name_underscores = 0   
                        input_name_found = 0
                        current_input_name = ""
                        input_underscores = 0  
                        current_input_port = ""
                        input_port_found = 0
                        output_underscores = 0
                elif string[i] == "-" or string[i] == ",":
                    if output_underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[4])
                        current_substring = ""
                        name_found = 0
                        current_name = ""
                        name_underscores = 0   
                        input_name_found = 0
                        current_input_name = ""
                        input_underscores = 0
                        current_input_port = ""
                        input_port_found = 0
                        output_underscores = 0
                    else:
                        current_output_name = current_substring[:-1]
                        current_substring = ""
                        output_name_found = 1
                        if string[i] == ",":
                            connection_names.append(current_name)
                            connection_input_devices.append(current_input_name)
                            connection_input_ports.append(current_input_port)
                            connection_output_devices.append(current_output_name)
                            connection_output_ports.append(None)
                            current_substring = ""
                            name_found = 0
                            current_name = ""
                            name_underscores = 0   
                            input_name_found = 0
                            current_input_name = ""
                            input_underscores = 0
                            current_input_port = ""
                            input_port_found = 0
                            output_underscores = 0
                            output_name_found = 0
                            current_output_name = ""
            else:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == ","):
                    error_code = 5
                    error_string = current_substring
                    name_found = 0
                    current_name = ""
                    name_underscores = 0   
                    input_name_found = 0
                    current_input_name = ""
                    input_underscores = 0
                    current_input_port = ""
                    input_port_found = 0
                    output_underscores = 0
                    output_name_found = 0
                    current_output_name = ""
                elif string[i] == ",":
                    if current_substring == ",":
                        connection_names.append(current_name)
                        connection_input_devices.append(current_input_name)
                        connection_input_ports.append(current_input_port)
                        connection_output_devices.append(current_output_name)
                        connection_output_ports.append(None)
                        current_substring = ""
                        name_found = 0
                        current_name = ""
                        name_underscores = 0   
                        input_name_found = 0
                        current_input_name = ""
                        input_underscores = 0
                        current_input_port = ""
                        input_port_found = 0
                        output_underscores = 0
                        output_name_found = 0
                        current_output_name = ""
                    else:
                        connection_names.append(current_name)
                        connection_input_devices.append(current_input_name)
                        connection_input_ports.append(current_input_port)
                        connection_output_devices.append(current_output_name)
                        connection_output_ports.append(current_substring[:-1])
                        current_substring = ""
                        name_found = 0
                        current_name = ""
                        name_underscores = 0   
                        input_name_found = 0
                        current_input_name = ""
                        input_underscores = 0
                        current_input_port = ""
                        input_port_found = 0
                        output_underscores = 0
                        output_name_found = 0
                        current_output_name = ""
        i += 1
    return(connection_names, connection_input_devices, connection_input_ports, connection_output_devices, connection_output_ports)
                    
def monitors_parser(string):
    i = 0
    monitors_names = []
    monitors_devices = []
    monitors_ports = []
    name_found = 0
    current_name = ""
    name_underscores = 0
    device_found = 0
    current_device = ""
    device_underscores = 0
    current_substring = ""
    error_string = ""
    error_code = 0
    errors = ["", "Connection name invalid: expected an alphabetical string followed by a single '_' , a number, and a '='", 
              "Device type invalid: expected an alphabetical string followed by a single '_' , a number, and a '-' or ','",
              "Port type invalid: expected either an alphanumeric string followed by an ',', or a blank field for a single-port device"]
    while i < len(string):
        if error_code != 0:
            error_string = error_string + string[i]
            if string[i] == ",":
                print("Error in following string: " + error_string)
                print(errors[error_code])
                error_string = ""
                error_code = 0
        else:
            current_substring = current_substring + string[i]
            if name_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "=" or string[i] == "_"):
                    error_code = 1
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                elif string[i].isalpha():
                    if name_underscores == 1:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                elif string[i].isdigit():
                    if name_underscores == 0:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                elif string[i] == "_":
                    if name_underscores == 0:
                        name_underscores += 1
                    else:
                        error_code = 1
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                elif string[i] == "=":
                    if name_underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[1])
                        current_substring = ""
                        name_underscores = 0
                    else:
                        current_name = current_substring[:-1]
                        current_substring = ""
                        name_found = 1
            elif device_found == 0:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == "-" or string[i] == "_" or string[i] == ","):
                    error_code = 2
                    error_string = current_substring
                    current_substring = ""
                    name_underscores = 0
                    name_found = 0
                    current_name = ""
                    device_underscores = 0
                elif string[i].isalpha():
                    if device_underscores == 1:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                elif string[i].isdigit():
                    if device_underscores == 0:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                elif string[i] == "_":
                    if device_underscores == 0:
                        device_underscores += 1
                    else:
                        error_code = 2
                        error_string = current_substring
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                elif string[i] == "-" or string[i] == ",":
                    if device_underscores == 0 or current_substring[len(current_substring) - 2] == "_":
                        print("Error in following string: " + current_substring)
                        print(errors[2])
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                    else:
                        current_device = current_substring[:-1]
                        current_substring = ""
                        device_found = 1
                        if string[i] == ",":
                            monitors_names.append(current_name)
                            monitors_devices.append(current_device)
                            monitors_ports.append(None)
                            current_substring = ""
                            name_underscores = 0
                            name_found = 0
                            current_name = ""
                            device_underscores = 0
                            device_found = 0
                            current_device = ""
            else:
                if not (string[i].isalpha() or string[i].isdigit() or string[i] == ","):
                    error_code = 3
                    error_string = current_substring
                    name_underscores = 0
                    name_found = 0
                    current_name = ""
                    device_underscores = 0
                    device_found = 0
                    current_device = ""
                elif string[i] == ",":
                    if current_substring == ",":
                        monitors_names.append(current_name)
                        monitors_devices.append(current_device)
                        monitors_ports.append(None)
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                        device_found = 0
                        current_device = ""
                    else:
                        monitors_names.append(current_name)
                        monitors_devices.append(current_device)
                        monitors_ports.append(current_substring[:-1])
                        current_substring = ""
                        name_underscores = 0
                        name_found = 0
                        current_name = ""
                        device_underscores = 0
                        device_found = 0
                        current_device = ""
        i += 1
    return(monitors_names, monitors_devices, monitors_ports)

results = device_parser(devices_string)
print(results[0])
print(results[1])
print(results[2])
results2 = connection_parser(connections_string)
print(results2[0])
print(results2[1])
print(results2[2])
print(results2[3])
print(results2[4])
results3 = monitors_parser(monitors_string)
print(results3[0])
print(results3[1])
print(results3[2])