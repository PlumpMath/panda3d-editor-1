__all__ = ["MouseHandlerClass"]
import sys

from pandac.PandaModules import WindowProperties, Vec3

MOUSE_REFRESH_RATE = 1./60.

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
  
  def toggle(self, state = None):
    if state is None:
      state = not self.enabled
    
    if state:
      taskMgr.remove('mouseHandlerTask')
      taskMgr.add(self.mouseHandlerTask, 'mouseHandlerTask')
    else:
      taskMgr.remove('mouseHandlerTask')
    
    self.enabled = state
  
  def toggleMouseFixed(self, state = None):
    """Set the mouse fixed"""
    if state == None:
      state = not self.mouseFixed
    self.mouseFixed = state
    if self.mouseFixed:
      self.prevMousePos = self.mousePosX, self.mousePosY
      self.discardFrame = True
    else:
      self.setMousePos(*self.prevMousePos)
    self.setMouseHidden(self.mouseFixed)
  
  def mouseHandlerTask(self, task):
    self.taskTimer += globalClock.getDt()
    # only allow the reset happening every MOUSE_REFRESH_RATE seconds
    if self.taskTimer > MOUSE_REFRESH_RATE:
      # if discardframe is defined, dont return the real mouse movement
      # instead return 0/0 and set the mouse centered
      # (this is used when a relative movement is needed, but the mouse
      # is not centered on the screen in the first frame)
      if self.discardFrame:
        self.mousePosX, self.mousePosY = 0,0
        self.discardFrame = False
        self.setMouseCentered()
        return task.again
      
      self.taskTimer -= MOUSE_REFRESH_RATE
      
      # read the mouse position
      if base.mouseWatcherNode != None and base.mouseWatcherNode.hasMouse():
        mpos = base.mouseWatcherNode.getMouse()
        self.mousePosX, self.mousePosY = mpos.getX(), mpos.getY()
        
        # if the mouse is fixed to the center of the window, reset the mousepos
        if self.mouseFixed:
          self.setMouseCentered()
    
    return task.again
  
  def setMouseCentered(self):
    """Set the mouse position into the center of the window"""
    px, py = 0,0
    self.setMousePos(px, py)
  
  def setMousePos(self, px, py):
    """Set the mouse position on the screen with a position x(-1,1) and y(-1,1)"""
    base.win.movePointer(0,  px * base.win.getXSize() / 2 + base.win.getXSize() / 2
                          , -py * base.win.getYSize() / 2 + base.win.getYSize() / 2)
  
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
    base.win.requestProperties(wp)
  
  def getMousePos(self):
    return self.mousePosX, self.mousePosY

mouseHandler = MouseHandlerClass()

