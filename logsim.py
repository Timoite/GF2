"""Runs the simulator."""

import sys
import wx
from gui import Gui


def main(arg_list):
    """Launch the simulatorinator."""
    app = wx.App()
    gui = Gui("Logic Simulatorinator")
    gui.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
