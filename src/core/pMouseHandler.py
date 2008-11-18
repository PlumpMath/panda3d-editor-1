#!/usr/bin/env python
import sys

from pandac.PandaModules import WindowProperties, Vec3

class MouseHandlerClass:
  def __init__( self ):
    # last read of the mouse at frame
    self.lastRead = -1
    self.mousePosX = 0
    self.mousePosY = 0
    self.mouseFixed = False
    self.discardFrame = False
    self.prevMousePos = 0, 0
    self.taskTimer = 0
    taskMgr.add( self.mouseHandlerTask, 'mouseHandlerTask' )
  
  def toggleMouseFixed( self, state=None ):
    if state == None:
      state = not self.mouseFixed
    self.mouseFixed = state
    if self.mouseFixed:
      self.prevMousePos = self.mousePosX, self.mousePosY
      self.discardFrame = True
    else:
      self.setMousePos( *self.prevMousePos )
    self.setMouseHidden( self.mouseFixed )
  
  def mouseHandlerTask( self, task ):
    if self.discardFrame:
      self.mousePosX, self.mousePosY = 0,0
      self.discardFrame = False
      self.setMouseCentered()
      return task.again
    
    self.taskTimer += globalClock.getDt()
    
    # only allow the reset happening every 1/60 second
    if self.taskTimer > 1./60.:
      self.taskTimer -= 1./60.
      
      if base.mouseWatcherNode.hasMouse():
        mpos = base.mouseWatcherNode.getMouse()
        self.mousePosX, self.mousePosY = mpos.getX(), mpos.getY()
        if self.mouseFixed:
          self.setMouseCentered()
    
    return task.again
  
  def setMouseCentered( self ): #, position=None ):
    px, py = 0,0 #base.win.getXSize()/2, base.win.getYSize()/2
    self.setMousePos( px, py )
  
  def setMousePos( self, px, py ):
    base.win.movePointer(0,  px * base.win.getXSize()/2 + base.win.getXSize()/2
                          , -py * base.win.getYSize()/2 + base.win.getYSize()/2)
  
  def setMouseHidden( self, state=None ):
    wp = WindowProperties()
    # if state is not defined, toggle the current state
    if state == None:
      state = wp.getCursorHidden()
    # hide/show mouse cursor
    wp.setCursorHidden( state )
    
    # does not exist panda 1.3.2 / but is reqired for osx-mouse movement
    if sys.platform == 'darwin':
      wp.setMouseMode(WindowProperties.MRelative)
    else:
      wp.setMouseMode(WindowProperties.MAbsolute)
    base.win.requestProperties(wp)
  
  def getMousePos( self ):
    return self.mousePosX, self.mousePosY
  def getMouseMovement( self ):
    return self.mousePosX, self.mousePosY

mouseHandler = MouseHandlerClass()