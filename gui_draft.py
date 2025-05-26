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
    instances = []
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

    def __init__(self, parent, monitor_name):
        """Initialise canvas properties and useful variables."""
        self.monitor_name = monitor_name
        MyGLCanvas.instances.append(self)
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

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

    def render(self, monitors_dictionary, devices):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Get values to draw
        [device_id, output_id] = self.devices.get_signal_ids(self.monitor_name)
        signal_list = monitors_dictionary[(device_id, output_id)]

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        i = 0
        y_HIGH = 40
        y_LOW = 20
        for signal in signal_list:
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if signal == devices.HIGH:
                y = y_HIGH
                y_next = y_HIGH
            if signal == devices.LOW:
                y = y_LOW
                y_next = y_LOW
            if signal == devices.RISING:
                y = y_LOW
                y_next = y_HIGH
            if signal == devices.FALLING:
                y = y_HIGH
                y_next = y_LOW
            if signal == devices.BLANK:
                i += 1
                continue
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y_next)
            i += 1
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()


class Gui(wx.Frame):
    def __init__(self, title):

        self.names = None
        self.devices = None
        self.network = None
        self.monitors = None
        self.cycles_completed = 0

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
        # save_image = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR)
        # save_button = wx.BitmapButton(self, wx.ID_ANY, save_image)
        # fileio_sizer.Add(save_button, 1)

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
        self.add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer.Add(self.add_sizer, wx.CENTER)
        add_image = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
        add_button = wx.BitmapButton(self, wx.ID_ANY, add_image)
        self.choice = wx.Choice(self, choices = [])
        self.add_sizer.Add(add_button, 0, wx.ALL, 20)
        self.add_sizer.Add(self.choice, 0, wx.CENTER | wx.RIGHT, 15)
        # self.AddMonitor()


        # Bind events to widgets
        open_button.Bind(wx.EVT_BUTTON, self.OpenFile)
        run_button.Bind(wx.EVT_BUTTON, self.Run)
        cont_button.Bind(wx.EVT_BUTTON, self.Continue)
        add_button.Bind(wx.EVT_BUTTON, self.CreateMonitor)

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

    def CreateMonitor(self, event):
        """Create a new monitor"""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open file before creating monitor.")
            return
        
        signal_int = self.choice.GetSelection()
        signal_name = self.all_signal_list[signal_int]

        """Add the specified signal to the monitors dictionary.

        Return NO_ERROR if successful, or the corresponding error if not.
        """
        [device_id, output_id] = self.devices.get_signal_ids(signal_name)
        monitor_device = self.devices.get_device(device_id)
        if monitor_device is None:
            return self.network.DEVICE_ABSENT
        elif output_id not in monitor_device.outputs:
            return self.monitors.NOT_OUTPUT
        elif (device_id, output_id) in self.monitors.monitors_dictionary:
            return self.monitors.MONITOR_PRESENT
        else:
            # If n simulation cycles have been completed before making this
            # monitor, then initialise the signal trace with an n-length list
            # of BLANK signals. Otherwise, initialise the trace with an empty
            # list.
            self.monitors.monitors_dictionary[(device_id, output_id)] = [
                self.devices.BLANK] * self.cycles_completed
            # add to gui
            self.AddMonitor(signal_name)
            return self.NO_ERROR

    def AddMonitor(self, signal_name):
        """Add a monitor that already exists to GUI"""

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, signal_name)

        monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Insert new monitor above the add button
        pos = len(self.lower_sizer.GetChildren()) - 1

        self.lower_sizer.Insert(pos, monitor_sizer, 0, wx.EXPAND, 0, id)
        minus_image = wx.ArtProvider.GetBitmap(wx.ART_MINUS)
        zap_button = wx.BitmapButton(self, wx.ID_ANY, minus_image)
        text = wx.StaticText(self, wx.ID_ANY, signal_name)
        monitor_sizer.Add(zap_button, 0, wx.ALL, 20)
        monitor_sizer.Add(text, 1, wx.CENTER | wx.RIGHT, 10)
        monitor_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()

        zap_button.Bind(wx.EVT_BUTTON, lambda evt, temp=pos, temp2=signal_name: self.ZapMonitor(evt, temp, temp2))


    def ZapMonitor(self, event, pos, signal_name):
        """Remove the specified monitor"""
        # Remove from monitors
        [device, port] = self.devices.get_signal_ids(signal_name)
        if self.monitors.remove_monitor(device, port):
            # Remove from GUI
            self.lower_sizer.GetChildren()[pos].DeleteWindows()
            self.Layout()
            print("Successfully zapped monitor")
        else:
            print("Error! Could not zap monitor.")


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

        [monitored_signal_list, non_monitored_signal_list] = self.monitors.get_signal_names()
        self.all_signal_list = monitored_signal_list + non_monitored_signal_list

        self.choice.SetItems(self.all_signal_list)

        for monitored_signal_name in monitored_signal_list:
            self.AddMonitor(monitored_signal_name)


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
        
        for canvas in MyGLCanvas.instances:
            canvas.render(self.monitors.monitors_dictionary, self.devices)


            
        return True

    def Run(self, event):
        """Run the simulation from scratch."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open file before running.")
            return
        
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def Continue(self, event):
        """Continue a previously run simulation."""
        # Handle the case that no file has yet been opened
        if not self.monitors:
            print("Error! Please open file before continuing.")
            return
        
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
