"""Contains classes useful for 3D viewports."""
__all__ = ["Viewport", "ViewportManager", "ViewportSplitter", "ViewportGrid"]

from pandac.PandaModules import WindowProperties
import wx

from core.pWindow import WindowManager, Window

HORIZONTAL = wx.HORIZONTAL
VERTICAL   = wx.VERTICAL
CREATENEW  = 99

class ViewportManager(WindowManager):
  """Manages the global viewport stuff."""
  viewports = []
  
  @staticmethod
  def initializeAll(*args, **kwargs):
    for v in ViewportManager.viewports:
      v.initialize(*args, **kwargs)
  
  @staticmethod
  def updateAll(*args, **kwargs):
    for v in ViewportManager.viewports:
      v.Update(*args, **kwargs)

class Viewport(wx.Panel, Window):
  """Class representing a 3D Viewport."""
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    ViewportManager.viewports.append(self)
  
  def initialize(self):
    self.Update()
    wp = WindowProperties()
    wp.setOrigin(0, 0)
    wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
    assert self.GetHandle() != 0
    wp.setParentWindow(self.GetHandle())
    Window.__init__(self, extraProps = wp)
    self.Bind(wx.EVT_SIZE, self.onSize)
  
  def onSize(self, evt):
    """Invoked when the viewport is resized."""
    if self.win != None:
      wp = WindowProperties()
      wp.setOrigin(0, 0)
      wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
      self.win.requestProperties(wp)

class ViewportSplitter(wx.SplitterWindow):
  """ A splitterwindow used to split two viewports. """
  HORIZONTAL = HORIZONTAL
  VERTICAL   = VERTICAL
  CREATENEW  = CREATENEW
  def __init__(self, parent, win1 = None, win2 = None, orientation = None):
    """win1 and win2 must be either a Viewport, ViewportSplitter, or None.
    If the parameters are not supplied, you can split later using split()."""
    wx.SplitterWindow.__init__(self, parent)
    self.win1 = win1
    self.win2 = win2
    if win1 != None and win2 != None and orientation != None:
      self.split(win1, win2, orientation)
    self.Bind(wx.EVT_SPLITTER_DCLICK, lambda evt: evt.Veto(0))
  
  def split(self, win1, win2, orientation):
    if win1 == self.CREATENEW: win1 = Viewport(self)
    if win2 == self.CREATENEW: win2 = Viewport(self)
    assert isinstance(win1, Viewport) or isinstance(win1, ViewportSplitter)
    assert isinstance(win2, Viewport) or isinstance(win2, ViewportSplitter)
    self.win1 = win1
    self.win2 = win2
    if orientation == self.HORIZONTAL:
      self.SplitHorizontally(win1, win2)
    elif orientation == self.VERTICAL:
      self.SplitVertically(win1, win2)
  
  def initialize(self, *args, **kwargs):
    self.win1.initialize(*args, **kwargs)
    self.win2.initialize(*args, **kwargs)
  
  def Update(self, *args, **kwargs):
    self.win1.Update()
    self.win2.Update()
    wx.SplitterWindow.Update(self, *args, **kwargs)
  
  def __getitem__(self, num):
    assert num == 0 or num == 1
    if num == 0: return self.win1
    if num == 1: return self.win2
  
  def __setitem__(self, num, value):
    assert num == 0 or num == 1
    if value == self.CREATENEW:
      value = Viewport(self)
    if num == 0: self.win1 = value
    if num == 1: self.win2 = value

class ViewportGrid(ViewportSplitter):
  """Represents a 4x4 grid of viewports. It's pretty limited right now."""
  HORIZONTAL = HORIZONTAL
  VERTICAL   = VERTICAL
  CREATENEW  = CREATENEW
  def __init__(self, parent, grid):
    """The "grid" argument should be a two-dimensional list of either Viewports or CREATENEW."""
    if grid == CREATENEW: grid = [[CREATENEW, CREATENEW], [CREATENEW, CREATENEW]]
    assert len(grid) == 2
    assert len(grid[0]) == len(grid[1]) == 2
    ViewportSplitter.__init__(self, parent)
    splitters = [
        ViewportSplitter(self, grid[0][0], grid[0][1], HORIZONTAL),
        ViewportSplitter(self, grid[1][0], grid[1][1], HORIZONTAL),
      ]
    self.split(splitters[0], splitters[1], VERTICAL)
    splitters[0].Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
      lambda evt: self[1].SetSashPosition(self[0].GetSashPosition()))
    splitters[1].Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
      lambda evt: self[0].SetSashPosition(self[1].GetSashPosition()))
    splitters[0].Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
      lambda evt: self[1].SetSashPosition(self[0].GetSashPosition()))
    splitters[1].Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
      lambda evt: self[0].SetSashPosition(self[1].GetSashPosition()))
