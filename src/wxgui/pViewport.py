"""Contains classes useful for 3D viewports."""
__all__ = ["Viewport", "ViewportManager"]

from pandac.PandaModules import WindowProperties
import wx

from core.pWindow import WindowManager, Window

class ViewportManager(WindowManager):
  """Manages the global viewport stuff."""
  viewports = []

class Viewport(wx.Panel, Window):
  """Class representing a 3D Viewport."""
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
  
  def initialize(self):
    self.Update()
    wp = WindowProperties()
    wp.setOrigin(0, 0)
    wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
    assert self.GetHandle() != 0
    wp.setParentWindow(self.GetHandle())
    Window.__init__(self, extraProps = wp)
    ViewportManager.viewports.append(self)
    self.Bind(wx.EVT_SIZE, self.onSize)
  
  def onSize(self, evt):
    """Invoked when the viewport is resized."""
    if self.win != None:
      wp = WindowProperties()
      wp.setOrigin(0, 0)
      wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
      self.win.requestProperties(wp)

