"""Contains classes useful for 3D viewports."""
__all__ = ["Viewport", "ViewportManager", "ViewportSplitter", "ViewportGrid"]

from pandac.PandaModules import WindowProperties, OrthographicLens, Point3
import wx

from core.pWindow import WindowManager, Window

HORIZONTAL = wx.SPLIT_HORIZONTAL
VERTICAL   = wx.SPLIT_VERTICAL
CREATENEW  = 99
VPLEFT     = 10
VPFRONT    = 11
VPTOP      = 12
VPPERSPECTIVE = 13

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
  CREATENEW  = CREATENEW
  VPLEFT     = VPLEFT
  VPFRONT    = VPFRONT
  VPTOP      = VPTOP
  VPPERSPECTIVE = VPPERSPECTIVE
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    ViewportManager.viewports.append(self)
    self.lens = None
    self.camPos = None
    self.camLookAt = None
  
  def initialize(self):
    self.Update()
    wp = WindowProperties()
    wp.setOrigin(0, 0)
    wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
    assert self.GetHandle() != 0
    wp.setParentWindow(self.GetHandle())
    Window.__init__(self, extraProps = wp)
    if self.lens != None:      self.camera.node().setLens(self.lens)
    if self.camPos != None:    self.camera.setPos(self.camPos)
    if self.camLookAt != None: self.camera.lookAt(self.camLookAt)
    self.Bind(wx.EVT_SIZE, self.onSize)
  
  def onSize(self, evt):
    """Invoked when the viewport is resized."""
    if self.win != None:
      wp = WindowProperties()
      wp.setOrigin(0, 0)
      wp.setSize(self.ClientSize.GetWidth(), self.ClientSize.GetHeight())
      self.win.requestProperties(wp)
  
  @staticmethod
  def make(parent, vpType = None):
    """Safe constructor that also takes CREATENEW, VPLEFT, VPTOP, etc."""
    if vpType == None or vpType == CREATENEW:
      return Viewport(parent)
    if isinstance(vpType, Viewport): return vpType
    if isinstance(vpType, ViewportSplitter): return vpType
    if isinstance(vpType, ViewportGrid): return vpType
    if vpType == VPLEFT:  return Viewport.makeLeft(parent)
    if vpType == VPFRONT: return Viewport.makeFront(parent)
    if vpType == VPTOP:   return Viewport.makeTop(parent)
    if vpType == VPPERSPECTIVE:  return Viewport.makePerspective(parent)
    raise TypeError, "Unknown viewport type: %s" % vpType
  
  @staticmethod
  def makeOrthographic(parent, campos):
    v = Viewport(parent)
    v.lens = OrthographicLens()
    v.lens.setFilmSize(30)
    v.camPos = campos
    v.camLookAt = Point3(0, 0, 0)
    return v
  
  @staticmethod
  def makePerspective(parent):
    v = Viewport(parent)
    v.camPos = Point3(30, 30, 30)
    v.camLookAt = Point3(0, 0, 0)
    return v
  
  @staticmethod
  def makeLeft(parent): return Viewport.makeOrthographic(parent, Point3(1, 0, 0))
  @staticmethod
  def makeFront(parent): return Viewport.makeOrthographic(parent, Point3(0, 1, 0))
  @staticmethod
  def makeTop(parent): return Viewport.makeOrthographic(parent, Point3(0, 0, 1))

class ViewportSplitter(wx.SplitterWindow):
  """ A splitterwindow used to split two viewports. """
  HORIZONTAL = HORIZONTAL
  VERTICAL   = VERTICAL
  CREATENEW  = CREATENEW
  VPLEFT     = VPLEFT
  VPFRONT    = VPFRONT
  VPTOP      = VPTOP
  VPPERSPECTIVE = VPPERSPECTIVE
  def __init__(self, parent, win1 = None, win2 = None, orientation = None):
    """win1 and win2 must be either a Viewport, ViewportSplitter, or None.
    If the parameters are not supplied, you can split later using split()."""
    wx.SplitterWindow.__init__(self, parent)
    self.win1 = win1
    self.win2 = win2
    self.prevSize = self.ClientSize
    if win1 != None and win2 != None and orientation != None:
      self.split(win1, win2, orientation)
    self.Bind(wx.EVT_SPLITTER_DCLICK, lambda evt: evt.Veto(0))
  
  def onSize(self, evt):
    d = self.ClientSize - self.prevSize
    self.prevSize = self.ClientSize
    if self.GetSplitMode() == wx.SPLIT_VERTICAL:
      d = d.GetWidth()
    elif self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
      d = d.GetHeight()
    else: return
    self.SetSashPosition(self.GetSashPosition() + (d / 2))
  
  def split(self, win1, win2, orientation):
    win1 = Viewport.make(self, win1)
    win2 = Viewport.make(self, win2)
    assert isinstance(win1, Viewport) or isinstance(win1, ViewportSplitter)
    assert isinstance(win2, Viewport) or isinstance(win2, ViewportSplitter)
    self.win1 = win1
    self.win2 = win2
    if orientation == self.HORIZONTAL:
      self.SplitHorizontally(win1, win2)
    elif orientation == self.VERTICAL:
      self.SplitVertically(win1, win2)
    self.Bind(wx.EVT_SIZE, self.onSize)
  
  def initialize(self, *args, **kwargs):
    self.win1.initialize(*args, **kwargs)
    self.win2.initialize(*args, **kwargs)
  
  def Update(self, *args, **kwargs):
    self.win1.Update()
    self.win2.Update()
    wx.SplitterWindow.Update(self, *args, **kwargs)
  
  def __getitem__(self, num):
    if num != 0 and num != 1: return
    if num == 0: return self.win1
    if num == 1: return self.win2
  
  def __setitem__(self, num, value):
    if num != 0 and num != 1: return
    if value == self.CREATENEW:
      value = Viewport(self)
    if num == 0: self.win1 = value
    if num == 1: self.win2 = value
  
  def __len__(self):
    return 2

class ViewportGrid(ViewportSplitter):
  """Represents a 4x4 grid of viewports. It's pretty limited right now."""
  HORIZONTAL = HORIZONTAL
  VERTICAL   = VERTICAL
  CREATENEW  = CREATENEW
  VPLEFT     = VPLEFT
  VPFRONT    = VPFRONT
  VPTOP      = VPTOP
  VPPERSPECTIVE = VPPERSPECTIVE
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
  
  def center(self):
    """Centers the splitters."""
    self.SetSashPosition(self.ClientSize.GetWidth() / 2)
    for s in range(len(self)):
      self[s].SetSashPosition(self.ClientSize.GetHeight() / 2)
