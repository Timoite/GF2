#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys
import os

import wx
import builtins

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface

from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            # Initialise instances of the four inner simulator classes
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface
        if len(arguments) == 1:
            [path] = arguments
        else:
            path = None

        app = wx.App()

        # Internationalisation setup
        builtins._ = wx.GetTranslation
        # Check the environment variable LANG
        lang = os.environ.get('LANG', 'en_US.UTF-8')
        # Get the system language
        system_lang = wx.Locale.GetSystemLanguage()
        # print(f"System language: {system_lang}, Environment LANG: {lang}")

        if ('zh' in lang or
            system_lang in [wx.LANGUAGE_CHINESE,
                            wx.LANGUAGE_CHINESE_SIMPLIFIED]):
            locale = wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
        else:
            locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        locale.AddCatalogLookupPathPrefix('locale')
        locale.AddCatalog('logsim')

        gui = Gui(_("Logic Simulatorinator"), path)
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
