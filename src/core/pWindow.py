__all__ = ["Window"]

from pandac.PandaModules import WindowProperties, loadPrcFileData, Trackball, DriveInterface
from pandac.PandaModules import MouseAndKeyboard, MouseWatcher, KeyboardButton, ButtonThrower
from pandac.PandaModules import GraphicsStateGuardian, Transform2SG, ModifierButtons
from pandac.PandaModules import FrameBufferProperties, GraphicsPipe, Texture
from direct.showbase.ShowBase import ShowBase

from core.pConfigDefs import EVENT_WINDOW_FOCUS_CHANGE

class WindowManager:
  """Manages the windows in the editor."""
  allowMultipleWindows = False
  windows = [] # Don't add windows to this list yourself!
  activeWindow = None
  gsg = None
  
  @staticmethod
  def startBase(showDefaultWindow = True, allowMultipleWindows = False):
    """Starts up Panda3D by loading the ShowBase modules."""
    WindowManager.allowMultipleWindows = allowMultipleWindows
    assert not (allowMultipleWindows and showDefaultWindow)
    # Load up showbase. If we want a default window, make sure one gets opened.
    nbase = ShowBase()
    nbase.windowType = "onscreen"
    if showDefaultWindow:
      activeWindow = Window()
    nbase.taskMgr.add(WindowManager.checkActiveWindow, "checkActiveWindow")
    return nbase
  
  @staticmethod
  def getDefaultCamera():
    """Returns the default camera. If there are multiple, returns the one with the mouse focus."""
    if len(WindowManager.windows) == 0: return None
    if len(WindowManager.windows) == 1: return WindowManager.windows[0].camera
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.camera
  
  @staticmethod
  def getDefaultGraphicsWindow():
    """Returns the default graphics window. If there are multiple, returns the one with the mouse focus."""
    if len(WindowManager.windows) == 0: return None
    if len(WindowManager.windows) == 1: return WindowManager.windows[0].win
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.win
    return None
  
  @staticmethod
  def hasMouse():
    """Returns whether any of the windows has mouse."""
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return True
    return False

  @staticmethod
  def getMouse():
    """Returns the coordinates of the window which has currently the mouse."""
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.mouseWatcherNode.getMouse()
    return None
  
  @staticmethod
  def getMouseX():
    """Returns the X coordinate of the window which has currently the mouse."""
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.mouseWatcherNode.getMouseX()
    return None
  
  @staticmethod
  def getMouseY():
    """Returns the X coordinate of the window which has currently the mouse."""
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.mouseWatcherNode.getMouseY()
    return None
  
  @staticmethod
  def getMouseWatcherNode():
    """Returns the mouse watcher node of the window which currently has the mouse."""
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        return w.mouseWatcherNode
    return None
  
  @staticmethod
  def checkActiveWindow(task = None):
    """Internal task that checks which of the windows is currently active."""
    activeWindow = None
    for w in WindowManager.windows:
      if w.mouseWatcherNode.hasMouse():
        activeWindow = w
    if activeWindow != WindowManager.activeWindow:
      WindowManager.activeWindow = activeWindow
      messenger.send(EVENT_WINDOW_FOCUS_CHANGE)
    if task != None:
      return task.cont
    else:
      return activeWindow

  @staticmethod
  def makeTextureBuffer(name, xSize, ySize, tex = None, toRam = False, fbp = None):
    """Copied from graphicsOutput.cxx and pythonified."""
    if fbp == None:
      fbp = FrameBufferProperties()
      fbp.setRgbColor(1)
      fbp.setDepthBits(1)
    
    flags = GraphicsPipe.BFRefuseWindow;
    if Texture.getTexturesPower2() != Texture.ATSNone:
      flags |= GraphicsPipe.BFSizePower2
    if tex != None and tex.getTextureType() == Texture.TTCubeMap:
      flags |= GraphicsPipe.BFSizeSquare
    
    buffer = gsg.getEngine().makeOutput(gsg.getPipe(), name, 0, fbp, WindowProperties.size(xSize, ySize), flags, gsg)
    
    if buffer != None:
      if toRam:
        buffer.addRenderTexture(tex, RTMCopyRam);
      else:
        buffer.addRenderTexture(tex, RTMBindOrCopy);
      return buffer
    
    return None

