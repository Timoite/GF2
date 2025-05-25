# Adapted from an example by Dr Gee (CUED)
import wx
from wx import ArtProvider
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner_original import Scanner
from parse import Parser


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

    def __init__(self, parent, devices, monitors):
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
    def __init__(self, title):

        self.names = None
        self.devices = None
        self.network = None
        self.monitors = None

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(400, 400))
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        # Configure sizers for layout
        self.main_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.main_sizer.Add(self.upper_sizer, 0, wx.EXPAND, 0)
        self.main_sizer.Add(self.lower_sizer, 0, wx.EXPAND | wx.TOP, 10)

        self.io_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.upper_sizer.Add(self.io_sizer, 2, wx.EXPAND | wx.RIGHT, 10)
        self.upper_sizer.Add(self.switches_sizer, 1, wx.EXPAND, 0)
        
        fileio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.io_sizer.Add(fileio_sizer, 1, wx.ALL | wx.CENTER, 5)
        self.io_sizer.Add(cycles_sizer, 1, wx.ALL | wx.CENTER, 5)
        self.io_sizer.Add(run_cont_sizer, 1, wx.ALL | wx.CENTER, 5)


        # Configure the widgets

        # File io widgets
        open_image = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        open_button = wx.BitmapButton(self, wx.ID_ANY, open_image)
        fileio_sizer.Add(open_button, 1, wx.RIGHT, 10)
        save_image = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR)
        save_button = wx.BitmapButton(self, wx.ID_ANY, save_image)
        fileio_sizer.Add(save_button, 1)

        # Cycles widgets
        text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        cycles_sizer.Add(text, 1, wx.CENTER | wx.RIGHT, 10)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, '20')
        cycles_sizer.Add(self.spin, 0, wx.CENTER)

        # Run and continue widgets
        run_button = wx.Button(self, wx.ID_ANY, "Run")
        run_cont_sizer.Add(run_button, 1, wx.CENTER | wx.RIGHT, 10)
        cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        run_cont_sizer.Add(cont_button, 1, wx.CENTER)

        # Switches widgets
        text = wx.StaticText(self, wx.ID_ANY, "Switches")
        self.switches_sizer.Add(text, 0, wx.CENTER)
        # self.AddSwitch("hello")
        # self.AddSwitch("goodbye")

        # Monitor widgets
        text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        self.lower_sizer.Add(text, 0, wx.ALL | wx.CENTER, 10)
        add_image = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
        add_button = wx.BitmapButton(self, wx.ID_ANY, add_image)
        self.lower_sizer.Add(add_button, 0, wx.ALL, 20)
        # self.AddMonitor()


        # Bind events to widgets
        open_button.Bind(wx.EVT_BUTTON, self.OpenFile)
        # Add save option here
        run_button.Bind(wx.EVT_BUTTON, self.Run)
        cont_button.Bind(wx.EVT_BUTTON, self.Continue)
        add_button.Bind(wx.EVT_BUTTON, self.AddMonitor)

        # Set screen size
        self.SetSizeHints(500, 440)
        self.SetSize(570, 1070)
        self.SetSizer(self.main_sizer)
        self.SetPosition((0,39))


    def AddSwitch(self, switch_id, switch_state):
        """Add a switch to GUI"""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switches_sizer.Add(switch_sizer, 0, wx.CENTER | wx.ALL, 5)
        text = wx.StaticText(self, wx.ID_ANY, switch_id)
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self, wx.ID_ANY, "", choices=['0','1'])
        switch_radiobox.SetSelection(switch_state)
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)
        switch_radiobox.Bind(wx.EVT_RADIOBOX, lambda evt, temp=switch_id: self.SwitchChanged(evt, temp))
        self.Layout()

    def SwitchChanged(self, event, switch_id):
        switch_state = event.GetSelection()
        if self.devices.set_switch(switch_id, switch_state):
            print("Successfully set switch.")
        else:
            print("Error! Invalid switch.")

    def CreateMonitor():
        """Create a new monitor"""

    def AddMonitor(self, event=None):
        """Add a monitor that already exists to GUI"""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Could not make monitor.")

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, 0, 0)

        monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Insert new monitor above the add button
        pos = len(self.lower_sizer.GetChildren()) - 1

        self.lower_sizer.Insert(pos, monitor_sizer, 0, wx.EXPAND, 0, id)
        minus_image = wx.ArtProvider.GetBitmap(wx.ART_MINUS)
        zap_button = wx.BitmapButton(self, wx.ID_ANY, minus_image)
        choice = wx.Choice(self, choices = ["Monitor1", "Monitor2", "Monitor3"])
        monitor_sizer.Add(zap_button, 0, wx.ALL, 20)
        monitor_sizer.Add(choice, 0, wx.CENTER | wx.RIGHT, 15)
        monitor_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()

        zap_button.Bind(wx.EVT_BUTTON, lambda evt, temp=pos: self.ZapMonitor(evt, temp))

    def ZapMonitor(self, event, pos):
        """Remove the specified monitor"""
        # Remove from monitors


        # Remove from GUI
        self.lower_sizer.GetChildren()[pos].DeleteWindows()
        self.Layout()



    def OpenFile(self, event):
        openFileDialog= wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("The user cancelled") 
            return     # the user changed idea...
        path=openFileDialog.GetPath()
        print("File chosen =",path)

        # Initialise instances of the four inner simulator classes
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)

        scanner = Scanner(path, self.names)
        parser = Parser(self.names, self.devices, self.network, self.monitors, scanner)
        if parser.parse_network():
            print("File parsed sucessfully")

        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        for switch_id in switch_ids:
            switch = self.devices.get_device(switch_id)
            switch_state = switch.switch_state
            self.AddSwitch(switch_id, switch_state)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        # TODO output onto canvas
        self.monitors.display_signals()
        return True

    def Run(self, event):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def Continue(self):
        """Continue a previously run simulation."""
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
