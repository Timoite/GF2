import wx
import wx.glcanvas as glcanvas
from OpenGL.GL import *

class MyGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, size):
        attribs = [glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 16, 0]
        super().__init__(parent, attribList=attribs, size=size)
        self.context = glcanvas.GLContext(self)
        self.zoom = 1.0  # initial zoom factor
        self.base_size = size
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

    def on_size(self, event):
        self.SetCurrent(self.context)
        width, height = self.GetClientSize()
        glViewport(0, 0, width, height)
        event.Skip()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        self.draw()
        self.SwapBuffers()

    def on_mouse_wheel(self, event):
        # Simulated "pinch" detection using Ctrl + scroll
        if event.ControlDown():  # Ctrl + two-finger scroll = "zoom"
            delta = event.GetWheelRotation()
            if delta > 0:
                self.zoom *= 1.1
            else:
                self.zoom /= 1.1
            self.update_zoom()
        else:
            event.Skip()  # let parent handle scroll normally
        

    def update_zoom(self):
        # Resize the virtual area based on the zoom level
        new_width = int(self.base_size[0] * self.zoom)
        new_height = int(self.base_size[1] * self.zoom)
        self.SetSize((new_width, new_height))

        if isinstance(self.GetParent(), wx.ScrolledWindow):
            self.GetParent().SetVirtualSize((new_width, new_height))
            self.GetParent().RefreshScrollbars()
        self.Refresh()

    def draw(self):
        glClearColor(1.0, 1.0, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScalef(self.zoom, self.zoom, 1.0)

        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(-0.5, -0.5)
        glVertex2f(0.5, -0.5)
        glVertex2f(0.0, 0.5)
        glEnd()

class ScrollableGLPanel(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetScrollRate(20, 20)
        self.canvas_size = (800, 600)

        self.gl_canvas = MyGLCanvas(self, size=self.canvas_size)
        self.gl_canvas.SetPosition((0, 0))

        self.SetVirtualSize(self.canvas_size)
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)

    def RefreshScrollbars(self):
        # Called when zoom level changes
        self.Layout()
        self.Refresh()
        self.Update()

    def on_scroll(self, event):
        x, y = self.GetViewStart()
        px, py = self.GetScrollPixelsPerUnit()
        self.gl_canvas.SetPosition((-x * px, -y * py))
        self.gl_canvas.Refresh()
        event.Skip()

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxGLCanvas with Zoom and Scrollbars", size=(600, 400))
        ScrollableGLPanel(self)
        self.Show()

class MyApp(wx.App):
    def OnInit(self):
        MyFrame()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
