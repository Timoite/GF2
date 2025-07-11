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

    def __init__(self, parent) -> None:
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
        self.SCALE_HEIGHT = 40

        # Initialise variables for zooming
        self.zoom_x = 1
        self.zoom_y = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self._on_mouse)

    def _init_gl(self) -> None:
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

    def _on_paint(self, event) -> None:
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self._init_gl()
            self.init = True

        self.size = self.GetClientSize()
        self._render()

    def _on_size(self, event) -> None:
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def _render(self) -> None:
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            self._init_gl()
            self.init = True

        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Posistioning constants
        self.DX = 15
        DY = 30
        BORDER_Y = 2 * DY
        self.BORDER_X = self.DX
        self.LINE_HEIGHT = 2 * DY + BORDER_Y
        TOP = self.size.height - self.SCALE_HEIGHT
        CYCLES_PER_TICK = max(5 * round(DY / (self.DX * self.zoom_x * 5)), 5)

        # Apply pan and zoom
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom_x, self.zoom_y, 1.0)

        self.check_canvas_size()

        # Draw axes
        for i in range(int(self.max_x)):  # Vertical
            if (i-self.BORDER_X) % (CYCLES_PER_TICK*self.DX) == 0:
                GL.glLineWidth(1)
                GL.glColor3f(0.4, 0.4, 0.4)
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(i, TOP)
                GL.glVertex2f(i, TOP - self.max_y)
                GL.glEnd()
        for i in range(int(self.max_y)):  # Horizontal
            j = TOP - i
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

        # If sim has been run, draw trace
        colours = self.parent.generate_colours(
                len(self.monitors_dictionary))
        if self.monitors_dictionary:
            for i, item in enumerate(self.monitors_dictionary.items()):
                sig_list = item[1]

                y_MID = TOP - (self.LINE_HEIGHT * i) - BORDER_Y
                y_HIGH = y_MID + DY
                y_LOW = y_MID - DY

                # Draw signal
                [r, g, b] = colours[i]
                GL.glColor3f(r, g, b)
                GL.glLineWidth(10)
                GL.glBegin(GL.GL_LINE_STRIP)
                for j, sig in enumerate(sig_list):
                    x = (j * self.DX) + self.BORDER_X
                    x_next = (j * self.DX) + self.BORDER_X + self.DX
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

        # Undo horizontal scroll
        GL.glScaled(1/self.zoom_x, 1/self.zoom_y, 1.0)
        GL.glTranslated(-self.pan_x, 0.0, 0.0)

        # Add trace labels
        if self.monitors_dictionary:
            for i, item in enumerate(self.monitors_dictionary.items()):
                sig_name = item[0][0]
                y = TOP - (self.LINE_HEIGHT * i) - (BORDER_Y / 4)
                self._render_text(sig_name, 10, y, False, False, colours[i])

        # Undo vertical scroll and re-add horizontal
        GL.glTranslated(self.pan_x, -self.pan_y, 0.0)
        GL.glScaled(self.zoom_x, self.zoom_y, 1.0)

        # Make blank box at the top
        GL.glColor3f(0.0, 0.0, 0.0)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(0, self.size.height)
        GL.glVertex2f(0, self.size.height - self.SCALE_HEIGHT)
        GL.glVertex2f(self.max_x, self.size.height - self.SCALE_HEIGHT)
        GL.glVertex2f(self.max_x, self.size.height)
        GL.glEnd()
        GL.glLineWidth(8)
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(0, self.size.height - self.SCALE_HEIGHT)
        GL.glVertex2f(self.max_x, self.size.height - self.SCALE_HEIGHT)
        GL.glEnd()

        # Add x axis scale
        for i in range(int(self.max_x)):
            if (i-self.BORDER_X) % (2*CYCLES_PER_TICK*self.DX) == 0:
                num = CYCLES_PER_TICK*(i-self.BORDER_X)\
                    // (CYCLES_PER_TICK*self.DX)
                if num >= 0:
                    self._render_text(
                        str(num), i,
                        self.size.height - (self.SCALE_HEIGHT / 2))

        GL.glFlush()
        self.SwapBuffers()

    def _render_text(self, text, x_pos, y_pos,
                     center=True, big=True, colour=(1.0, 1.0, 1.0)) -> None:
        """Handle text drawing operations."""
        GL.glColor3f(colour[0], colour[1], colour[2])
        if big:
            font = GLUT.GLUT_BITMAP_TIMES_ROMAN_24
        else:
            font = GLUT.GLUT_BITMAP_TIMES_ROMAN_10
        if center:
            line_width = sum(GLUT.glutBitmapWidth(font, ord(c)) for c in text)
            x_pos -= line_width / (2 * self.zoom_x)
            x_pos = max(x_pos, 0)
        line_height = max(GLUT.glutBitmapWidth(font, ord(c)) for c in text)
        y_pos -= line_height / 2
        GL.glRasterPos2f(x_pos, y_pos)
        for character in text:
            GLUT.glutBitmapCharacter(font, ord(character))

    def _on_mouse(self, event) -> None:
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        ox = (event.GetX() - self.pan_x) / self.zoom_x
        # oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom_x = self.zoom_x
        # old_zoom_y = self.zoom_y

        wheel_rotation, wheel_delta = \
            event.GetWheelRotation(), event.GetWheelDelta()
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
                dPANx = 20
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

        self.check_canvas_size()

        self.Refresh()

    def check_canvas_size(self) -> None:
        """Recalculate the size of the canvas."""
        # Limit zoom
        self.zoom_x = max(0.01, self.zoom_x)
        self.zoom_x = min(10, self.zoom_x)

        # How much space do the signals take up
        if self.monitors_dictionary:
            self.signals_width = 2 * self.BORDER_X + \
                self.parent.cycles_completed * self.DX
            self.signals_height = len(self.monitors_dictionary)\
                * self.LINE_HEIGHT

        # If screen is larger than canvas, hide scollbars
        if self.size.width / self.zoom_x >= self.signals_width:
            self.max_x = self.size.width / self.zoom_x
            self.parent.hscrollbar.Hide()
        else:
            self.max_x = self.signals_width
            self.parent.hscrollbar.Show()
        if self.size.height / self.zoom_y >= self.signals_height:
            self.max_y = (self.size.height - self.SCALE_HEIGHT) / self.zoom_y
            self.parent.vscrollbar.Hide()
        else:
            self.max_y = self.signals_height
            self.parent.vscrollbar.Show()
        self.parent.Layout()

        # Make sure panning within bounds of screen
        self.pan_x = min(0, self.pan_x)
        self.pan_x = max(self.size.width
                         - (self.max_x * self.zoom_x), self.pan_x)
        self.pan_y = max(0, self.pan_y)
        self.pan_y = min((self.max_y * self.zoom_y)
                         - self.size.height + self.SCALE_HEIGHT, self.pan_y)

        # Set scrollbar positions
        self.parent.hscrollbar.SetScrollbar(
            int(-self.pan_x), int(self.size.width),
            int(self.max_x * self.zoom_x), 0)
        self.parent.vscrollbar.SetScrollbar(
            int(self.pan_y), int(self.size.height - self.SCALE_HEIGHT),
            int(self.max_y * self.zoom_y), 0)


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.
    """

    def __init__(self, title, path) -> None:
        """Initialise static widgets and layout."""
        super().__init__(parent=None, title=title, size=(400, 400))
        self.path = None
        self.names = None
        self.devices = None
        self.network = None
        self.monitors = None
        self.cycles_completed = 0

        self.OPEN_ID = 1000
        self.ABOUT_ID = 1001
        self.QUIT_ID = 1002
        self.RUN_ID = 1003
        self.CLEAR_ID = 1004
        self.PLAY_ID = 1005
        self.PAUSE_ID = 1006
        self.ZOOM_IN_ID = 1007
        self.ZOOM_OUT_ID = 1008
        self.RESET_ZOOM_ID = 1009
        self.DEF_SPEED = 50
        self.SPEEDS = [0.1, 0.2, 0.5, 1, 2, 5, 10]

        self.has_started = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._run_network)

        # Configure the file menu
        fileMenu = wx.Menu()
        fileMenu.Append(self.OPEN_ID, _(u"&Open"))
        fileMenu.Append(self.ABOUT_ID, _(u"&About"))
        fileMenu.Append(self.QUIT_ID, _(u"&Exit"))
        runMenu = wx.Menu()
        runMenu.Append(self.RUN_ID, _(u"&Run / Continue"))
        runMenu.Append(self.CLEAR_ID, _(u"&Clear"))
        runMenu.Append(self.PLAY_ID, _(u"&Play"))
        runMenu.Append(self.PAUSE_ID, _(u"&Pause"))
        viewMenu = wx.Menu()
        viewMenu.Append(self.ZOOM_IN_ID, _(u"&Zoom In"))
        viewMenu.Append(self.ZOOM_OUT_ID, _(u"&Zoom Out"))
        viewMenu.Append(self.RESET_ZOOM_ID, _(u"&Reset Zoom"))
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, _(u"&File"))
        menuBar.Append(runMenu, _(u"&Run"))
        menuBar.Append(viewMenu, _(u"&View"))
        self.SetMenuBar(menuBar)

        # Configure the toolbar
        toolbar = self.CreateToolBar()
        myimage = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddTool(self.OPEN_ID, _(u"Open file"), myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        toolbar.AddTool(self.QUIT_ID, _(u"Quit"), myimage)
        toolbar.Realize()
        self.ToolBar = toolbar

        # ----- Configure the widgets -----
        # Run
        run_text1 = wx.StaticText(
            self, wx.ID_ANY, _(u"Run for N Cycles"))
        cycles_text = wx.StaticText(
            self, wx.ID_ANY, _(u"Cycles:"))
        self.cycles_spin = wx.SpinCtrl(
            self, wx.ID_ANY, '20', min=1, max=10000)
        self.run_button = wx.Button(
            self, self.RUN_ID, _(u"Run"))
        continue_button = wx.Button(
            self, self.CLEAR_ID, _(u"Clear"))
        run_text2 = wx.StaticText(
            self, wx.ID_ANY, _(u"Run Indefinitely"))
        play_button = wx.Button(
            self, self.PLAY_ID, _(u"Play"))
        pause_button = wx.Button(
            self, self.PAUSE_ID, _(u"Pause"))
        self.speed_slider = wx.Slider(
            self, wx.ID_ANY, 3, 0, 6, size=(100, -1))
        self.speed_slider_text = wx.StaticText(
            self, wx.ID_ANY, _(u"Speed: ")
            + str(self.SPEEDS[self.speed_slider.GetValue()])+"x")
        total_cycles_text = wx.StaticText(
            self, wx.ID_ANY, _(u"Total Cycles: "))
        self.total_cycles_text = wx.StaticText(self, wx.ID_ANY, "0")

        # Monitors
        monitors_text = wx.StaticText(
            self, wx.ID_ANY, _(u"Monitors"))

        # Switches
        switches_text = wx.StaticText(
            self, wx.ID_ANY, _(u"Switches"))

        # Canvas
        self.canvas = MyGLCanvas(self)
        self.hscrollbar = wx.ScrollBar(self, style=wx.HORIZONTAL)
        self.vscrollbar = wx.ScrollBar(self, style=wx.VERTICAL)
        self.hscrollbar.SetScrollbar(0, 20, 50, 15)
        self.vscrollbar.SetScrollbar(0, 20, 50, 15)

        # ----- Configure sizers ------
        # Main layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=0)

        main_sizer.Add(left_sizer)
        main_sizer.Add(right_sizer, 100, wx.EXPAND | wx.ALL, 5)

        # Left
        run_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        play_pause_sizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        total_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.monitors_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self.monitors_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.monitors_scroll.SetScrollRate(10, 10)
        self.monitors_scroll.SetSizer(self.monitors_rows_sizer)
        self.switches_rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.switches_scroll.SetScrollRate(10, 10)
        self.switches_scroll.SetSizer(self.switches_rows_sizer)

        left_sizer.Add(run_sizer, 1, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(monitors_sizer, 5, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(switches_sizer, 5, wx.EXPAND | wx.ALL, 5)
        run_sizer.Add(run_text1, 0, wx.CENTER)
        run_sizer.Add(run_cont_sizer, 0,
                      wx.CENTER | wx.TOP | wx.LEFT | wx.RIGHT, 10)
        run_sizer.Add(cycles_sizer, 0, wx.CENTER | wx.ALL, 5)
        run_sizer.Add(run_text2, 0, wx.CENTER | wx.TOP, 20)
        run_sizer.Add(play_pause_sizer, 0, wx.CENTER | wx.TOP, 10)
        run_sizer.Add(speed_sizer, 0, wx.CENTER | wx.TOP, 10)
        run_sizer.Add(total_sizer, 0, wx.CENTER | wx.TOP, 25)
        cycles_sizer.Add(cycles_text, 1, wx.CENTER | wx.RIGHT, 10)
        cycles_sizer.Add(self.cycles_spin, 0, wx.CENTER)
        run_cont_sizer.Add(self.run_button, 1, wx.CENTER | wx.RIGHT, 10)
        run_cont_sizer.Add(continue_button, 1, wx.CENTER)
        play_pause_sizer.Add(play_button, 1, wx.CENTER | wx.RIGHT, 10)
        play_pause_sizer.Add(pause_button, 1, wx.CENTER)
        speed_sizer.Add(self.speed_slider_text, 1, wx.CENTER | wx.RIGHT, 10)
        speed_sizer.Add(self.speed_slider)
        total_sizer.Add(
            total_cycles_text, 0, wx.CENTER | wx.RIGHT | wx.BOTTOM, 10)
        total_sizer.Add(self.total_cycles_text, 0, wx.CENTER | wx.BOTTOM, 10)
        monitors_sizer.Add(monitors_text, 0, wx.CENTER | wx.BOTTOM, 10)
        monitors_sizer.Add(self.monitors_scroll, 2,
                           wx.EXPAND | wx.CENTER | wx.ALL, 5)
        self.monitors_rows_sizer.Fit(self.monitors_scroll)
        switches_sizer.Add(switches_text, 0, wx.CENTER | wx.BOTTOM, 10)
        switches_sizer.Add(self.switches_scroll, 1, wx.EXPAND | wx.CENTER)
        self.switches_rows_sizer.Fit(self.switches_scroll)

        # Right
        right_sizer.AddGrowableCol(0, 1)
        right_sizer.AddGrowableRow(0, 1)
        right_sizer.Add(self.canvas, 1, wx.EXPAND | wx.TOP, 10)
        right_sizer.Add(self.vscrollbar, 0, wx.EXPAND | wx.TOP, 10)
        right_sizer.Add(self.hscrollbar, 0, wx.EXPAND)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self._on_menu)
        toolbar.Bind(wx.EVT_TOOL, self._on_toolbar)
        self.run_button.Bind(wx.EVT_BUTTON, self._on_run)
        continue_button.Bind(wx.EVT_BUTTON, self._on_run)
        play_button.Bind(wx.EVT_BUTTON, self._on_run)
        pause_button.Bind(wx.EVT_BUTTON, self._on_run)
        self.speed_slider.Bind(wx.EVT_SLIDER, self._on_slider)
        self.hscrollbar.Bind(wx.EVT_SCROLL, self._on_scroll)
        self.vscrollbar.Bind(wx.EVT_SCROLL, self._on_scroll)

        # Set screen size
        self.SetSizeHints(720, 720)
        self.SetSize(720, 720)
        self.SetSizer(main_sizer)
        self.SetPosition((0, 50))

        self._open_file(None, path)

    def _add_switch(self, switch_id, switch_state) -> None:
        """Add a switch to GUI."""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switches_rows_sizer.Add(switch_sizer, 0, wx.CENTER | wx.ALL, 5)
        text = wx.StaticText(self.switches_scroll, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self.switches_scroll,
                                      wx.ID_ANY, "", choices=['0', '1'])
        switch_radiobox.SetSelection(switch_state)
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)
        switch_radiobox.Bind(wx.EVT_RADIOBOX, lambda evt,
                             temp=switch_id: self._on_switch(evt, temp))
        self.switches_scroll.FitInside()
        self.Layout()

    def _on_switch(self, event, switch_id) -> None:
        """Handle event when a switch is toggled."""
        switch_state = event.GetSelection()
        if not self.devices.set_switch(switch_id, switch_state):
            print(_(u"Error! Invalid switch."))

    def _add_monitor(self, signal_name) -> None:
        """Create a new monitor."""
        # Get which signal to add
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        device_id = self.names.get_name_string(device_id)

        # Create monitor
        monitor_error = self.monitors.make_monitor(
            device_id, output_id, self.cycles_completed)
        if monitor_error == self.monitors.NO_ERROR:
            self._update_monitor_list()
            print(_(u"Successfully made monitor."))
        else:
            print(_(u"Error! Could not make monitor."))

    def _zap_monitor(self, signal_name) -> None:
        """Remove the specified monitor."""
        # Get which signal to zap
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        device_id = self.names.get_name_string(device_id)

        if self.monitors.remove_monitor(device_id, output_id):
            self._update_monitor_list()
            print(_(u"Successfully zapped monitor."))
        else:
            print(_(u"Error! Could not zap monitor."))

    def _update_monitor_list(self) -> None:
        """Update the monitor selection list."""
        # Clear the list
        self.monitors_rows_sizer.Clear(True)

        # Get all signals
        [monitored, unmonitored] = self.monitors.get_signal_names()

        # Add monitored signals
        colours = self.generate_colours(len(monitored))
        for i, sig in enumerate(monitored):
            r, g, b = colours[i]
            R, G, B = int(r*255), int(g*255), int(b*255)
            monitor_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            checkbox = wx.CheckBox(self.monitors_scroll, wx.ID_ANY, sig)
            checkbox.SetValue(True)
            checkbox.Bind(wx.EVT_CHECKBOX, self._on_checkbox)
            line = wx.Panel(self.monitors_scroll, size=(20, 5))
            line.SetBackgroundColour((R, G, B))
            monitor_row_sizer.Add(checkbox, 1, wx.EXPAND)
            monitor_row_sizer.Add(line, 0, wx.CENTER | wx.RIGHT, 10)
            self.monitors_rows_sizer.Add(
                monitor_row_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 5)

        # Add unmonitored signals
        for sig in unmonitored:
            monitor_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            checkbox = wx.CheckBox(self.monitors_scroll, wx.ID_ANY, sig)
            checkbox.SetValue(False)
            checkbox.Bind(wx.EVT_CHECKBOX, self._on_checkbox)
            monitor_row_sizer.Add(checkbox, 1, wx.EXPAND)
            self.monitors_rows_sizer.Add(
                monitor_row_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 5)

        self.monitors_scroll.FitInside()
        self.Layout()

    def _on_checkbox(self, event) -> None:
        """Handle checkbox events."""
        checkbox = event.GetEventObject()
        signal_name = checkbox.GetLabel()
        checked = checkbox.IsChecked()
        if checked:
            self._add_monitor(signal_name)
        else:
            self._zap_monitor(signal_name)
        self.canvas.Refresh()

    def _on_slider(self, event) -> None:
        """Handle slider events."""
        text = _(u"Speed: ")\
            + str(self.SPEEDS[self.speed_slider.GetValue()])+"x"
        self.speed_slider_text.SetLabel(text)
        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start(int(
                self.DEF_SPEED / self.SPEEDS[self.speed_slider.GetValue()]))

    def _on_menu(self, event) -> None:
        """Handle menu events."""
        Id = event.GetId()
        if Id == self.OPEN_ID:
            self._open_file(event)
        elif Id == self.QUIT_ID:
            self._quit(event)
        elif Id == self.ABOUT_ID:
            wx.MessageBox(_(u"Logic Simulatorinator\n\
                          Created by Harry Weedon, \
                          Thomas Barker and Tim Tan\n2025"),
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        elif Id == self.ZOOM_IN_ID:
            self.canvas.zoom_x *= 1.5
            self.canvas.check_canvas_size()
            self.canvas.Refresh()
        elif Id == self.ZOOM_OUT_ID:
            self.canvas.zoom_x /= 1.5
            self.canvas.check_canvas_size()
            self.canvas.Refresh()
        elif Id == self.RESET_ZOOM_ID:
            self.canvas.zoom_x = 1.0
            self.canvas.check_canvas_size()
            self.canvas.Refresh()
        else:
            self._on_run(event)

    def _on_toolbar(self, event) -> None:
        """Handle toolbar events."""
        Id = event.GetId()
        if Id == self.OPEN_ID:
            self._open_file(event)
        elif Id == self.QUIT_ID:
            self._quit(event)

    def _open_file(self, event, path=None) -> None:
        """Load a file into the simulator."""
        if self.timer.IsRunning():
            print("Error! Simulation is running")
            return
        if not path:
            # Opens file selector
            openFileDialog = wx.FileDialog(
                self, _(u"Open txt file"), "", "",
                wildcard=_(u"TXT files (*.txt)|*.txt"),
                style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                if not self.path:
                    self._quit(None)
                return
            path = openFileDialog.GetPath()
        self.path = path
        print(_(u"File chosen ="), self.path)

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
            print(_(u"Error! Unable to parse file."))
            return

        # Add switches
        self.switches_rows_sizer.Clear(True)
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            switch = self.devices.get_device(switch_id)
            switch_state = switch.switch_state
            self._add_switch(switch_id, switch_state)

        # Clear any existing traces
        for monitor in self.monitors.monitors_dictionary:
            self.monitors.monitors_dictionary[monitor] = []
        self.canvas.monitors_dictionary = self.monitors.monitors_dictionary

        self._update_monitor_list()
        self.canvas.Refresh()
        self.has_started = False

    def _run_network(self, event=None, cycles=1) -> None:
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
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

        # Scroll canvas all the way to the right
        self.canvas.check_canvas_size()
        self.canvas.pan_x = self.canvas.size.width\
            - (self.canvas.max_x * self.canvas.zoom_x)
        self.canvas.Refresh()

        return True

    def _on_run(self, event) -> None:
        """Handle run/continue/play/pause operations."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print(_(u"Error! Please open a file first"))
            return

        # Get correct ID
        if event.GetId() in [
                self.RUN_ID, self.CLEAR_ID, self.PLAY_ID, self.PAUSE_ID]:
            Id = event.GetId()
        else:
            Id = event.GetEventObject().GetId()

        if Id == self.RUN_ID:
            if self.timer.IsRunning():
                print(_(u"Error! Already running simulation"))
            else:
                if not self.has_started:
                    self.cycles_completed = 0
                cycles = self.cycles_spin.GetValue()
                self._run_network(cycles=cycles)
                self.has_started = True
        elif Id == self.CLEAR_ID:
            if self.has_started and not self.timer.IsRunning():
                for monitor in self.monitors.monitors_dictionary:
                    self.monitors.monitors_dictionary[monitor] = []
                self.canvas.monitors_dictionary =\
                    self.monitors.monitors_dictionary
                self.cycles_completed = 0
                self.total_cycles_text.SetLabel(str(self.cycles_completed))
                self.Layout()
                self.canvas.pan_x = self.canvas.pan_y = 0
                self.canvas.Refresh()
                self.has_started = False
            else:
                print(_(u"Error! Unable to clear"))
        elif Id == self.PLAY_ID:
            if not self.timer.IsRunning():
                self.timer.Start(int(
                    self.DEF_SPEED
                    / self.SPEEDS[self.speed_slider.GetValue()]))
                self.has_started = True
            else:
                print(_(u"Error! Already running simulation"))
        elif Id == self.PAUSE_ID:
            if self.timer.IsRunning():
                self.timer.Stop()
            else:
                print(_(u"Error! Not running simulation"))

        if self.has_started:
            self.run_button.SetLabel(_(u"Continue"))
        else:
            self.run_button.SetLabel(_(u"Run"))

    def _on_scroll(self, event) -> None:
        """Handle canvas repositioning on scroll."""
        self.canvas.pan_x = -self.hscrollbar.GetThumbPosition()
        self.canvas.pan_y = self.vscrollbar.GetThumbPosition()
        self.canvas.Refresh()

    def generate_colours(self, n) -> list[list[float]]:
        """Generate n unique colours."""
        def hsv_to_rgb(h, s, v):
            i = int(h * 6)
            f = (h * 6) - i
            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)
            i = i % 6
            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            elif i == 5:
                r, g, b = v, p, q
            return [r, g, b]

        colours = []
        for i in range(n):
            h = i / max(n, 1)  # Hue from 0 to 1
            rgb = hsv_to_rgb(h, 1.0, 1.0)  # Full saturation and brightness
            colours.append(rgb)
        return colours

    def _quit(self, event) -> None:
        """Exit the program."""
        sys.exit()