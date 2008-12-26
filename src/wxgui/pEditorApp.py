__all__ = ["EditorApp"]

from pandac.PandaModules import loadPrcFileData, WindowProperties, CompassEffect, Filename, BoundingSphere, deg2Rad, Vec3
from direct.wxwidgets.WxAppShell import WxAppShell as AppShell
# temporarely changed be Hypnos doesnt have cvs
#from direct.directtools.DirectGrid import DirectGrid
from core.pGrid import DirectGrid
from core.pConfigDefs import *
from core.pWindow import WindowManager
from core.pModelController import modelController
from core.modules.pAmbientLightNodeWrapper import AmbientLightNodeWrapper
from core.modules.pBaseWrapper import BaseWrapper
from core.modules.pCodeNodeWrapper import CodeNodeWrapper
from core.modules.pDirectionalLightNodeWrapper import DirectionalLightNodeWrapper
from core.modules.pGeoMipTerrainNodeWrapper import GeoMipTerrainNodeWrapper
from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.modules.pParticleSystemWrapper import ParticleSystemWrapper
from core.modules.pPointLightNodeWrapper import PointLightNodeWrapper
from core.modules.pSpotLightNodeWrapper import SpotLightNodeWrapper
import wx
from math import tan
from gc import collect

# Local imports
from pPropertyGrid import PropertyGrid
from pSceneGraphTree import SceneGraphTree
from pTextureManager import TextureManager
from pViewport import *

from core.modules import *

# Get the default window origin
defWP = WindowProperties.getDefault()
if defWP.hasOrigin():
  origin = defWP.getXOrigin(), defWP.getYOrigin()
else:
  origin = (0, 0)

ID_ENABLE_GRID = 2
ID_SINGLE_VIEWPORT = 3
ID_4x4_GRID = 4
ID_2_HORIZONTAL = 5
ID_2_VERTICAL = 6
ID_NODEPATH = 7
ID_MODEL = 8
ID_TERRAIN = 9
ID_AMBIENT = 10
ID_DIRECTIONAL = 11
ID_POINT = 12
ID_SPOT = 13

