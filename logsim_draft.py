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

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner_original import Scanner
from parse import Parser
from userint import UserInterface
from gui_draft import Gui


def main(arg_list):
    app = wx.App()
    gui = Gui("Logic Simulatorinator")
    gui.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
