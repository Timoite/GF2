import sys

arguments = sys.argv[1:]
if len(arguments) != 1:
    print("Error! One command line argument is required.")
    sys.exit()

else:

    print("\nNow opening file...")
    print("Path: " + arguments[0])
    try:
        file = open(arguments[0], "r")
    except FileNotFoundError:
        print("Error: file not found.")
    contents = file.read()
    file.close()
    print(contents)
    devices_found = 0
    devices_index = 0
    connections_found = 0
    connections_index = 0
    monitors_found = 0
    monitors_index = 0
    i = 0
    while i < len(contents) - 10:
        if contents[i:i+7] == "DEVICES":
            if devices_found == 1:
                print("File Contents Error! There should only be one DEVICES header.")
                sys.exit()
            else:
                devices_found = 1
                devices_index = i
        elif contents[i:i+11] == "CONNECTIONS":
            if connections_found == 1:
                print("File Contents Error! There should only be one CONNECTIONS header.")
                sys.exit()
            else:
                connections_found = 1
                connections_index = i
        elif contents[i:i+8] == "MONITORS":
            if monitors_found == 1:
                print("File Contents Error! There should only be one MONITORS header.")
                sys.exit()
            else:
                monitors_found = 1
                monitors_index = i
        i += 1
    if devices_found == 0:
        print("File Contents Error! The file must include a DEVICES header.")
        sys.exit()
    if connections_found == 0:
        print("File Contents Error! The file must include a CONNECTIONS header.")
        sys.exit()
    if monitors_found == 0:
        print("File Contents Error! The file must include a MONITORS header.")
        sys.exit()
    if (devices_index > connections_index or devices_index > monitors_index or connections_index > monitors_index):
        print("File Contents Error! The file's headings must be in the order DEVICES, CONNECTIONS, MONITORS.")
        sys.exit()
    devices = contents[devices_index+7:connections_index].replace(" ", "")
    if devices == "":
        print("File Contents Error! The file must have at least one device.")
        sys.exit()
    devices = devices.replace("\n", "")
    devices = devices.upper()
    connections = contents[connections_index+11:monitors_index].replace(" ", "")
    if connections == "":
        print("File Contents Error! The file must have at least one connection.")
        sys.exit()
    connections = connections.replace("\n", "")
    connections = connections.upper()
    monitors = contents[monitors_index+8:].replace(" ", "")
    if monitors == "":
        print("File Contents Error! The file must have at least one monitor.")
        sys.exit()
    monitors = monitors.replace("\n", "")
    monitors = monitors.upper()
    print(devices)
    print(connections)
    print(monitors)