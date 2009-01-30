from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from pandac.PandaModules import WindowProperties, Vec3
import sys, time

from core.pConfigDefs import *
from core.pMouseHandler import mouseHandler
from core.pWindow import WindowManager

# Note: globals moved to pConfigDefs

class CameraController(DirectObject, FSM):
  def __init__(self):
    FSM.__init__(self,'mouseControllerClass')
    
    self.cameraPosPivot = render.attachNewNode( 'cameraPivot' )
    self.cameraRotPivot = self.cameraPosPivot.attachNewNode( 'cameraPivot' )
    self.cameraRotPivot.setHpr( STARTUP_CAMERA_HPR )
    # show a point at the cameraPosPivot
    self.posPivotModel = loader.loadModel( CAMERACONTROLLER_PIVOT_MODEL )
    self.posPivotModel.reparentTo( self.cameraPosPivot )
    self.posPivotModel.setScale( 0.1 )
    
    self.pressedKeys = dict()
    moveSpeed = 25
    self.moveVec = Vec3(0)
    self.moveActions = {'w': Vec3(0,moveSpeed,0),
                        's': Vec3(0,-moveSpeed,0),
                        'a': Vec3(-moveSpeed,0,0),
                        'd': Vec3(moveSpeed,0,0),
                        'e': Vec3(0,0,moveSpeed),
                        'q': Vec3(0,0,-moveSpeed)}
    taskMgr.add(self.movePivotTask, 'movePivotTask')
    
    self.cameraHprResets = {'shift-1': Vec3(90,0,0),
                            'shift-2': Vec3(180,0,0),
                            'shift-3': Vec3(0,-90,0),
                            'shift-4': Vec3(-90,0,0),
                            'shift-5': Vec3(0,0,0),
                            'shift-6': Vec3(0,90,0),}
    
    self.backupSettings()
    
    self.request('Disabled')
    
    self.accept('shift-0', self.toggleLens)
  
  def __del__(self):
    print "I: CameraController.__del__:"
    print "  - prevMouseEnabled", self.prevMouseEnabled
    print "  - prevCamParent", self.prevCamParent
    base.camera.reparentTo(self.prevCamParent)
    if self.prevMouseEnabled:
      base.enableMouse()
  
  def enable( self ):
    self.request('Default')
  def disable( self ):
    self.request('Disabled')
  
  def backupSettings(self):
    # TODO: BACKUP AND RESTORE THE LENS SETTINGS (NEAR/FAR/FOV)
    # backup settings
    self.prevCamParent = base.camera.getParent()
    self.prevCameraPos = base.camera.getPos()
    if base.mouse2cam.getParent() == base.mouseInterface:
      self.prevMouseEnabled = True
    else:
      self.prevMouseEnabled = False
    base.disableMouse()
  
  def restoreSettings(self):
    # doesnt work
    # base.camera.reparentTo(self.prevCamParent)
    # this works
    base.camera = WindowManager.getDefaultCamera()
    base.camera.reparentTo(self.prevCamParent)
    base.camera.setPos(self.prevCameraPos)
    if self.prevMouseEnabled:
      base.enableMouse()
  
  def enterDisabled( self ):
    # restore settings
    self.restoreSettings()
    self.posPivotModel.hide()
    self.ignoreAll()
  def exitDisabled( self ):
    # backup settings
    self.backupSettings()
    # start control of camera
    WindowManager.getDefaultCamera().reparentTo( self.cameraRotPivot )
    WindowManager.getDefaultCamera().setY( -STARTUP_CAMERA_DISTANCE )
    self.posPivotModel.show()
  
  # --- Default start ---
  def enterDefault( self ):
    #self.accept( 'mouse1', self.request, ['MouseButton1Pressed'] )
    self.accept('mouse2', self.request, ['MouseButton2Pressed'])
    self.accept('mouse3', self.request, ['MouseButton3Pressed'])
    self.accept('wheel_down', self.zoomOut)
    self.accept('wheel_up', self.zoomIn)
    self.accept('page_down', self.zoomOut)
    self.accept('page_up', self.zoomIn)
    # camera movement
    for key, vec in self.moveActions.items():
      self.accept( key, self.movePivot, [key, True] )
      self.accept( key+"-up", self.movePivot, [key, False] )
    # camera rotation reset
    for key, rot in self.cameraHprResets.items():
      self.accept( key, self.setCameraRotation, [rot] )
  
  def exitDefault( self ):
    self.ignore('mouse2')
    self.ignore('mouse3')
    self.ignore('wheel_down')
    self.ignore('wheel_up')
    self.ignore('page_down')
    self.ignore('page_up')
  # --- Default end ---
  
  # --- helper function begin ---
  def zoomOut( self ):
    camera = WindowManager.getDefaultCamera()
    if type(camera.node().getLens()) == PerspectiveLens:
      camera.setY( min( -MIN_CAMERA_DISTANCE
                 , max( -MAX_CAMERA_DISTANCE
                 , camera.getY() -1 * MOUSE_ZOOM_SPEED ) ) )
    elif type(camera.node().getLens()) == OrthographicLens:
      lens = camera.node().getLens()
      filmSize = lens.getFilmSize()
      lens.setFilmSize(filmSize*1.25)
  
  def zoomIn( self ):
    camera = WindowManager.getDefaultCamera()
    if type(camera.node().getLens()) == PerspectiveLens:
      camera.setY( min( -MIN_CAMERA_DISTANCE
              , max( -MAX_CAMERA_DISTANCE
              , camera.getY() + 1 * MOUSE_ZOOM_SPEED ) ) )
    elif type(camera.node().getLens()) == OrthographicLens:
      lens = camera.node().getLens()
      filmSize = lens.getFilmSize()
      lens.setFilmSize(filmSize*0.75)
  
  def movePivot(self, key, active):
    self.pressedKeys[key] = active
  
  def movePivotTask(self, task):
    ''' move the camera pivot by keypresses
    '''
    #print "I: CameraController.movePivotTask:", task.time
    # the movement the camera pivot should make
    moveVec = Vec3(0)
    for key, active in self.pressedKeys.items():
      if active:
        moveVec += self.moveActions[key]
    # move relative to camera viewport
    cam = WindowManager.getDefaultCamera()
    relVec = self.cameraPosPivot.getRelativeVector(cam, moveVec)
    self.cameraPosPivot.setPos(self.cameraPosPivot, relVec*globalClock.getDt())
    # send a event with the new position of the pivot
    pivotPos = Vec3(self.cameraPosPivot.getPos(render))
    messenger.send(EVENT_CAMERAPIVOT_POSITION_CHANGE, [pivotPos])
    return task.cont
  
  def setCameraRotation(self, rotation):
    print "I: CameraController.setCameraRotation", rotation
    self.cameraRotPivot.setHpr( render, rotation )
  
  def toggleLens(self):
    camera = WindowManager.getDefaultCamera()
    print type(camera.node())
    print type(camera.node().getLens())
    if type(camera.node().getLens()) == PerspectiveLens:
      lens = OrthographicLens()
      lens.setFilmSize(Vec2(10,10))
      camera.node().setLens(lens)
    elif type(camera.node().getLens()) == OrthographicLens:
      lens = PerspectiveLens()
      camera.node().setLens(lens)
  
  def getCreatePos( self ):
    return self.cameraPosPivot.getPos( render )
  # --- helper function end ---
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton2Pressed( self ):
    #print "enterMouseButton1Pressed"
    #self.ignoreAll()
    
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
    self.ignore('mouse2-up')
    taskMgr.remove( 'taskMouseButton2Pressed' )
    self.taskMouseButton2PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---
  
  
  # --- MouseButton1Pressed start ---
  def enterMouseButton3Pressed( self ):
    #self.ignoreAll()
    
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
    self.ignore('mouse3-up')
    taskMgr.remove( 'taskMouseButton3Pressed' )
    self.taskMouseButton1PressedRunning = False
    mouseHandler.toggleMouseFixed( False )
  # --- MouseButton1Pressed end ---

base.disableMouse()
cameraController = CameraController()
