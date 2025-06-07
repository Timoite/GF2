"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
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

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.max_x = 2000
        self.max_y = 2000
        self.size = self.GetClientSize()
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
            self.init_gl()
            self.init = True

        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # ---- Render centered text ----
        size = self.GetClientSize()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        center_x = size.width // 2
        center_y = size.height // 2
        self.render_text(text, center_x, center_y, "center")

        # Apply pan and zoom
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

        # ---- Draw zoom/pan-sensitive content here ----
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            y = 75 if i % 2 == 0 else 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        self.render_text("start", 0, center_y, "left")
        self.render_text("end", self.max_x, center_y, "right")

        GL.glFlush()
        self.SwapBuffers()


    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(self.size.width), ", ", str(self.size.height)])
        self.render(text)
        self.parent.update_scrollbars()

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

        wheel_rotation, wheel_delta = event.GetWheelRotation(), event.GetWheelDelta()
        if wheel_rotation != 0:
            # Zooming
            if event.ControlDown():
                if wheel_rotation < 0:
                    self.zoom *= (1.0 + (
                        wheel_rotation / (20 * wheel_delta)))
                if wheel_rotation > 0:
                    self.zoom /= (1.0 - (
                        wheel_rotation / (20 * wheel_delta)))
                # Adjust pan so as to zoom around the mouse position
                self.pan_x -= (self.zoom - old_zoom) * ox
                self.pan_y -= (self.zoom - old_zoom) * oy

            # Horizontal panning
            elif event.ShiftDown():
                dPANx = 10
                if wheel_rotation < 0:
                    self.pan_x += dPANx
                if wheel_rotation > 0:
                    self.pan_x -= dPANx


            # Vertical panning
            else:
                dPANy = 10
                if wheel_rotation < 0:
                    self.pan_y += dPANy
                if wheel_rotation > 0:
                    self.pan_y -= dPANy
            
            self.init = False


        # if self.pan_x < 0:
        #     self.pan_x = 0

        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, align=None):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        if align == "center":
            # Measure total width of the text (ignores line breaks for simplicity)
            lines = text.split('\n')
            max_line_width = max(sum(GLUT.glutBitmapWidth(font, ord(c)) for c in line) for line in lines)
            x_pos = x_pos - (max_line_width / 4)

        elif align == "right":
            # Measure total width of the text (ignores line breaks for simplicity)
            lines = text.split('\n')
            max_line_width = max(sum(GLUT.glutBitmapWidth(font, ord(c)) for c in line) for line in lines)
            x_pos = x_pos - (max_line_width / 2)

        GL.glRasterPos2f(x_pos, y_pos)
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

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        
        self.hscrollbar = wx.ScrollBar(self, style=wx.HORIZONTAL)
        self.vscrollbar = wx.ScrollBar(self, style=wx.VERTICAL)
        self.hscrollbar.SetScrollbar(0, 20, 50, 15)
        self.vscrollbar.SetScrollbar(0, 20, 50, 15)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.hscrollbar.Bind(wx.EVT_SCROLL, self.on_scroll)
        self.vscrollbar.Bind(wx.EVT_SCROLL, self.on_scroll)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=0)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(left_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        left_sizer.AddGrowableCol(0, 1)
        left_sizer.AddGrowableRow(0, 1)
        left_sizer.Add(self.canvas, 1, wx.EXPAND)
        left_sizer.Add(self.vscrollbar, 0, wx.EXPAND)
        left_sizer.Add(self.hscrollbar, 0, wx.EXPAND)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_scroll(self, event):
        self.canvas.pan_x = -self.hscrollbar.GetThumbPosition()
        self.canvas.pan_y = self.vscrollbar.GetThumbPosition()
        self.canvas.render("hello")

    def update_scrollbars(self):
        pan_x, pan_y = self.canvas.pan_x, self.canvas.pan_y
        width, height = self.canvas.size.width, self.canvas.size.height
        max_x, max_y = self.canvas.max_x, self.canvas.max_y
        zoom = self.canvas.zoom
        self.hscrollbar.SetScrollbar(int(-pan_x), int(width), int(max_x * zoom), 0)
        self.vscrollbar.SetScrollbar(int(pan_y), int(height), int(max_y * zoom), 0)

app = wx.App()
gui = Gui("Demo")
gui.Show(True)
app.MainLoop()