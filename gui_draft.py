# Adapted from an example by Dr Gee (CUED)
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
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(400, 400))
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        
        # Configure sizers for layout
        main_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        main_sizer.Add(upper_sizer, 0, wx.EXPAND, 0)
        main_sizer.Add(lower_sizer, 0, wx.EXPAND | wx.TOP, 10)

        io_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        switches_sizer = wx.StaticBoxSizer(wx.VERTICAL, self)
        upper_sizer.Add(io_sizer, 2, wx.EXPAND | wx.RIGHT, 10)
        upper_sizer.Add(switches_sizer, 1, wx.EXPAND, 0)
        
        fileio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        run_cont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        io_sizer.Add(fileio_sizer, 1, wx.ALL | wx.CENTER, 5)
        io_sizer.Add(cycles_sizer, 1, wx.ALL | wx.CENTER, 5)
        io_sizer.Add(run_cont_sizer, 1, wx.ALL | wx.CENTER, 5)


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
        spin = wx.SpinCtrl(self, wx.ID_ANY, '20')
        cycles_sizer.Add(spin, 0, wx.CENTER)

        # Run and continue widgets
        run_button = wx.Button(self, wx.ID_ANY, "Run")
        run_cont_sizer.Add(run_button, 1, wx.CENTER | wx.RIGHT, 10)
        cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        run_cont_sizer.Add(cont_button, 1, wx.CENTER)

        # Switches widgets
        text = wx.StaticText(self, wx.ID_ANY, "Switches")
        switches_sizer.Add(text, 0, wx.CENTER)
        self.AddSwitch(switches_sizer)

        # Monitor widgets
        text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        lower_sizer.Add(text, 0, wx.ALL | wx.CENTER, 10)
        self.AddMonitor(lower_sizer)
        add_image = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
        add_button = wx.BitmapButton(self, wx.ID_ANY, add_image)
        lower_sizer.Add(add_button, 0, wx.ALL, 20)


        # Bind events to widgets
        open_button.Bind(wx.EVT_BUTTON, self.OnOpenFile)
        # Add save option here


        # Set screen size
        self.SetSizeHints(500, 440)
        self.SetSize(570, 1070)
        self.SetSizer(main_sizer)
        self.SetPosition((0,39))

    def AddSwitch(self, sizer):
        """Add a switch to GUI"""
        switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(switch_sizer, 0, wx.CENTER)
        text = wx.StaticText(self, wx.ID_ANY, "Switch 1")
        switch_sizer.Add(text, 0, wx.CENTER | wx.RIGHT, 5)
        switch_radiobox = wx.RadioBox(self, wx.ID_ANY, "", choices=['0','1'])
        switch_sizer.Add(switch_radiobox, 0, wx.CENTER)

    def AddMonitor(self, sizer):
        """Add a monitor to GUI"""
        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, 0, 0)

        monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(monitor_sizer, 0, wx.EXPAND, 0)
        minus_image = wx.ArtProvider.GetBitmap(wx.ART_MINUS)
        zap_button = wx.BitmapButton(self, wx.ID_ANY, minus_image)
        choice = wx.Choice(self, choices = ["Monitor1", "Monitor2", "Monitor3"])
        monitor_sizer.Add(zap_button, 0, wx.ALL, 20)
        monitor_sizer.Add(choice, 0, wx.CENTER | wx.RIGHT, 15)
        monitor_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)

    def OnOpenFile(self, event):
        openFileDialog= wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("The user cancelled") 
            return     # the user changed idea...
        path=openFileDialog.GetPath()
        print("File chosen =",path)

        names = None
        devices = None
        network = None
        monitors = None

        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        if parser.parse_network():
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network,
                      monitors)
            app.MainLoop()
        
    def Toolbarhandler(self, event): 
        if event.GetId()==self.OpenID:
            openFileDialog= wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
               print("The user cancelled") 
               return     # the user changed idea...
            print("File chosen=",openFileDialog.GetPath())
            
app = wx.App()
gui = Gui("Logic Simulatorinator")
gui.Show(True)
app.MainLoop()
