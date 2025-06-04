import wx
import wx.glcanvas as glcanvas
from OpenGL import GL

class MyGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        attribs = [glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER]
        super().__init__(parent, attribList=attribs)
        self.context = glcanvas.GLContext(self)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.scroll_x = 0
        self.scroll_y = 0

        self.width = 1000
        self.height = 1000

    def set_scroll_offset(self, x, y):
        self.scroll_x = x
        self.scroll_y = y
        self.Refresh()

    def on_paint(self, event):
        self.SetCurrent(self.context)
        dc = wx.PaintDC(self)
        self.render()

    def render(self):
        GL.glViewport(0, 0, *self.GetClientSize())
        GL.glClearColor(0.9, 0.9, 0.9, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        width, height = self.GetClientSize()
        GL.glOrtho(0, width, height, 0, -1, 1)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslatef(-self.scroll_x, -self.scroll_y, 0)

        self.draw_scene()
        self.SwapBuffers()

    def draw_scene(self):
        # Draw a simple grid
        GL.glColor3f(0.0, 0.0, 0.0)
        GL.glBegin(GL.GL_LINES)
        for x in range(0, self.width, 50):
            GL.glVertex2f(x, 0)
            GL.glVertex2f(x, self.height)
        for y in range(0, self.height, 50):
            GL.glVertex2f(0, y)
            GL.glVertex2f(self.width, y)
        GL.glEnd()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Scrollable OpenGL Canvas", size=(800, 600))
        panel = wx.Panel(self)
        canvas = MyGLCanvas(panel)
        self.canvas = canvas

        h_scroll = wx.ScrollBar(panel, style=wx.SB_HORIZONTAL)
        v_scroll = wx.ScrollBar(panel, style=wx.SB_VERTICAL)

        h_scroll.SetScrollbar(0, 100, canvas.width, 100)
        v_scroll.SetScrollbar(0, 100, canvas.height, 100)

        h_scroll.Bind(wx.EVT_SCROLL, self.on_scroll)
        v_scroll.Bind(wx.EVT_SCROLL, self.on_scroll)

        self.h_scroll = h_scroll
        self.v_scroll = v_scroll

        sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer = wx.BoxSizer(wx.HORIZONTAL)
        canvas_sizer.Add(canvas, 1, wx.EXPAND)
        canvas_sizer.Add(v_scroll, 0, wx.EXPAND)

        sizer.Add(canvas_sizer, 1, wx.EXPAND)
        sizer.Add(h_scroll, 0, wx.EXPAND)

        panel.SetSizer(sizer)

    def on_scroll(self, event):
        scroll_x = self.h_scroll.GetThumbPosition()
        scroll_y = self.v_scroll.GetThumbPosition()
        self.canvas.set_scroll_offset(scroll_x, scroll_y)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
