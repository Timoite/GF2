"""Implement the graphical user interface for the Logic Simulator."""

import wx
from wx import ArtProvider
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
import sys


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    instances = []

    def __init__(self, parent, monitor_name):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.monitor_name = monitor_name
        self.parent = parent
        MyGLCanvas.instances.append(self)  # Keep a record of all canvases

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.monitors_dictionary = None


    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        self.initial_size = self.GetClientSize()

    def render_signal(self, monitors_dictionary, devices, cycles_completed):
        """Render the latest simulation."""
        self.monitors_dictionary = monitors_dictionary
        self.devices = devices
        self.cycles_completed = cycles_completed
        self.render()

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Get values to draw
        try:
            [device_id, output_id] = \
                self.devices.get_signal_ids(self.monitor_name)
            signal_list = self.monitors_dictionary[self.monitor_name, output_id]

            i = 0
            y_HIGH = 40
            y_LOW = 20
            dx = 8
            scalef = (self.initial_size.width-2*dx)/(self.cycles_completed*dx)
            if scalef < 1:
                GL.glScalef(scalef, 1.0, 1.0)

            # Draw a sample signal trace
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for signal in signal_list:
                x = (i * dx) + 0.5 * dx
                x_next = (i * dx) + dx
                if signal == self.devices.HIGH:
                    y = y_HIGH
                    y_next = y_HIGH
                if signal == self.devices.LOW:
                    y = y_LOW
                    y_next = y_LOW
                if signal == self.devices.RISING:
                    y = y_LOW
                    y_next = y_HIGH
                if signal == self.devices.FALLING:
                    y = y_HIGH
                    y_next = y_LOW
                if signal == self.devices.BLANK:
                    i += 1
                    continue
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y_next)
                i += 1
            GL.glEnd()

            if scalef < 1:
                GL.glScalef(1/scalef, 1.0, 1.0)
        # if the sim has not been run yet
        except AttributeError:
            pass

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render()

    def on_size(self, event):
        """Handle the size event."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glViewport(0, 0, size.width, size.height)
        event.Skip()


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.
    """

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(400, 400))
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.names = None
        self.devices = None
        self.network = None
        self.monitors = None
        self.cycles_completed = 0

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        main_sizer.Add(upper_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(lower_sizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

        io_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        upper_sizer.Add(io_sizer, 2, wx.EXPAND | wx.RIGHT, 10)
        upper_sizer.Add(switches_sizer, 1, wx.EXPAND, 0)

        self.fileio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.total_sizer = wx.BoxSizer(wx.HORIZONTAL)
        io_sizer.Add(self.fileio_sizer, 0, wx.ALL | wx.CENTER, 5)
        io_sizer.Add(self.cycles_sizer, 0, wx.TOP | wx.CENTER, 15)
        io_sizer.Add(self.run_cont_sizer, 0, wx.ALL | wx.CENTER, 10)
        io_sizer.Add(self.total_sizer, 0, wx.BOTTOM | wx.CENTER, 5)

        # Configure the widgets

        # File io widgets
        open_image = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        open_button = wx.BitmapButton(self, wx.ID_ANY, open_image)
        self.fileio_sizer.Add(open_button, 1, wx.RIGHT, 5)
        quit_image = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        quit_button = wx.BitmapButton(self, wx.ID_ANY, quit_image)
        self.fileio_sizer.Add(quit_button, 1, wx.LEFT, 5)

        # Cycles widgets
        text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.cycles_sizer.Add(text, 1, wx.CENTER | wx.RIGHT, 10)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, '20')
        self.cycles_sizer.Add(self.spin, 0, wx.CENTER)

        # Run and continue widgets
        run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_cont_sizer.Add(run_button, 1, wx.CENTER | wx.RIGHT, 10)
        cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.run_cont_sizer.Add(cont_button, 1, wx.CENTER)

        # Total cycles widgets
        text = wx.StaticText(self, wx.ID_ANY, "Total Cycles: ")
        self.total_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        self.total_cycles_text = \
            wx.StaticText(self, wx.ID_ANY, str(self.cycles_completed))
        self.total_sizer.Add(self.total_cycles_text, 0, wx.CENTER)

        # Switches widgets
        text = wx.StaticText(self, wx.ID_ANY, "Switches")
        switches_sizer.Add(text, 0, wx.CENTER)
        self.switch_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        switches_sizer.Add(self.switch_rows_sizer, 0, wx.EXPAND | wx.CENTER)

        # Monitor widgets
        text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        lower_sizer.Add(text, 1, wx.ALL | wx.CENTER, 10)

        self.monitor_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scrolled_panel.SetScrollRate(10, 10)
        self.scrolled_panel.SetSizer(self.monitor_rows_sizer)
        lower_sizer.Add(self.scrolled_panel, 100, wx.EXPAND)
        self.monitor_rows_sizer.Fit(self.scrolled_panel)

        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_sizer.Add(add_sizer, 0, wx.EXPAND)
        add_image = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
        add_button = wx.BitmapButton(self, wx.ID_ANY, add_image)
        add_sizer.Add(add_button, 0, wx.ALL, 20)
        self.choice = wx.Choice(self, choices=[])
        add_sizer.Add(self.choice, 0, wx.CENTER | wx.RIGHT, 15)

        # Bind events to widgets
        open_button.Bind(wx.EVT_BUTTON, self.OpenFile)
        quit_button.Bind(wx.EVT_BUTTON, self.Quit)
        run_button.Bind(wx.EVT_BUTTON, self.Run)
        cont_button.Bind(wx.EVT_BUTTON, self.Continue)
        add_button.Bind(wx.EVT_BUTTON, self.CreateMonitor)

        # Set screen size
        self.SetSizeHints(500, 500)
        self.SetSize(600, 600)
        self.SetSizer(main_sizer)
        self.SetPosition((0, 39))

    def clear_widgets(self):
        self.switch_rows_sizer.Clear(True)
        self.monitor_rows_sizer.Clear(True)
        self.total_cycles_text.SetLabel(str(self.cycles_completed))
        MyGLCanvas.instances = []

    def AddSwitch(self, switch_id, switch_state):
        """Add a switch to GUI."""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switch_rows_sizer.Add(switch_sizer, 0, wx.CENTER | wx.ALL, 5)
        text = wx.StaticText(self, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self, wx.ID_ANY, "", choices=['0', '1'])
        switch_radiobox.SetSelection(switch_state)
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)
        switch_radiobox.Bind(wx.EVT_RADIOBOX, lambda evt,
                             temp=switch_id: self.OnSwitch(evt, temp))
        self.Layout()

    def OnSwitch(self, event, switch_id):
        """Handle event when a switch is toggled."""
        switch_state = event.GetSelection()
        if not self.devices.set_switch(switch_id, switch_state):
            self.Error("Invalid switch.")

    def CreateMonitor(self, event):
        """Create a new monitor."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            self.Error("Please open file before creating monitor.")
            return
        
        print("in create monitor")

        # Get which signal to add
        signal_int = self.choice.GetSelection()
        signal_name = self.all_signal_list[signal_int]
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)

        monitor_error = self.monitors.make_monitor(device_id, output_id, self.cycles_completed)
        if monitor_error == self.monitors.NO_ERROR:
            print("Successfully made monitor.")
            # Add to gui
            self.AddMonitor(signal_name)
        else:
            print("Error! Could not make monitor.")

    def AddMonitor(self, signal_name):
        """Add a monitor that already exists to GUI."""
        monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pos = len(self.monitor_rows_sizer.GetChildren())

        self.monitor_rows_sizer.Add(monitor_sizer, 0, wx.EXPAND, 0)
        minus_image = wx.ArtProvider.GetBitmap(wx.ART_MINUS)
        zap_button = wx.BitmapButton(self.scrolled_panel, wx.ID_ANY, minus_image)
        text = wx.StaticText(self.scrolled_panel, wx.ID_ANY, signal_name)
        text.SetMinSize((100, -1))
        monitor_sizer.Add(zap_button, 0, wx.CENTER | wx.ALL, 20)
        monitor_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 10)
        self.canvas = MyGLCanvas(self.scrolled_panel, signal_name)
        monitor_sizer.Add(self.canvas, 1, wx.EXPAND | wx.CENTER | wx.ALL, 5)

        self.scrolled_panel.FitInside()
        self.Layout()

        zap_button.Bind(wx.EVT_BUTTON,
                        lambda evt, temp=pos, temp2=signal_name:
                        self.ZapMonitor(evt, temp, temp2))

    def ZapMonitor(self, event, pos, signal_name):
        """Remove the specified monitor."""
        # Remove from monitors
        [device, port] = self.devices.get_signal_ids(signal_name)
        if self.monitors.remove_monitor(device, port):
            # Remove from GUI
            self.monitor_rows_sizer.GetChildren()[pos].DeleteWindows()
            self.scrolled_panel.FitInside()
            self.Layout()
        else:
            self.Error("Could not zap monitor.")

    def OpenFile(self, event):
        """Open a file specified by the user."""
        openFileDialog = wx.FileDialog(
            self, "Open txt file", "", "",
            wildcard="TXT files (*.txt)|*.txt",
            style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        self.path = openFileDialog.GetPath()
        print("File chosen =", self.path)
        self.cycles_completed = 0
        self.clear_widgets()
        self.init_sim()

    def init_sim(self):

        # Initialise instances of the four inner simulator classes
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)

        scanner = Scanner(self.path, self.names)
        parser = Parser(self.names,
                        self.devices, self.network, self.monitors, scanner)
        if not parser.parse_network():
            self.Error("Unable to parse file.")
            return

        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            switch = self.devices.get_device(switch_id)
            switch_state = switch.switch_state
            self.AddSwitch(switch_id, switch_state)

        [monitored_signal_list, non_monitored_signal_list] = \
            self.monitors.get_signal_names()
        self.all_signal_list = monitored_signal_list + \
            non_monitored_signal_list

        self.choice.SetItems(self.all_signal_list)

        for monitored_signal_name in monitored_signal_list:
            self.AddMonitor(monitored_signal_name)

    def run_network(self):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        # Handle the case that no file has yet been opened
        if not self.monitors:
            self.Error("Please open a file first")
            return

        cycles = self.spin.GetValue()

        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.Error("Network oscillating.")
                return False

        self.cycles_completed += cycles
        self.total_cycles_text.SetLabel(str(self.cycles_completed))

        for canvas in MyGLCanvas.instances:
            canvas.render_signal(self.monitors.monitors_dictionary,
                                 self.devices, self.cycles_completed)

        return True

    def Run(self, event):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        self.clear_widgets()
        self.init_sim()
        self.run_network()

    def Continue(self, event):
        """Continue a previously run simulation."""
        if self.cycles_completed == 0:
            self.Error("Nothing to continue. Please run first.")
        else:
            self.run_network()
        

    def Error(self, error_msg):
        """Create error box."""
        wx.MessageBox(error_msg, 'Error', wx.OK | wx.ICON_ERROR)

    def Quit(self, event):
        sys.exit()