class EditorApp(AppShell):
  appversion    = "cvs"
  appname       = "Panda Editor"
  copyright     = "Copyright (c) Carnegie Mellon University.\nAll rights reserved."
  contactname   = "pro-rsoft"
  contactemail  = "niertie1@gmail.com"
  frameWidth    = defWP.getXSize()
  frameHeight   = defWP.getYSize()
  
  def __init__(self, editorInstance):
    """EditorApp constructor."""
    # Instance of the editor
    self.editorInstance = editorInstance
    
    # Create the Wx app
    self.wxApp = wx.App(redirect = False)
    self.wxApp.SetAppName("Panda Editor")
    self.wxApp.SetClassName("PEditor")
    
    self.modified = True
    self.filename = Filename()
    
    # Initialize the app shell and add some controls
    AppShell.__init__(self, title = "Panda Editor", pos = origin)
    self.splitter1 = wx.SplitterWindow(self, style = wx.SP_3D | wx.SP_BORDER)
    self.splitter1.SetMinimumPaneSize(1)
    self.splitter2 = wx.SplitterWindow(self.splitter1, style = wx.SP_3D | wx.SP_BORDER)
    self.splitter2.SetMinimumPaneSize(1)
    self.leftBarSplitter = wx.SplitterWindow(self.splitter2, style = wx.SP_3D | wx.SP_BORDER)
    self.leftBarSplitter.SetMinimumPaneSize(1)
    #self.rightBarSplitter = wx.SplitterWindow(self.splitter1, style = wx.SP_3D | wx.SP_BORDER)
    #self.rightBarSplitter.SetMinimumPaneSize(1)
    self.sceneGraphTree = SceneGraphTree(self.leftBarSplitter)
    self.propertyGrid = PropertyGrid(self.leftBarSplitter)
    self.textureManager = TextureManager(self.splitter1, style = wx.SP_3D | wx.SUNKEN_BORDER)
    self.view = Viewport.makePerspective(self.splitter2)
    sizer = wx.BoxSizer(wx.VERTICAL)
    assert self.leftBarSplitter.SplitHorizontally(self.sceneGraphTree, self.propertyGrid)
    assert self.splitter2.SplitVertically(self.leftBarSplitter, self.view, 200)
    #assert self.rightBarSplitter.SplitHorizontally(self.textureManager, None)
    assert self.splitter1.SplitVertically(self.splitter2, self.textureManager, -200)
    sizer.Add(self.splitter1, 1, wx.EXPAND, 0)
    self.splitter1.Unsplit() # Yes, I know this looks odd.
    self.SetSizer(sizer); self.Layout()
    self.initialize()
    self.splitter2.SetSashPosition(200)
    
    # Setup some events
    base.accept("c", self.onCenterTrackball)
    
    base.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.onModelSelect)
    # If a model-translate-rotate-scale tool is selected the automatic mouse
    # movement has to be disable to prevent camera & object movement.
    # Hmm doesnt really work as well... (camera is still moved)
    base.accept(EVENT_MODELCONTROLLER_EDITTOOL_SELECTED, base.disableMouse)
    base.accept(EVENT_MODELCONTROLLER_EDITTOOL_DESELECTED, base.enableMouse)
    base.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.__setattr__, ["modified", True])
    # The object has been modified in the scene, this event happens every frame
    #base.accept(EVENT_MODELCONTROLLER_FAST_REFRESH, )
    # The editor has been disabled, collisions etc are deleted
    #base.accept(EDITOR_TOGGLE_OFF_EVENT, )
    # The editor has been enabled, collisions etc are created.
    # This event happens shortly after the wxgui has been created
    #base.accept(EDITOR_TOGGLE_ON_EVENT, )
  
  def appInit(self):
    """Overridden from WxAppShell.py."""
    # Create a new event loop (to overide default wxEventLoop)
    self.evtLoop = wx.EventLoop()
    self.oldLoop = wx.EventLoop.GetActive()
    wx.EventLoop.SetActive(self.evtLoop)
    taskMgr.add(self.wxStep, "evtLoopTask")
  
  def createMenuBar(self):
    """Overridden from WxAppShell.py."""
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
    self.menuBar.Check(ID_ENABLE_GRID, True)
    
    # Create menu
    self.menuCreate = wx.Menu()
    self.menuBar.Append(self.menuCreate, "&Create")
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreate.Append(ID_MODEL, "&Model..."))
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreate.Append(ID_TERRAIN, "&Terrain..."))
    
    self.menuCreateLight = wx.Menu()
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreateLight.Append(ID_AMBIENT, "&Ambient"))
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreateLight.Append(ID_DIRECTIONAL, "&Directional"))
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreateLight.Append(ID_POINT, "&Point"))
    self.Bind(wx.EVT_MENU, self.onCreateObject, self.menuCreateLight.Append(ID_SPOT, "&Spotlight"))
    self.menuCreate.AppendSubMenu(self.menuCreateLight, "&Light")
    
    # Viewports menu
    self.menuViewports = wx.Menu()
    self.menuBar.Append(self.menuViewports, "View&ports")
    self.Bind(wx.EVT_MENU, self.onChangeViewports, self.menuViewports.AppendRadioItem(ID_SINGLE_VIEWPORT, "&Single Viewport"))
    self.Bind(wx.EVT_MENU, self.onChangeViewports, self.menuViewports.AppendRadioItem(ID_4x4_GRID, "4x4 &Grid"))
    self.Bind(wx.EVT_MENU, self.onChangeViewports, self.menuViewports.AppendRadioItem(ID_2_HORIZONTAL, "2 &Horizontal"))
    self.Bind(wx.EVT_MENU, self.onChangeViewports, self.menuViewports.AppendRadioItem(ID_2_VERTICAL, "2 &Vertical"))
    self.menuBar.Check(ID_SINGLE_VIEWPORT, True)
    self.menuViewports.AppendSeparator()
    self.viewportMenus = []
  
  def createInterface(self):
    """Overridden from WxAppShell.py."""
    self.CreateStatusBar()
    self.SetStatusText("Welcome to the Panda3D Editor")
    self.Update()
  
  def initialize(self):
    """Initializes the viewports and editor."""
    self.Update()
    ViewportManager.updateAll()
    self.wxStep()
    ViewportManager.initializeAll()
    self.reloadViewportMenus()
    self.editorInstance.toggle("WorldEditMode")
    # Position the camera
    if base.trackball != None:
      base.trackball.node().setPos(0, 30, 0)
      base.trackball.node().setHpr(0, 15, 0)
    
    # Load the direct things
    self.grid = DirectGrid(parent = render)
    self.sceneGraphTree.reload()
    if not isinstance(self.view, Viewport):
      self.view.center()
  
  def reloadViewportMenus(self):
    """Reloads the viewport menus."""
    # Add the individual viewport menus
    for m in self.viewportMenus:
      m.Destroy()
    self.viewportMenus = []
    collect()
    #for v in range(len(ViewportManager.viewports)):
    #  self.viewportMenus.append(self.menuViewports.AppendSubMenu(ViewportMenu(ViewportManager.viewports[v]), "Viewport %d" % (v + 1)))
  
  def wxStep(self, task = None):
    """A step in the WX event loop. You can either call this yourself or use as task."""
    while self.evtLoop.Pending():
      self.evtLoop.Dispatch()
    self.wxApp.ProcessIdle()
    if task != None: return task.cont
  
  def onModelSelect(self, model):
    """Invoked when a model is selected. Shows/hides the texture panel."""
    if model == None and self.splitter1.IsSplit():
      self.splitter1.Unsplit()
    elif model != None and not self.splitter1.IsSplit():
      assert self.splitter1.SplitVertically(self.splitter2, self.textureManager, -200)
  
  def onDestroy(self, evt):
    """Invoked when the window is destroyed."""
    wx.EventLoop.SetActive(self.oldLoop)
  
  def onNew(self, evt = None):
    self.filename = Filename()
    self.modified = True
    self.SetTitle("Panda Editor")
    self.editorInstance.destroyAllModels()
  
  def onOpen(self, evt = None):
    filter = "Panda3D Egg Format (*.egg)|*.[eE][gG][gG];*.egg"
    filter += "|Panda3D Compressed Egg Format (*.egg.pz)|*.[eE][gG][gG].[pP][zZ];*.egg.pz"
    filter += "|Panda3D Binary Format (*.bam)|*.[bB][aA][mM];*.bam"
    filter += "|Panda3D Compressed Binary Format (*.bam)|*.[bB][aA][mM].[pP][zZ];*.bam.pz"
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
        # Reset the camera
        if base.trackball != None:
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
      dlg = wx.FileDialog(self, "Save file", "", "", "Panda3D Binary Format (*.bam)|.[bB][aA][mM];*.bam", wx.SAVE | wx.FD_OVERWRITE_PROMPT)
      try:
        if dlg.ShowModal() == wx.ID_OK:
          self.filename = Filename.fromOsSpecific(dlg.GetPath())
          self.SetTitle(self.filename.getBasename() + " - Panda Editor")
          self.modified = False
          self.editorInstance.saveEggModelsFile(self.filename.getFullpath())
      finally:
        dlg.Destroy()
  
  def onSaveAs(self, evt = None):
    dlg = wx.FileDialog(self, "Save file as", "", "", "Panda3D Binary Format (*.bam)|.[bB][aA][mM];*.bam", wx.SAVE | wx.FD_OVERWRITE_PROMPT)
    try:
      if dlg.ShowModal() == wx.ID_OK:
        self.onNew()
        self.filename = Filename.fromOsSpecific(dlg.GetPath())
        self.SetTitle(self.filename.getBasename() + " - Panda Editor")
        self.modified = False
        self.editorInstance.saveEggModelsFile(self.filename.getFullpath())
    finally:
      dlg.Destroy()
  
  def onCreateObject(self, e):
    """Invoked when the user hits one of the buttons in the "Create" menu."""
    
    modelParent = modelController.getSelectedModel() 
    if modelParent == None: modelParent = render
    objectInstance = None
    if e.Id == ID_NODEPATH:
      objectInstance = NodePathWrapper.onCreateInstance(modelParent)
    elif e.Id == ID_MODEL:
      filter = "Panda3D Egg Format (*.egg)|*.[eE][gG][gG];*.egg"
      filter += "|Panda3D Binary Format (*.bam)|*.[bB][aA][mM];*.bam"
      filter += "|MultiGen (*.flt)|*.[fF][lL][tT];*.flt"
      filter += "|Lightwave (*.lwo)|*.[lL][wW][oO];*.lwo"
      filter += "|AutoCAD (*.dxf)|*.[dD][xX][fF];*.dxf"
      filter += "|VRML (*.wrl)|*.[wW][rR][lL];*.wrl"
      filter += "|DirectX (*.x)|*.[xX];*.x"
      filter += "|COLLADA (*.dae)|*.[dD][aA][eE];*.dae"
      dlg = wx.FileDialog(self, "Select model", "", "", filter, wx.OPEN)
      try:
        if dlg.ShowModal() == wx.ID_OK:
          objectInstance = NodePathWrapper.onCreateInstance(modelParent, Filename.fromOsSpecific(dlg.GetPath()).getFullpath())
      finally:
        dlg.Destroy()
    elif e.Id == ID_TERRAIN:
      filter = "Portable Network Graphics (*.png)|*.[pP][nN][gG];*.png"
      dlg = wx.FileDialog(self, "Select heightfield", "", "", filter, wx.OPEN)
      try:
        if dlg.ShowModal() == wx.ID_OK:
          objectInstance = GeoMipTerrainNodeWrapper.onCreateInstance(modelParent, Filename.fromOsSpecific(dlg.GetPath()).getFullpath())
      finally:
        dlg.Destroy()
    elif e.Id == ID_AMBIENT:
      objectInstance = AmbientLightNodeWrapper.onCreateInstance(modelParent)
    elif e.Id == ID_DIRECTIONAL:
      objectInstance = DirectionalLightNodeWrapper.onCreateInstance(modelParent)
    elif e.Id == ID_POINT:
      objectInstance = PointLightNodeWrapper.onCreateInstance(modelParent)
    elif e.Id == ID_SPOT:
      objectInstance = SpotLightNodeWrapper.onCreateInstance(modelParent)
    
    if objectInstance != None:
      objectInstance.reparentTo(modelParent)
      objectInstance.enableEditmode() 
      modelController.selectModel(objectInstance)
      messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def onChangeViewports(self, e):
    """Invoked when the user changes viewport layout."""
    self.Update()
    sashpos = self.splitter2.GetSashPosition()
    if e.Id == ID_SINGLE_VIEWPORT:
      if isinstance(self.view, Viewport): return
      self.view.close()
      self.view = Viewport.makePerspective(self.splitter2)
    elif e.Id == ID_4x4_GRID:
      if isinstance(self.view, ViewportGrid): return
      self.view.close()
      self.view = ViewportGrid(self.splitter2, [[Viewport.VPTOP,  Viewport.VPFRONT],
                                               [Viewport.VPLEFT, Viewport.VPPERSPECTIVE]])
      self.view.center()
    else:
      if e.Id == ID_2_HORIZONTAL: orientation = wx.SPLIT_HORIZONTAL
      elif e.Id == ID_2_VERTICAL: orientation = wx.SPLIT_VERTICAL
      else: return
      if isinstance(self.view, ViewportSplitter) and not isinstance(self.view, ViewportGrid):
        if self.view.GetSplitMode() == orientation: return
        self.view.close()
        self.view.split(Viewport.VPTOP, Viewport.VPPERSPECTIVE, orientation)
      else:
        self.view.close()
        self.view = ViewportSplitter(self.splitter2, Viewport.VPTOP, Viewport.VPPERSPECTIVE, orientation)
    self.splitter2.Unsplit()
    assert self.splitter2.SplitVertically(self.leftBarSplitter, self.view, sashpos)
    # Reload the menus
    collect()
    self.reloadViewportMenus()
    # Make sure the viewports are initialized correctly
    self.Update()
    ViewportManager.updateAll()
    self.wxStep()
    ViewportManager.initializeAll()
  
  def onToggleGrid(self, evt = None):
    """Toggles the grid on/off."""
    if evt.GetEventObject().IsChecked(ID_ENABLE_GRID):
      self.grid.enable()
    else:
      self.grid.disable()
  
  def onCenterTrackball(self, evt = None):
    """Center the trackball, like 'c' does in pview."""
    gbv = render.getBounds();
    # Determine the bounding sphere around the object.
    if gbv.isInfinite(): return
    if gbv.isEmpty(): return
    
    # The BoundingVolume might be a sphere (it's likely), but since it
    # might not, we'll take no chances and make our own sphere.
    sphere = BoundingSphere(gbv.getApproxCenter(), 0.0)
    if (not sphere.extendBy(gbv)): return
    
    radius = 50.0
    
    # Loop through the windows/viewports
    for w in WindowManager.windows:
      # Choose a suitable distance to view the whole volume in our frame.
      # This is based on the camera lens in use.
      fov = w.camLens.getFov();
      distance = radius / tan(deg2Rad(min(fov[0], fov[1]) / 2.0));
      
      # Ensure the far plane is far enough back to see the entire object.
      idealFarPlane = distance + radius * 1.5;
      w.camLens.setFar(max(w.camLens.getDefaultFar(), idealFarPlane));
      
      # And that the near plane is far enough forward.
      w.camLens.setNear(min(w.camLens.getDefaultNear(), radius - sphere.getRadius()))
      
      w.trackball.node().setOrigin(sphere.getCenter())
      w.trackball.node().setPos(Vec3.forward() * distance)
      
      # Also set the movement scale on the trackball to be consistent
      # with the size of the model and the lens field-of-view.
      w.trackball.node().setForwardScale(distance * 0.006)
