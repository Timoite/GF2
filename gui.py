"""Implement the graphical user interface for the Logic Simulator."""

import wx
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

    """

    instances = {}  # Keep a record of all canvases

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
        self.monitors_dictionary = None
        MyGLCanvas.instances[monitor_name] = self  # Keep a record of canvases

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        self.initial_size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, self.initial_size.width, self.initial_size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, self.initial_size.width, 0,
                   self.initial_size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

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

        # Try to render signal
        try:
            # Get values to draw
            [device_id, output_id] = \
                self.devices.get_signal_ids(self.monitor_name)
            if "." in self.monitor_name:
                device_name = self.monitor_name[:(self.monitor_name.find("."))]
            else:
                device_name = self.monitor_name
            signal_list = self.monitors_dictionary[device_name,
                                                   output_id]

            # Scaling the drawing
            i = 0
            y_HIGH = 25
            y_LOW = 5
            dx = 8
            starting_x = dx / 2
            scalef = (self.initial_size.width - dx) \
                / (self.cycles_completed * dx)
            if scalef < 1:
                GL.glScalef(scalef, 1.0, 1.0)
                starting_x /= scalef

            # Drawing
            GL.glColor3f(1.0, 0.0, 0.0)  # signal trace is red
            GL.glBegin(GL.GL_LINE_STRIP)
            for signal in signal_list:
                x = (i * dx) + starting_x
                x_next = (i * dx) + starting_x + dx
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

            # Reset scaling
            if scalef < 1:
                GL.glScalef(1/scalef, 1.0, 1.0)

        # if the sim has not been run yet
        except AttributeError:
            pass

        """We have been drawing to the back buffer, flush the graphics pipeline
        and swap the back buffer to the front"""
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
        """Initialise static widgets and layout."""
        super().__init__(parent=None, title=title, size=(400, 400))
        self.names = None
        self.devices = None
        self.network = None
        self.monitors = None
        self.cycles_completed = 0

        self.OPEN_ID = 998
        self.QUIT_ID = 999

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(100, "&Open")
        fileMenu.Append(101, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Configure the toolbar
        toolbar=self.CreateToolBar()
        myimage=wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddTool(self.OPEN_ID,"Open file", myimage)
        myimage=wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        toolbar.AddTool(self.QUIT_ID,"Quit", myimage)
        toolbar.Bind(wx.EVT_TOOL, self._on_toolbar)
        toolbar.Realize()
        self.ToolBar = toolbar

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        main_sizer.Add(upper_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(lower_sizer, 0,
                       wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

        io_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        upper_sizer.Add(io_sizer, 2, wx.EXPAND | wx.RIGHT, 10)
        upper_sizer.Add(switches_sizer, 1, wx.EXPAND, 0)

        self.run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.total_sizer = wx.BoxSizer(wx.HORIZONTAL)
        io_sizer.Add(self.cycles_sizer, 0, wx.TOP | wx.CENTER, 15)
        io_sizer.Add(self.run_cont_sizer, 0, wx.ALL | wx.CENTER, 10)
        io_sizer.Add(self.total_sizer, 0, wx.BOTTOM | wx.CENTER, 5)

        """Configure the widgets"""
        # Cycles widgets
        text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.cycles_sizer.Add(text, 1, wx.CENTER | wx.RIGHT, 10)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, '20', min=1, max=1000)
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
        lower_sizer.Add(self.monitor_rows_sizer, 0, wx.EXPAND)
        self.monitor_rows = {}
        # Widgets to add and remove monitors
        add_zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_sizer.Add(add_zap_sizer, 0, wx.EXPAND)
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_zap_sizer.Add(add_sizer, 1, wx.EXPAND)
        zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_zap_sizer.Add(zap_sizer, 0, wx.EXPAND)
        text = wx.StaticText(self, wx.ID_ANY, "Add monitor:")
        add_sizer.Add(text, 0, wx.CENTER | wx.ALL, 10)
        self.add_choice = wx.Choice(self, choices=[])
        add_sizer.Add(self.add_choice, 0, wx.CENTER)
        text = wx.StaticText(self, wx.ID_ANY, "Zap monitor:")
        zap_sizer.Add(text, 0, wx.CENTER | wx.ALL, 10)
        self.zap_choice = wx.Choice(self, choices=[])
        zap_sizer.Add(self.zap_choice, 0, wx.CENTER | wx.RIGHT, 5)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self._on_menu)
        run_button.Bind(wx.EVT_BUTTON, self._run)
        cont_button.Bind(wx.EVT_BUTTON, self._continue_)
        self.add_choice.Bind(wx.EVT_CHOICE, self._on_add_choice)
        self.zap_choice.Bind(wx.EVT_CHOICE, self._on_zap_choice)

        # Set screen size
        self.SetSizeHints(500, 500)
        self.SetSize(600, 600)
        self.SetSizer(main_sizer)
        self.SetPosition((0, 50))

    def _add_switch(self, switch_id, switch_state):
        """Add a switch to GUI."""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switch_rows_sizer.Add(switch_sizer, 0, wx.CENTER | wx.ALL, 5)
        text = wx.StaticText(self, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self, wx.ID_ANY, "", choices=['0', '1'])
        switch_radiobox.SetSelection(switch_state)
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)
        switch_radiobox.Bind(wx.EVT_RADIOBOX, lambda evt,
                             temp=switch_id: self._on_switch(evt, temp))
        self.Layout()
        self._janky_linux_resizing_fix()

    def _on_switch(self, event, switch_id):
        """Handle event when a switch is toggled."""
        switch_state = event.GetSelection()
        if not self.devices.set_switch(switch_id, switch_state):
            print("Error! Invalid switch.")

    def _create_monitor(self, signal_name):
        """Create a new monitor."""
        # Get which signal to add
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        device_id = self.names.get_name_string(device_id)

        # Create monitor
        monitor_error = self.monitors.make_monitor(
            device_id, output_id, self.cycles_completed)
        if monitor_error == self.monitors.NO_ERROR:
            self._add_monitor(signal_name)
            print("Successfully made monitor.")
        else:
            print("Error! Could not make monitor.")

    def _add_monitor(self, signal_name):
        """Add a monitor that already exists to GUI."""
        # Add to GUI
        monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.monitor_rows[signal_name] = monitor_sizer
        self.monitor_rows_sizer.Add(monitor_sizer, 0, wx.EXPAND, 0)
        text = wx.StaticText(self, wx.ID_ANY, signal_name)
        text.SetMinSize((120, -1))
        monitor_sizer.Add(text, 0, wx.CENTER | wx.ALL, 13)
        self.canvas = MyGLCanvas(self, signal_name)
        monitor_sizer.Add(self.canvas, 1, wx.EXPAND | wx.CENTER | wx.ALL, 5)

        # Redraw gui
        self.Layout()

        self._set_choice_options()

        self._janky_linux_resizing_fix()

    def _zap_montior(self, signal_name):
        """Remove the specified monitor."""
        # Get which signal to zap
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        device_id = self.names.get_name_string(device_id)

        if self.monitors.remove_monitor(device_id, output_id):
            # Remove from GUI
            MyGLCanvas.instances.pop(signal_name)
            self.monitor_rows[signal_name].Clear(True)
            self.monitor_rows.pop(signal_name)
            self.Layout()
            self._janky_linux_resizing_fix()
            self._set_choice_options()
            print("Successfully zapped monitor.")
        else:
            print("Error! Could not zap monitor.")

    def _set_choice_options(self):
        default = "- Select -"
        [monitored, unmonitored] = self.monitors.get_signal_names()
        monitored.insert(0, default)
        unmonitored.insert(0, default)
        self.add_choice.SetItems(unmonitored)
        self.add_choice.SetSelection(0)
        self.zap_choice.SetItems(monitored)
        self.zap_choice.SetSelection(0)

    def _on_add_choice(self, event):
        signal_int = self.add_choice.GetSelection()
        if signal_int == 0:  # No signals to add
            return
        signal_name = self.monitors.get_signal_names()[1][signal_int - 1]
        self._create_monitor(signal_name)

    def _on_zap_choice(self, event):
        signal_int = self.zap_choice.GetSelection()
        if signal_int == 0:  # No signals to zap
            return
        signal_name = self.monitors.get_signal_names()[0][signal_int - 1]
        self._zap_montior(signal_name)

    def _on_menu(self, event):
        Id = event.GetId()
        if Id  == self.OPEN_ID:
            self._open_file(event)
        elif Id == self.QUIT_ID:
            self._quit(event)

    def _on_toolbar(self, event): 
        Id = event.GetId()
        if Id  == self.OPEN_ID:
            self._open_file(event)
        elif Id == self.QUIT_ID:
            self._quit(event)

    def _open_file(self, event):
        """Open a file specified by the user."""
        # Opens file selector
        openFileDialog = wx.FileDialog(
            self, "Open txt file", "", "",
            wildcard="TXT files (*.txt)|*.txt",
            style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        self.path = openFileDialog.GetPath()
        print("File chosen =", self.path)

        # Make sure gui is blank
        self.cycles_completed = 0
        self.total_cycles_text.SetLabel(str(self.cycles_completed))
        self._clear_widgets()

        # Initialise instances of the four inner simulator classes
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)

        # Interpret file
        scanner = Scanner(self.path, self.names)
        parser = Parser(self.names,
                        self.devices, self.network, self.monitors, scanner)
        if not parser.parse_network():
            print("Error! Unable to parse file.")
            return

        # Add switches and monitors to gui
        self._populate_widgets()

    def _populate_widgets(self):
        """Add required switches and monitors to the gui."""
        # Add switches
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            switch = self.devices.get_device(switch_id)
            switch_state = switch.switch_state
            self._add_switch(switch_id, switch_state)

        self._set_choice_options()

        # Add monitors and ensure they are cleared
        for monitored_signal_name in self.monitors.get_signal_names()[0]:
            self._add_monitor(monitored_signal_name)
        for signal_list in self.monitors.monitors_dictionary:
            self.monitors.monitors_dictionary[signal_list] = []

    def _clear_widgets(self):
        """Clear the switches and monitors from the gui."""
        self.switch_rows_sizer.Clear(True)
        self.monitor_rows_sizer.Clear(True)
        MyGLCanvas.instances = {}
        self.monitor_rows = {}

    def _run_network(self):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        # Get user input
        cycles = self.spin.GetValue()

        # Run
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False

        # Update cycles
        self.cycles_completed += cycles
        self.total_cycles_text.SetLabel(str(self.cycles_completed))

        # Update monitor displays
        for canvas in MyGLCanvas.instances.values():
            canvas.render_signal(self.monitors.monitors_dictionary,
                                 self.devices, self.cycles_completed)

        return True

    def _run(self, event):
        """Run the simulation from scratch."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open a file first")
            return

        self.cycles_completed = 0
        self._clear_widgets()
        self._populate_widgets()
        self._run_network()

    def _continue_(self, event):
        """Continue a previously run simulation."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open a file first")
            return

        if self.cycles_completed == 0:
            print("Error! Nothing to continue. Please run first.")
        else:
            self._run_network()

    def _quit(self, event):
        """Exit the program."""
        sys.exit()

    def _janky_linux_resizing_fix(self):
        inital_size = self.GetSize()
        self.SetSizeHints(0, 0)
        self.Fit()
        fitted_size = self.GetSize()
        self.SetSizeHints(fitted_size)
        new_size = [0, 0]
        if fitted_size[0] > inital_size[0]:
            new_size[0] = fitted_size[0]
        else:
            new_size[0] = inital_size[0]

        if fitted_size[1] > inital_size[1]:
            new_size[1] = fitted_size[1]
        else:
            new_size[1] = inital_size[1]

        self.SetSize(new_size)
