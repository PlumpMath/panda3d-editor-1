from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from pandac.PandaModules import WindowProperties, Vec3
import sys, time

from core.pConfigDefs import *
from core.pMouseHandler import mouseHandler
from core.pWindow import WindowManager

# Note: globals moved to pConfigDefs

class CameraController( DirectObject, FSM ):
  def __init__(self):
    FSM.__init__(self,'mouseControllerClass')
    
    self.cameraPosPivot = render.attachNewNode( 'cameraPivot' )
    self.cameraRotPivot = self.cameraPosPivot.attachNewNode( 'cameraPivot' )
    self.cameraRotPivot.setHpr( STARTUP_CAMERA_HPR )
    # show a point at the cameraPosPivot
    self.posPivotModel = loader.loadModel( CAMERACONTROLLER_PIVOT_MODEL )
    self.posPivotModel.reparentTo( self.cameraPosPivot )
    self.posPivotModel.setScale( 0.1 )
    
    self.request( 'Disabled' )
  
  def enable( self ):
    self.request( 'Default' )
  def disable( self ):
    self.request( 'Disabled' )
  
  def enterDisabled( self ):
    try:
      WindowManager.getDefaultCamera().reparentTo( render )
    except:
      pass
    self.posPivotModel.hide()
  def exitDisabled( self ):
    WindowManager.getDefaultCamera().reparentTo( self.cameraRotPivot )
    WindowManager.getDefaultCamera().setY( -STARTUP_CAMERA_DISTANCE )
    self.posPivotModel.show()
    
  
  # --- Default start ---
  def enterDefault( self ):
    #self.accept( 'mouse1', self.request, ['MouseButton1Pressed'] )
    self.accept( 'mouse2', self.request, ['MouseButton2Pressed'] )
    self.accept( 'mouse3', self.request, ['MouseButton3Pressed'] )
    self.accept( 'wheel_down', self.zoomOut )
    self.accept( 'wheel_up', self.zoomIn )
    self.accept( 'page_down', self.zoomOut )
    self.accept( 'page_up', self.zoomIn )
  
  def exitDefault( self ):
    self.ignoreAll()
  # --- Default end ---
  
  # --- helper function begin ---
  def zoomOut( self ):
    cam = WindowManager.getDefaultCamera()
    cam.setY( min( -MIN_CAMERA_DISTANCE
            , max( -MAX_CAMERA_DISTANCE
            , cam.getY() -1 * MOUSE_ZOOM_SPEED ) ) )
  
  def zoomIn( self ):
    cam = WindowManager.getDefaultCamera()
    cam.setY( min( -MIN_CAMERA_DISTANCE
            , max( -MAX_CAMERA_DISTANCE
            , cam.getY() + 1 * MOUSE_ZOOM_SPEED ) ) )
  
  def getCreatePos( self ):
    return self.cameraPosPivot.getPos( render )
  # --- helper function end ---
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton2Pressed( self ):
    #print "enterMouseButton1Pressed"
    self.ignoreAll()
    
    # add the task and the abort funtion
    self.taskMouseButton2PressedRunning = True
    taskMgr.add( self.taskMouseButton2Pressed, 'taskMouseButton2Pressed' )
    self.accept( 'mouse2-up', self.request, ['Default'] )
    # center the mouse to prevent a huge jump in the beginng
    mouseHandler.toggleMouseFixed( True )
  
  def taskMouseButton2Pressed( self, task ):
    # this is needed because the task might be called once more after the exit
    # function has been called
    # also skip first frame
    mx,my = mouseHandler.getMousePos()
    if self.taskMouseButton2PressedRunning and task.frame:
      curHpr = self.cameraRotPivot.getHpr()
      newHpr = curHpr + Vec3(mx,-my,0) * MOUSE_ROTATION_SPEED #* globalClock.getDt()
      newHpr.setY( min( 90, max( -90, newHpr.getY() ) ) )
      self.cameraRotPivot.setHpr( newHpr )
    return task.cont
  
  def exitMouseButton2Pressed( self ):
    taskMgr.remove( 'taskMouseButton2Pressed' )
    self.taskMouseButton2PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---
  
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton3Pressed( self ):
    self.ignoreAll()
    
    # add the task and the abort funtion
    self.taskMouseButton3PressedRunning = True
    taskMgr.add( self.taskMouseButton3Pressed, 'taskMouseButton3Pressed' )
    self.accept( 'mouse3-up', self.request, ['Default'] )
    # center the mouse to prevent a huge jump in the beginng
    mouseHandler.toggleMouseFixed( True )
  
  def taskMouseButton3Pressed( self, task ):
    # this is needed because the task might be called once more after the exit
    # function has been called
    # also skip first frame
    mx,my = mouseHandler.getMousePos()
    if self.taskMouseButton3PressedRunning and task.frame:
      diffPos = WindowManager.getDefaultCamera().getPos( render ) - self.cameraPosPivot.getPos( render )
      diffPos.normalize()
      self.cameraPosPivot.setX( self.cameraPosPivot.getX() \
                              - mx * diffPos.getY() * MOUSE_MOVEMENT_SPEED
                              - my * diffPos.getX() * MOUSE_MOVEMENT_SPEED )
      self.cameraPosPivot.setY( self.cameraPosPivot.getY() \
                              - my * diffPos.getY() * MOUSE_MOVEMENT_SPEED
                              + mx * diffPos.getX() * MOUSE_MOVEMENT_SPEED )
    return task.cont
  
  def exitMouseButton3Pressed( self ):
    taskMgr.remove( 'taskMouseButton3Pressed' )
    self.taskMouseButton1PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---

base.disableMouse()
cameraController = CameraController()
