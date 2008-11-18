from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from pandac.PandaModules import WindowProperties, Vec3
import sys, time


from core.pConfigDefs import *
from core.pMouseHandler import *

MOUSE_ROTATION_SPEED = 25.0
MOUSE_MOVEMENT_SPEED = 25.0
# camera distance parameters
MOUSE_ZOOM_SPEED = 10.0
STARTUP_CAMERA_DISTANCE = 100
STARTUP_CAMERA_HPR = Vec3( 30,-30,0 )
MIN_CAMERA_DISTANCE = 10
MAX_CAMERA_DISTANCE = 1000


class CameraController( DirectObject, FSM ):
  def __init__( self ):
    FSM.__init__(self,'mouseControllerClass')
    
    self.cameraPosPivot = render.attachNewNode( 'cameraPivot' )
    self.cameraPosPivot.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
    self.cameraRotPivot = self.cameraPosPivot.attachNewNode( 'cameraPivot' )
    self.cameraRotPivot.setHpr( STARTUP_CAMERA_HPR )
    # show a point at the cameraPosPivot
    self.posPivotModel = loader.loadModel( CAMERACONTROLLER_PIVOT_MODEL )
    self.posPivotModel.reparentTo( self.cameraPosPivot )
    self.posPivotModel.setScale( 0.1 )
    self.posPivotModel.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
    
    self.request( 'Disabled' )
  
  def enable( self ):
    self.request( 'Default' )
  def disable( self ):
    self.request( 'Disabled' )
  
  def enterDisabled( self ):
    base.camera.reparentTo( render )
    self.posPivotModel.hide()
  def exitDisabled( self ):
    base.camera.reparentTo( self.cameraRotPivot )
    base.camera.setY( -STARTUP_CAMERA_DISTANCE )
    self.posPivotModel.show()
    
  
  # --- Default start ---
  def enterDefault( self ):
    #print "enterDefault"
    #self.accept( 'mouse1', self.request, ['MouseButton1Pressed'] )
    self.accept( 'mouse2', self.request, ['MouseButton2Pressed'] )
    self.accept( 'mouse3', self.request, ['MouseButton3Pressed'] )
    self.accept( 'wheel_down', self.zoomOut )
    self.accept( 'wheel_up', self.zoomIn )
    self.accept( 'page_down', self.zoomOut )
    self.accept( 'page_up', self.zoomIn )
    #messenger.toggleVerbose()
  
  def exitDefault( self ):
    #print "exitDefault"
    self.ignoreAll()
  # --- Default end ---
  
  # --- helper function begin ---
  def zoomOut( self ):
    base.camera.setY( min( -MIN_CAMERA_DISTANCE
                    , max( -MAX_CAMERA_DISTANCE
                    , base.camera.getY() -1 * MOUSE_ZOOM_SPEED ) ) )
    #print "zoomOut", base.camera.getY()
  
  def zoomIn( self ):
    base.camera.setY( min( -MIN_CAMERA_DISTANCE
                    , max( -MAX_CAMERA_DISTANCE
                    , base.camera.getY() + 1 * MOUSE_ZOOM_SPEED ) ) )
    #print "zoomIn", base.camera.getY()
  
  def getCreatePos( self ):
    return self.cameraPosPivot.getPos( render )
  
  #def move_pivot_relative( self, moveX, moveY ):
  #  multiplier = 1
  # --- helper function end ---
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton1Pressed( self ):
    #print "enterMouseButton1Pressed"
    self.ignoreAll()
    
    # add the task and the abort funtion
    self.taskMouseButton1PressedRunning = True
    taskMgr.add( self.taskMouseButton1Pressed, 'taskMouseButton1Pressed' )
    self.accept( 'mouse1-up', self.request, ['Default'] )
    # center the mouse to prevent a huge jump in the beginng
    #*()
    #mouseHandler.toggleMouseFixed()
    mouseHandler.toggleMouseFixed( True )
  
  def taskMouseButton1Pressed( self, task ):
    # this is needed because the task might be called once more after the exit
    # function has been called
    # also skip first frame
    mx,my = mouseHandler.getMousePos()
    if self.taskMouseButton1PressedRunning and task.frame:
      #print mx,my
      pass
      #base.camera.setPos( base.camera, -Vec3(mx,0,my) * MOUSE_MOVEMENT_SPEED )
      print self.cameraPosPivot.getPos(render)
      #self.cameraPosPivot.setPos( self.cameraPosPivot, Vec3(mx,my,0) * MOUSE_MOVEMENT_SPEED )
      #self.move_pivot_relative( mx*MOUSE_MOVEMENT_SPEED, my*MOUSE_MOVEMENT_SPEED )
    return task.cont
  
  def exitMouseButton1Pressed( self ):
    #print "exitMouseButton1Pressed"
    taskMgr.remove( 'taskMouseButton1Pressed' )
    self.taskMouseButton1PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---
  
  
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
      #print "step", task.time, globalClock.getDt()
      #time.sleep( 0.001 )
      curHpr = self.cameraRotPivot.getHpr()
      newHpr = curHpr + Vec3(mx,-my,0) * MOUSE_ROTATION_SPEED #* globalClock.getDt()
      newHpr.setY( min( 90, max( -90, newHpr.getY() ) ) )
      self.cameraRotPivot.setHpr( newHpr )
      #print "camera hpr", self.cameraRotPivot.getHpr( render )
    return task.cont
  
  def exitMouseButton2Pressed( self ):
    #print "exitMouseButton2Pressed"
    taskMgr.remove( 'taskMouseButton2Pressed' )
    self.taskMouseButton2PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---
  
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton3Pressed( self ):
    #print "enterMouseButton1Pressed"
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
      #print mx,my$
      pass
      #base.camera.setPos( base.camera, -Vec3(0,my,0) * MOUSE_MOVEMENT_SPEED )
      diffPos = camera.getPos( render ) - self.cameraPosPivot.getPos( render )
      diffPos.normalize()
      self.cameraPosPivot.setX( self.cameraPosPivot.getX() \
                              - mx * diffPos.getY() * MOUSE_MOVEMENT_SPEED
                              - my * diffPos.getX() * MOUSE_MOVEMENT_SPEED )
      self.cameraPosPivot.setY( self.cameraPosPivot.getY() \
                              - my * diffPos.getY() * MOUSE_MOVEMENT_SPEED
                              + mx * diffPos.getX() * MOUSE_MOVEMENT_SPEED )
#      print "camera pivot", self.cameraPosPivot.getPos(render)
    return task.cont
  
  def exitMouseButton3Pressed( self ):
    #print "exitMouseButton3Pressed"
    taskMgr.remove( 'taskMouseButton3Pressed' )
    self.taskMouseButton1PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---

base.disableMouse()
cameraController = CameraController()