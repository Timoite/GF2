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

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

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
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

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

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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

        self.OPEN_ID = 997
        self.ABOUT_ID = 998
        self.QUIT_ID = 999

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(self.OPEN_ID, "&Open")
        fileMenu.Append(self.ABOUT_ID, "&About")
        fileMenu.Append(self.QUIT_ID, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Configure the toolbar
        toolbar = self.CreateToolBar()
        myimage = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddTool(self.OPEN_ID,"Open file", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        toolbar.AddTool(self.QUIT_ID,"Quit", myimage)
        toolbar.Bind(wx.EVT_TOOL, self._on_toolbar)
        toolbar.Realize()
        self.ToolBar = toolbar

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self)

        # Configure the widgets
        run_text = wx.StaticText(self, wx.ID_ANY, "Run for N cycles:")
        run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        total_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, '20', min=1, max=1000)
        run_button = wx.Button(self, wx.ID_ANY, "Run")
        cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        total_cycles_text = wx.StaticText(self, wx.ID_ANY, "Total Cycles: ")
        self.total_cycles_text = wx.StaticText(self, wx.ID_ANY, "0")

        monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_text = wx.StaticText(self, wx.ID_ANY, "Add monitor:")
        self.add_choice = wx.Choice(self, choices=[])
        zap_text = wx.StaticText(self, wx.ID_ANY, "Zap monitor:")
        self.zap_choice = wx.Choice(self, choices=[])

        switches_text = wx.StaticText(self, wx.ID_ANY, "Switches")

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        UI_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(UI_sizer)
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)

        run_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        monitors_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.switch_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scrolled_panel.SetScrollRate(10, 10)
        self.scrolled_panel.SetSizer(self.switch_rows_sizer)
        UI_sizer.Add(run_sizer, 0, wx.EXPAND | wx.ALL, 5)
        UI_sizer.Add(monitors_sizer, 0, wx.EXPAND | wx.ALL, 5)
        UI_sizer.Add(switches_sizer, 1, wx.EXPAND | wx.ALL, 5)

        run_sizer.Add(run_text, 0, wx.CENTER | wx.ALL, 10)
        run_sizer.Add(cycles_sizer, 0, wx.CENTER | wx.ALL, 5)
        run_sizer.Add(run_cont_sizer, 0, wx.CENTER | wx.ALL, 5)
        run_sizer.Add(total_sizer, 0, wx.CENTER | wx.ALL, 5)
        cycles_sizer.Add(cycles_text, 1, wx.CENTER | wx.RIGHT, 10)
        cycles_sizer.Add(self.spin, 0, wx.CENTER)
        run_cont_sizer.Add(run_button, 1, wx.CENTER | wx.RIGHT, 10)
        run_cont_sizer.Add(cont_button, 1, wx.CENTER)
        total_sizer.Add(total_cycles_text, 0, wx.CENTER | wx.RIGHT, 5)
        total_sizer.Add(self.total_cycles_text, 0, wx.CENTER)
        monitors_sizer.Add(monitors_text, 1, wx.CENTER | wx.ALL, 10)
        monitors_sizer.Add(add_sizer)
        monitors_sizer.Add(zap_sizer)
        add_sizer.Add(add_text, 0, wx.CENTER | wx.ALL, 10)
        add_sizer.Add(self.add_choice, 0, wx.CENTER)
        zap_sizer.Add(zap_text, 0, wx.CENTER | wx.ALL, 10)
        zap_sizer.Add(self.zap_choice, 0, wx.CENTER)
        switches_sizer.Add(switches_text, 1, wx.CENTER | wx.ALL, 10)
        switches_sizer.Add(self.scrolled_panel, 10, wx.EXPAND | wx.CENTER)
        self.switch_rows_sizer.Fit(self.scrolled_panel)

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
        text = wx.StaticText(self.scrolled_panel, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self.scrolled_panel, wx.ID_ANY, "", choices=['0', '1'])
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
        elif Id == self.ABOUT_ID:
            wx.MessageBox("Logic Simulatorinator\nCreated by Harry Weedon, Thomas Barker and Tim Tan\n2025",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

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
        # self.switch_rows_sizer.Clear(True)
        # self.monitor_rows_sizer.Clear(True)
        # MyGLCanvas.instances = {}
        # self.monitor_rows = {}

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
        # inital_size = self.GetSize()
        # self.SetSizeHints(0, 0)
        # self.Fit()
        # fitted_size = self.GetSize()
        # self.SetSizeHints(fitted_size)
        # new_size = [0, 0]
        # if fitted_size[0] > inital_size[0]:
        #     new_size[0] = fitted_size[0]
        # else:
        #     new_size[0] = inital_size[0]

        # if fitted_size[1] > inital_size[1]:
        #     new_size[1] = fitted_size[1]
        # else:
        #     new_size[1] = inital_size[1]

        # self.SetSize(new_size)
        print()