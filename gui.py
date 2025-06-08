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
        self.parent = parent
        self.monitors_dictionary = None
        self.devices = None

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.max_x = 0
        self.max_y = 0
        self.signals_width = 0
        self.signals_height = 0
        self.size = self.GetClientSize()
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom_x = 1
        self.zoom_y = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom_x, self.zoom_x, self.zoom_x)

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        
        self.size = self.GetClientSize()
        # self.check_panning()
        self.render()
        self.check_panning()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True

        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Apply pan and zoom
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom_x, self.zoom_y, 1.0)

        # Posistioning constants
        DX = 15
        DY = 30
        BORDER_Y = 2*DY
        BORDER_X = DX
        LINE_HEIGHT = 2*DY + BORDER_Y

        # Draw axes
        for i in range(int(self.max_y)):
            j = self.size.height - i
            if i % DY == 0:
                if i % (4*DY) == 0:
                    GL.glLineWidth(3)
                    GL.glColor3f(1.0, 1.0, 1.0)
                else:
                    GL.glLineWidth(1)
                    GL.glColor3f(0.4, 0.4, 0.4)
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(0, j)
                GL.glVertex2f(self.max_x, j)
                GL.glEnd()
        for i in range(int(self.max_x)):
            if (i-BORDER_Y) % (3*DX) == 0:
                GL.glLineWidth(1)
                GL.glColor3f(0.4, 0.4, 0.4)
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(i, 0)
                GL.glVertex2f(i, self.max_y)
                GL.glEnd()

        # if sim has been run, draw trace
        if self.monitors_dictionary:
            colours = self.parent.generate_colors(len(self.monitors_dictionary))
            for i, item in enumerate(self.monitors_dictionary.items()):
                sig_list = item[1]
                
                y_MID = self.size.height - (LINE_HEIGHT * i) - BORDER_Y
                y_HIGH = y_MID + DY
                y_LOW = y_MID - DY

                # Draw signal
                [r, g, b] = colours[i]
                GL.glColor3f(r, g, b)
                GL.glLineWidth(10)
                GL.glBegin(GL.GL_LINE_STRIP)
                for j, sig in enumerate(sig_list):
                    x = (j * DX) + BORDER_X
                    x_next = (j * DX) + BORDER_X + DX
                    if sig == self.devices.HIGH:
                        y = y_HIGH
                        y_next = y_HIGH
                    if sig == self.devices.LOW:
                        y = y_LOW
                        y_next = y_LOW
                    if sig == self.devices.RISING:
                        y = y_LOW
                        y_next = y_HIGH
                    if sig == self.devices.FALLING:
                        y = y_HIGH
                        y_next = y_LOW
                    if sig == self.devices.BLANK:
                        continue
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y_next)
                    j += 1
                GL.glEnd()
                GL.glLineWidth(1)

                self.signals_width = 2 * BORDER_X + j * DX
            self.signals_height = 2 * BORDER_Y + i * LINE_HEIGHT

        GL.glFlush()
        self.SwapBuffers()

    def on_mouse(self, event):
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        # size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom_x
        # oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom_x = self.zoom_x
        # old_zoom_y = self.zoom_y

        wheel_rotation, wheel_delta = event.GetWheelRotation(), event.GetWheelDelta()
        if wheel_rotation != 0:
            # Zooming
            if event.ControlDown():
                if wheel_rotation > 0:
                    self.zoom_x *= (1.0 + (
                        wheel_rotation / (20 * wheel_delta)))
                if wheel_rotation < 0:
                    self.zoom_x /= (1.0 - (
                        wheel_rotation / (20 * wheel_delta)))
                # Adjust pan so as to zoom around the mouse position
                self.pan_x -= (self.zoom_x - old_zoom_x) * ox
                # self.pan_y -= (self.zoom_y - old_zoom_y) * oy

            # Horizontal scrolling
            elif event.ShiftDown():
                dPANx = 10
                if wheel_rotation > 0:
                    self.pan_x += dPANx
                if wheel_rotation < 0:
                    self.pan_x -= dPANx

            # Vertical scrolling
            else:
                dPANy = 10
                if wheel_rotation < 0:
                    self.pan_y += dPANy
                if wheel_rotation > 0:
                    self.pan_y -= dPANy
            
            self.init = False

        if self.pan_x > 0:
            self.pan_x = 0
        elif (self.size.width - self.pan_x) / self.zoom_x > self.max_x:
            self.pan_x = self.size.width - (self.max_x * self.zoom_x)
        if self.pan_y < 0:
            self.pan_y = 0
        elif (self.pan_y + self.size.height) / self.zoom_y > self.max_y:
            self.pan_y = (self.max_y * self.zoom_y) - self.size.height

        self.Refresh()

    def check_panning(self):
        if self.size.width / self.zoom_x >= self.signals_width:
            self.max_x = self.size.width / self.zoom_x
            self.parent.hscrollbar.Hide()
        else:
            self.max_x = self.signals_width
            self.parent.hscrollbar.Show()
        if self.size.height / self.zoom_y >= self.signals_height:
            self.max_y = self.size.height / self.zoom_y
            self.parent.vscrollbar.Hide()
        else:
            self.max_y = self.signals_height
            self.parent.vscrollbar.Show()

        self.parent.Layout()
        self.parent.update_scrollbars()

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
        fileMenu.Append(self.OPEN_ID, "&Open")
        fileMenu.Append(self.ABOUT_ID, "&About")
        fileMenu.Append(self.QUIT_ID, "&Exit")
        runMenu = wx.Menu()
        runMenu.Append(self.OPEN_ID, "&Run")
        runMenu.Append(self.OPEN_ID, "&Continue")
        runMenu.Append(self.OPEN_ID, "&Play")
        runMenu.Append(self.OPEN_ID, "&Pause")
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(runMenu, "&Run")
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

        # ----- Configure the widgets -----
        # Run
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

        # Monitors
        monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_text = wx.StaticText(self, wx.ID_ANY, "Add monitor:")
        self.add_choice = wx.Choice(self, choices=[])
        zap_text = wx.StaticText(self, wx.ID_ANY, "Zap monitor:")
        self.zap_choice = wx.Choice(self, choices=[])

        # Switches
        switches_text = wx.StaticText(self, wx.ID_ANY, "Switches")

        # Scrollbars
        self.hscrollbar = wx.ScrollBar(self, style=wx.HORIZONTAL)
        self.vscrollbar = wx.ScrollBar(self, style=wx.VERTICAL)
        self.hscrollbar.SetScrollbar(0, 20, 50, 15)
        self.vscrollbar.SetScrollbar(0, 20, 50, 15)

        # Canvas
        self.canvas = MyGLCanvas(self)

        # ----- Configure sizers ------
        # Main layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=0)
        main_sizer.Add(left_sizer, 1, wx.ALL, 5)
        main_sizer.Add(right_sizer, 100, wx.EXPAND | wx.ALL, 5)

        # Left
        run_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        monitors_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.switches_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.switches_scroll.SetScrollRate(10, 10)
        self.switches_scroll.SetSizer(self.switches_rows_sizer)
        left_sizer.Add(run_sizer, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(monitors_sizer, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(switches_sizer, 1, wx.EXPAND | wx.ALL, 5)
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
        switches_sizer.Add(self.switches_scroll, 100, wx.EXPAND | wx.CENTER)
        self.switches_rows_sizer.Fit(self.switches_scroll)

        # Right
        right_sizer.AddGrowableCol(0, 1)
        right_sizer.AddGrowableRow(0, 1)
        right_sizer.Add(self.canvas, 1, wx.EXPAND)
        right_sizer.Add(self.vscrollbar, 0, wx.EXPAND)
        right_sizer.Add(self.hscrollbar, 0, wx.EXPAND)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self._on_menu)
        run_button.Bind(wx.EVT_BUTTON, self._run)
        cont_button.Bind(wx.EVT_BUTTON, self._continue)
        self.add_choice.Bind(wx.EVT_CHOICE, self._on_add_choice)
        self.zap_choice.Bind(wx.EVT_CHOICE, self._on_zap_choice)
        self.hscrollbar.Bind(wx.EVT_SCROLL, self.on_scroll)
        self.vscrollbar.Bind(wx.EVT_SCROLL, self.on_scroll)

        # Set screen size
        self.SetSizeHints(500, 500)
        self.SetSize(600, 600)
        self.SetSizer(main_sizer)
        self.SetPosition((0, 50))

    def _add_switch(self, switch_id, switch_state):
        """Add a switch to GUI."""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switches_rows_sizer.Add(switch_sizer, 0, wx.CENTER | wx.ALL, 5)
        text = wx.StaticText(self.switches_scroll, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self.switches_scroll, wx.ID_ANY, "", choices=['0', '1'])
        switch_radiobox.SetSelection(switch_state)
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)
        switch_radiobox.Bind(wx.EVT_RADIOBOX, lambda evt,
                             temp=switch_id: self._on_switch(evt, temp))
        self.Layout()

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
            self._set_choice_options()
            print("Successfully made monitor.")
        else:
            print("Error! Could not make monitor.")

    def _zap_montior(self, signal_name):
        """Remove the specified monitor."""
        # Get which signal to zap
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        device_id = self.names.get_name_string(device_id)

        if self.monitors.remove_monitor(device_id, output_id):
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
        self.canvas.on_paint(None)

    def _on_zap_choice(self, event):
        signal_int = self.zap_choice.GetSelection()
        if signal_int == 0:  # No signals to zap
            return
        signal_name = self.monitors.get_signal_names()[0][signal_int - 1]
        self._zap_montior(signal_name)
        self.canvas.on_paint(None)

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

        # Add switches
        self.switches_rows_sizer.Clear(True)
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            switch = self.devices.get_device(switch_id)
            switch_state = switch.switch_state
            self._add_switch(switch_id, switch_state)

        self._set_choice_options()
        self.update_canvas

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
        self.canvas.monitors_dictionary = self.monitors.monitors_dictionary
        self.canvas.devices = self.devices

        return True

    def _run(self, event):
        """Run the simulation from scratch."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open a file first")
            return

        self.cycles_completed = 0
        for monitor in self.monitors.monitors_dictionary:
            self.monitors.monitors_dictionary[monitor] = []
        self._run_network()
        self.update_canvas()

    def _continue(self, event):
        """Continue a previously run simulation."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open a file first")
            return

        if self.cycles_completed == 0:
            print("Error! Nothing to continue. Please run first.")
        else:
            self._run_network()
            self.update_canvas()

    def on_scroll(self, event):
            self.canvas.pan_x = -self.hscrollbar.GetThumbPosition()
            self.canvas.pan_y = self.vscrollbar.GetThumbPosition()
            self.update_canvas()

    def update_scrollbars(self):
        pan_x, pan_y = self.canvas.pan_x, self.canvas.pan_y
        width, height = self.canvas.size.width, self.canvas.size.height
        max_x, max_y = self.canvas.max_x, self.canvas.max_y
        zoom_x, zoom_y = self.canvas.zoom_x, self.canvas.zoom_y
        self.hscrollbar.SetScrollbar(int(-pan_x), int(width), int(max_x * zoom_x), 0)
        self.vscrollbar.SetScrollbar(int(pan_y), int(height), int(max_y * zoom_y), 0)

    def update_canvas(self):
        self.canvas.init = False
        self.canvas.Refresh()
        self.update_scrollbars()

    def generate_colors(self, n):
        """
        Generate `n` distinct high-saturation RGB colors in a repeatable order.
        Returns a list of RGB tuples with values in the range [0, 255].
        """
        def hsv_to_rgb(h, s, v):
            """Convert HSV (in [0-1] range) to RGB (in [0-255])"""
            i = int(h * 6)
            f = (h * 6) - i
            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)
            i = i % 6
            if i == 0: r, g, b = v, t, p
            elif i == 1: r, g, b = q, v, p
            elif i == 2: r, g, b = p, v, t
            elif i == 3: r, g, b = p, q, v
            elif i == 4: r, g, b = t, p, v
            elif i == 5: r, g, b = v, p, q
            return [r, g, b]

        colors = []
        golden_ratio_conjugate = 0.61803398875  # Ensures good distribution
        h = 0  # Initial hue
        for i in range(n):
            h = (h + golden_ratio_conjugate) % 1
            rgb = hsv_to_rgb(h, 1.0, 1.0)  # Full saturation and value
            colors.append(rgb)
        return colors

    def _quit(self, event):
        """Exit the program."""
        sys.exit()
