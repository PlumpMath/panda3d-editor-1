__all__ = ["MouseHandlerClass"]
import sys

from pandac.PandaModules import WindowProperties, Vec3

from core.pWindow import WindowManager

MOUSE_REFRESH_RATE = 1./30.

class MouseHandlerClass:
  def __init__(self):
    # last read of the mouse at frame
    self.lastRead = -1
    self.mousePosX = 0
    self.mousePosY = 0
    self.mouseFixed = False
    self.discardFrame = False
    self.prevMousePos = 0, 0
    self.taskTimer = 0
    self.enabled = False
  
  '''def toggle(self, state = None):
    if state is None:
      state = not self.enabled
    
    if state:
      taskMgr.remove('mouseHandlerTask')
      taskMgr.add(self.mouseHandlerTask, 'mouseHandlerTask')
    else:
      taskMgr.remove('mouseHandlerTask')
    
    self.enabled = state'''
  
  '''def toggle(self, state = None):
    if state is None:
      state = not self.enabled
    
    if state:
    else:
    
    self.enabled = state'''
  
  def toggleMouseFixed(self, state = None):
    """Set the mouse fixed"""
    if state == None:
      state = not self.mouseFixed
    self.mouseFixed = state
    if self.mouseFixed:
      self.prevMousePos = self._getCurrentMousePos()
      #self.discardFrame = True
      taskMgr.remove('mouseHandlerTask')
      #taskMgr.doMethodLater(MOUSE_REFRESH_RATE, self.mouseHandlerTask, 'mouseHandlerTask')
      taskMgr.add(self.mouseHandlerTask, 'mouseHandlerTask')
    else:
      self.setMousePos(*self.prevMousePos)
      taskMgr.remove('mouseHandlerTask')
    self.setMouseHidden(self.mouseFixed)
  
  def mouseHandlerTask(self, task):
    # dont return the real mouse movement offset in the first frame
    if not task.frame:
      print "skip", task.frame
      self.mousePosX, self.mousePosY = 0,0
      self.setMouseCentered()
      self.lastTaskTime = globalClock.getFrameTime()
      return task.cont
    
    curTime = globalClock.getFrameTime()
    if (curTime - MOUSE_REFRESH_RATE > self.lastTaskTime):
      self.lastTaskTime = curTime
      # cache the mouse position
      self.mousePosX, self.mousePosY = self._getCurrentMousePos()
      
      # if the mouse is fixed to the center of the window, reset the mousepos
      if self.mouseFixed:
        self.setMouseCentered()
    
    return task.cont
  
  def _getCurrentMousePos(self):
    if WindowManager.hasMouse():
      mpos = WindowManager.getMouse()
      if mpos != None:
        return mpos.getX(), mpos.getY()
    return 0,0
  
  def setMouseCentered(self):
    """Set the mouse position into the center of the window"""
    self.setMousePos(0, 0)
  
  def setMousePos(self, px, py):
    """Set the mouse position on the screen with a position x(-1,1) and y(-1,1)"""
    if WindowManager.activeWindow == None: return
    px, py = float(px), float(py)
    win = WindowManager.activeWindow.win
    win.movePointer(0, int( px * win.getXSize() / 2 + win.getXSize() / 2)
                     , int(-py * win.getYSize() / 2 + win.getYSize() / 2) )
  
  def setMouseHidden(self, state = None):
    """Hides/Shows the mouse"""
    wp = WindowProperties()
    # If state is not defined, toggle the current state
    if state == None:
      state = wp.getCursorHidden()
    # Hide/show mouse cursor
    wp.setCursorHidden(state)
    
    # Does not exist panda 1.3.2 / but is required for osx-mouse movement
    if sys.platform == 'darwin':
      wp.setMouseMode(WindowProperties.MRelative)
    else:
      wp.setMouseMode(WindowProperties.MAbsolute)
    
    for w in WindowManager.windows:
      w.win.requestProperties(wp)
  
  def getMousePos(self):
    if self.mouseFixed:
      # return cached mouse position
      return self.mousePosX, self.mousePosY
    # read current mouse position
    return self._getCurrentMousePos()

mouseHandler = MouseHandlerClass()

