"""Contains classes useful for 3D viewports."""
__all__ = ["Viewport", "ViewportManager"]

from pandac.PandaModules import WindowProperties
import wx

class ViewportManager:
  """Manages the global viewport stuff."""
  viewports = []

class Viewport(wx.Panel):
  """Class representing a 3D Viewport."""
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    self.Update()
    base.windowType = "onscreen"
    wp = WindowProperties.getDefault()
    wp.setOrigin(0, 0)
    wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
    assert self.GetHandle() != 0
    wp.setParentWindow(self.GetHandle())
    if len(ViewportManager.viewports) == 0:
      self.win = base.openDefaultWindow(props = wp)
    else:
      self.win = base.openWindow(props = wp)
    self.cam = base.camList[-1]
    ViewportManager.viewports.append(self)

