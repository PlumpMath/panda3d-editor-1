__all__ = ["EditorApp"]

from pandac.PandaModules import loadPrcFileData, WindowProperties, CompassEffect, Filename, BoundingSphere, deg2Rad, Vec3
from direct.wxwidgets.WxAppShell import WxAppShell as AppShell
# temporarely changed be Hypnos doesnt have cvs
#from direct.directtools.DirectGrid import DirectGrid
from core.pGrid import DirectGrid
import wx
from math import tan

# Local imports
from pPropertyGrid import PropertyGrid
from pSceneGraphTree import SceneGraphTree

# Get the default window origin
defWP = WindowProperties.getDefault()
if defWP.hasOrigin():
  origin = defWP.getXOrigin(), defWP.getYOrigin()
else:
  origin = (0, 0)

ID_ENABLE_GRID = 2

class EditorApp(AppShell):
  appversion    = "cvs"
  appname       = "Panda Editor"
  copyright     = "Copyright (c) Carnegie Mellon University.\nAll rights reserved."
  contactname   = "pro-rsoft"
  contactemail  = "niertie1@gmail.com"
  frameWidth    = defWP.getXSize()
  frameHeight   = defWP.getYSize()
  
  def __init__(self, editorInstance):
    # Instance of the editor
    self.editorInstance = editorInstance
    
    # Create the Wx app
    self.wxApp = wx.App(redirect = False)
    self.wxApp.SetAppName("Panda Editor")
    self.wxApp.SetClassName("PEditor")
    
    self.scene = render.attachNewNode("scene")
    self.modified = True
    self.filename = Filename()
    
    # Initialize the app shell and add some controls
    AppShell.__init__(self, title = "Panda Editor", pos = origin)
    self.splitter = wx.SplitterWindow(self, style = wx.SP_3D | wx.SP_BORDER)
    self.sideBarSplitter = wx.SplitterWindow(self.splitter, style = wx.SP_3D | wx.SP_BORDER)
    self.sceneGraphTree = SceneGraphTree(self.sideBarSplitter)
    self.propertyGrid = PropertyGrid(self.sideBarSplitter)
    self.panel3D = wx.Panel(self.splitter)
    sizer = wx.BoxSizer(wx.VERTICAL)
    assert self.sideBarSplitter.SplitHorizontally(self.sceneGraphTree, self.propertyGrid)
    assert self.splitter.SplitVertically(self.sideBarSplitter, self.panel3D, 200)
    sizer.Add(self.splitter, 1, wx.EXPAND, 0)
    self.SetSizer(sizer)
    self.Layout()

    # Setup the panda stuff
    self.setupPandaWindow()
    self.editorInit()
    self.sceneGraphTree.reload()
    
    # Setup some events
    self.panel3D.Bind(wx.EVT_SIZE, self.onPanelSize)
    base.accept("c", self.onCenterTrackball)
  
  def appInit(self):
    # Create a new event loop (to overide default wxEventLoop)
    self.evtLoop = wx.EventLoop()
    self.oldLoop = wx.EventLoop.GetActive()
    wx.EventLoop.SetActive(self.evtLoop)
    taskMgr.add(self.wxStep, "evtLoopTask")
  
  def createMenuBar(self):
    # File menu
    self.menuFile = wx.Menu()
    self.menuBar.Append(self.menuFile, "&File")
    self.Bind(wx.EVT_MENU, self.onNew, self.menuFile.Append(wx.ID_NEW, "&New"))
    self.Bind(wx.EVT_MENU, self.onOpen, self.menuFile.Append(wx.ID_OPEN, "&Open"))
    self.Bind(wx.EVT_MENU, self.onSave, self.menuFile.Append(wx.ID_SAVE, "&Save"))
    self.Bind(wx.EVT_MENU, self.onSaveAs, self.menuFile.Append(wx.ID_SAVEAS, "Save &As..."))
    self.menuFile.AppendSeparator()
    self.Bind(wx.EVT_MENU, self.quit, self.menuFile.Append(wx.ID_EXIT, "&Quit"))
    
    # Edit menu
    self.menuEdit = wx.Menu()
    self.menuBar.Append(self.menuEdit, "&Edit")
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_UNDO, "&Undo"))
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_REDO, "&Redo"))
    self.menuEdit.AppendSeparator()
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_CUT, "Cu&t"))
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_COPY, "&Copy"))
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_PASTE, "&Paste"))
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_DELETE, "&Delete"))
    self.menuEdit.AppendSeparator()
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_SELECTALL, "Select &All"))
    self.Bind(wx.EVT_MENU, self.quit, self.menuEdit.Append(wx.ID_ANY, "Select &None"))
    
    # View menu
    self.menuView = wx.Menu()
    self.menuBar.Append(self.menuView, "&View")
    self.Bind(wx.EVT_MENU, self.onToggleGrid, self.menuView.AppendCheckItem(ID_ENABLE_GRID, "E&nable Grid"))
    self.Bind(wx.EVT_MENU, self.onCenterTrackball, self.menuView.Append(wx.ID_ANY, "&Center Model"))
    self.Bind(wx.EVT_MENU, self.onChooseColor, self.menuView.Append(wx.ID_ANY, "&Background Color..."))
    self.menuBar.Check(ID_ENABLE_GRID, True)
  
  def createInterface(self):
    self.CreateStatusBar()
    self.SetStatusText("Welcome to the Panda3D Editor")
    self.Update()
  
  def setupPandaWindow(self):
    self.Update()
    self.panel3D.Update()
    self.wxStep()
    base.windowType = "onscreen"
    wp = WindowProperties.getDefault()
    wp.setOrigin(0, 0)
    wp.setSize(self.panel3D.GetClientSize().GetWidth(), self.panel3D.GetClientSize().GetHeight())
    assert self.panel3D.GetHandle() != 0
    wp.setParentWindow(self.panel3D.GetHandle())
    base.openDefaultWindow(props = wp)
    self.Raise()
  
  def editorInit(self):
    # Add a small axis indicator in the bottom of the screen
    self.axisPivot = base.a2dBottomLeft.attachNewNode("axisPivot")
    self.axisPivot.setPos(0.1, 0, 0.1)
    self.axisPivot.setScale(0.01)
    self.axis = loader.loadModel("models/misc/xyzAxis")
    self.axis.reparentTo(self.axisPivot)
    self.axis.node().setEffect(CompassEffect.make(base.camera))
    
    # Position the camera
    base.trackball.node().setPos(0, 30, 0)
    base.trackball.node().setHpr(0, 15, 0)
    
    # Load the direct things
    self.grid = DirectGrid(parent = render)
  
  def wxStep(self, task = None):
    while self.evtLoop.Pending():
      self.evtLoop.Dispatch()
    self.wxApp.ProcessIdle()
    if task != None: return task.cont
  
  def onDestroy(self, event):
    wx.EventLoop.SetActive(self.oldLoop)
  
  def onPanelSize(self, sizeEvt = None):
    if(base.win != None): # Make sure we have a window
      wp = WindowProperties()
      wp.setOrigin(0, 0)
      wp.setSize(self.panel3D.GetClientSize().GetWidth(), self.panel3D.GetClientSize().GetHeight())
      base.win.requestProperties(wp)
  
  def onNew(self, evt = None):
    self.filename = Filename()
    self.modified = True
    self.SetTitle("Panda Editor")
    self.scene.removeNode()
    self.scene = render.attachNewNode("scene")
  
  def onOpen(self, evt = None):
    filter = "Panda3D Binary Format (*.bam)|*.[bB][aA][mM]"
    filter += "|Panda3D Egg Format (*.egg)|*.[eE][gG][gG]"
    ''' # disabled by hypnos, making the loading work
    filter += "|MultiGen (*.flt)|*.[fF][lL][tT]"
    filter += "|Lightwave (*.lwo)|*.[lL][wW][oO]"
    filter += "|AutoCAD (*.dxf)|*.[dD][xX][fF]"
    filter += "|VRML (*.wrl)|*.[wW][rR][lL]"
    filter += "|DirectX (*.x)|*.[xX]"
    filter += "|COLLADA (*.dae)|*.[dD][aA][eE]" '''
    dlg = wx.FileDialog(self, "Load file", "", "", filter, wx.OPEN)
    try:
      if dlg.ShowModal() == wx.ID_OK:
        #self.filename = Filename.fromOsSpecific(dlg.GetPath())
        p3dFilename = Filename.fromOsSpecific(dlg.GetPath())
        self.filename = str(dlg.GetPath())
        self.SetTitle(p3dFilename.getBasename() + " - Panda Editor")
        self.modified = False
        self.editorInstance.loadEggModelsFile( self.filename )
        #self.scene.removeNode()
        #self.scene = loader.loadModel(self.filename)
        #self.scene.reparentTo(render)
        # Reset the camera
        base.trackball.node().setPos(0, 30, 0)
        base.trackball.node().setHpr(0, 15, 0)
        self.onCenterTrackball()
        if p3dFilename.getExtension().lower() != "bam":
          self.filename = Filename()
          self.modified = True
        self.sceneGraphTree.reload()
    finally:
      dlg.Destroy()
  
  def onSave(self, evt = None):
    if not self.modified: return
    if self.filename == None or self.filename.empty():
      self.onSaveAs(evt)
    else:
      dlg = wx.FileDialog(self, "Save file", "", "", "Panda3D Binary Format (*.bam)|.[bB][aA][mM]", wx.SAVE | wx.FD_OVERWRITE_PROMPT)
      try:
        if dlg.ShowModal() == wx.ID_OK:
          self.filename = Filename.fromOsSpecific(dlg.GetPath())
          self.SetTitle(self.filename.getBasename() + " - Panda Editor")
          self.modified = False
          self.scene.writeBamFile(self.filename)
      finally:
        dlg.Destroy()
  
  def onSaveAs(self, evt = None):
    dlg = wx.FileDialog(self, "Save file as", "", "", "Panda3D Binary Format (*.bam)|.[bB][aA][mM]", wx.SAVE | wx.FD_OVERWRITE_PROMPT)
    try:
      if dlg.ShowModal() == wx.ID_OK:
        self.onNew()
        self.filename = Filename.fromOsSpecific(dlg.GetPath())
        self.SetTitle(self.filename.getBasename() + " - Panda Editor")
        self.modified = False
        self.scene.writeBamFile(self.filename)
    finally:
      dlg.Destroy()
  
  def onToggleGrid(self, evt = None):
    if evt.GetEventObject().IsChecked(ID_ENABLE_GRID):
      self.grid.enable(parent = render)
    else:
      self.grid.disable()
  
  def onCenterTrackball(self, evt = None):
    gbv = self.scene.getBounds();
    # Determine the bounding sphere around the object.
    if gbv.isInfinite(): return
    if gbv.isEmpty(): return
    
    # The BoundingVolume might be a sphere (it's likely), but since it
    # might not, we'll take no chances and make our own sphere.
    sphere = BoundingSphere(gbv.getApproxCenter(), 0.0)
    if (not sphere.extendBy(gbv)): return
    
    radius = 50.0
    
    # Choose a suitable distance to view the whole volume in our frame.
    # This is based on the camera lens in use.
    fov = base.camLens.getFov();
    distance = radius / tan(deg2Rad(min(fov[0], fov[1]) / 2.0));
    
    # Ensure the far plane is far enough back to see the entire object.
    idealFarPlane = distance + radius * 1.5;
    base.camLens.setFar(max(base.camLens.getDefaultFar(), idealFarPlane));
    
    # And that the near plane is far enough forward.
    base.camLens.setNear(min(base.camLens.getDefaultNear(), radius - sphere.getRadius()))
    
    base.trackball.node().setOrigin(sphere.getCenter())
    base.trackball.node().setPos(Vec3.forward() * distance)
    
    # Also set the movement scale on the trackball to be consistent
    # with the size of the model and the lens field-of-view.
    base.trackball.node().setForwardScale(distance * 0.006)
  
  def onChooseColor(self, evt = None):
    data = wx.ColourData()
    bgcolor = base.getBackgroundColor()
    bgcolor = bgcolor[0] * 255.0, bgcolor[1] * 255.0, bgcolor[2] * 255.0
    data.SetColour(bgcolor)
    dlg = wx.ColourDialog(self, data)
    try:
      if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetColourData().GetColour()
        data = data[0] / 255.0, data[1] / 255.0, data[2] / 255.0
        base.setBackgroundColor(*data)
    finally:
      dlg.Destroy()