class Window(object):
  """Class representing a graphics window."""
  def __init__(self, extraProps = None):
    base.windowType = "onscreen"
    props = WindowProperties.getDefault()
    if extraProps != None:
      props.addProperties(extraProps)
    if not WindowManager.allowMultipleWindows:
      base.openDefaultWindow(props = props, gsg = WindowManager.gsg)
      self.win = base.win
      assert len(WindowManager.windows) == 0
    else:
      self.win = base.openWindow(props = props, gsg = WindowManager.gsg)
    if WindowManager.gsg == None:
      WindowManager.gsg = self.win.getGsg()
    self.camera = base.camList[-1]
    self.camNode = self.camera.node()
    self.camLens = self.camNode.getLens()
    self.buttonThrowers = None
    self.setupMouse(self.win)
    WindowManager.windows.append(self)
  
  def close(self):
    """Closes the window."""
    base.closeWindow(self.win)
    WindowManager.windows.remove(self)
  
  # Viciously stolen from ShowBase.py
  def setupMouse(self, win):
    """
    Creates the structures necessary to monitor the mouse input,
    using the indicated window.  If the mouse has already been set
    up for a different window, those structures are deleted first.
    """
    if self.buttonThrowers != None:
      for bt in self.buttonThrowers:
        mw = bt.getParent()
        mk = mw.getParent()
        bt.removeNode()
        mw.removeNode()
        mk.removeNode()
    # For each mouse/keyboard device, we create
    #  - MouseAndKeyboard
    #  - MouseWatcher
    #  - ButtonThrower
    # The ButtonThrowers are stored in a list, self.buttonThrowers.
    # Given a ButtonThrower, one can access the MouseWatcher and
    # MouseAndKeyboard using getParent.
    #
    # The MouseAndKeyboard generates mouse events and mouse
    # button/keyboard events; the MouseWatcher passes them through
    # unchanged when the mouse is not over a 2-d button, and passes
    # nothing through when the mouse *is* over a 2-d button.  Therefore,
    # objects that don't want to get events when the mouse is over a
    # button, like the driveInterface, should be parented to
    # MouseWatcher, while objects that want events in all cases, like the
    # chat interface, should be parented to the MouseAndKeyboard.
    
    self.buttonThrowers = []
    self.pointerWatcherNodes = []
    for i in range(win.getNumInputDevices()):
      name = win.getInputDeviceName(i)
      mk = base.dataRoot.attachNewNode(MouseAndKeyboard(win, i, name))
      mw = mk.attachNewNode(MouseWatcher("watcher%s" % (i)))
      mb = mw.node().getModifierButtons()
      mb.addButton(KeyboardButton.shift())
      mb.addButton(KeyboardButton.control())
      mb.addButton(KeyboardButton.alt())
      mb.addButton(KeyboardButton.meta())
      mw.node().setModifierButtons(mb)
      bt = mw.attachNewNode(ButtonThrower("buttons%s" % (i)))
      if (i != 0):
        bt.node().setPrefix('mousedev%s-' % (i))
      mods = ModifierButtons()
      mods.addButton(KeyboardButton.shift())
      mods.addButton(KeyboardButton.control())
      mods.addButton(KeyboardButton.alt())
      mods.addButton(KeyboardButton.meta())
      bt.node().setModifierButtons(mods)
      self.buttonThrowers.append(bt)
      if (win.hasPointer(i)):
        self.pointerWatcherNodes.append(mw.node())
    
    self.mouseWatcher = self.buttonThrowers[0].getParent()
    self.mouseWatcherNode = self.mouseWatcher.node()
    # print "ButtonThrowers = ", self.buttonThrowers
    # print "PointerWatcherNodes = ", self.pointerWatcherNodes
    
    # Now we have the main trackball & drive interfaces.
    # useTrackball() and useDrive() switch these in and out; only
    # one is in use at a given time.
    self.trackball = base.dataUnused.attachNewNode(Trackball('trackball'))
    self.drive = base.dataUnused.attachNewNode(DriveInterface('drive'))
    self.mouse2cam = base.dataUnused.attachNewNode(Transform2SG('mouse2cam'))
    self.mouse2cam.node().setNode(self.camera.node())
    
    # A special ButtonThrower to generate keyboard events and
    # include the time from the OS.  This is separate only to
    # support legacy code that did not expect a time parameter; it
    # will eventually be folded into the normal ButtonThrower,
    # above.
    mw = self.buttonThrowers[0].getParent()
    self.timeButtonThrower = mw.attachNewNode(ButtonThrower('timeButtons'))
    self.timeButtonThrower.node().setPrefix('time-')
    self.timeButtonThrower.node().setTimeFlag(1)
    
    #FIXME: we might need DGUI once for our non-default windows
    # Tell the gui system about our new mouse watcher.
    #self.aspect2d.node().setMouseWatcher(mw.node())
    #self.aspect2dp.node().setMouseWatcher(mw.node())
    #mw.node().addRegion(PGMouseWatcherBackground())

