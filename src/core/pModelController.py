from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from pandac.PandaModules import *
from direct.task.Task import Task

from pWindow import WindowManager
from core.pConfigDefs import *
from core.pModelIdManager import modelIdManager
#from core.pCameraController import cameraController
from core.pMouseHandler import mouseHandler

DEBUG = False

class ModelController( DirectObject ):
  def __init__( self ):
    self.__selectedModel = None
    self.__modelMode = MODEL_MODIFICATION_MODES[0]
    
    self.__selectedModel = None
    self.selectedObjectParent = None
    self.selectedObjectDistance = 0
    self.selectedObjectRelativePos = Vec3(0,0,0)
    self.__relativeModificationTo = None
    self.modelModeNode = None
    
    self.enabled = False
    
    self.accept( EVENT_WINDOW_FOCUS_CHANGE, self.onWindowFocusChange )
  
  def toggle( self, state=None ):
    if state is None:
      state = not self.enabled
    
    if state:
      self.enable()
    else:
      self.disable()
    self.enabled = state
  
  def enable(self):
    if not self.enabled:
      self.modelModeNode = NodePath('temp')
      
      self.createCollisionPicker()
      
      # create another ray which copy's the mouseray of the camera
      # using the real mouseray can cause problems
      self.mouseRayCameraNodePath = NodePath( 'editorMouseRayNodePath' )
      if WindowManager.getDefaultCamera() != None:
        self.mouseRayCameraNodePath.reparentTo( WindowManager.getDefaultCamera() )
      self.mouseRayNodePath = NodePath( 'editorMouseRayNodePath' )
      self.mouseRayNodePath.reparentTo( self.mouseRayCameraNodePath )
      
      # load axisCube, if that fails generate it and quit
      self.objectAxisCube = loader.loadModel( MODELCONTROLLER_AXISCUBE_MODEL )
      self.objectAxisCube.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
      #self.objectAxisCube.reparentTo( render )
      if not self.objectAxisCube:
        if DEBUG:
          print "E: axiscube.bam was missing, generating now"
          print "  - please restart the application now"
        import createAxisCube
        sys.exit()
      self.objectAxisCube.setLightOff()
      
      if DEBUG:
        print "I: modelControllerClass: reading", MODEL_MODIFICATION_MODEL
      # arrows for movement and rotation
      modificatorsNode = loader.loadModel( MODEL_MODIFICATION_MODEL )
      self.modelModeNodes = list()
      for i in xrange(len(MODEL_MODIFICATION_MODES_FUNCTIONS)):
        parent = NodePath('modelModificationNode-%i' % i) # render.attachNewNode( 'modelModificationNode-%i' % i )
        parent.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
        parent.setLightOff()
        self.modelModeNodes.append( parent )
        for nameTag in MODEL_MODIFICATION_MODES_FUNCTIONS[i]:
          searchTag = '**/%s' % nameTag
          modificator = modificatorsNode.find( searchTag )
          if DEBUG:
            print "  - searching", searchTag, "found", modificator
          modificator.reparentTo( parent )
          modificator.setTag( MODEL_MODIFICATOR_TAG, nameTag )
          #modificator.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
          modelIdManager.setObject( modificator, nameTag )
          # arrows are hidden otherwise
          modificator.setBin("BT_unsorted", 40)
      
      self.__relativeModificationTo = render
      
      self.accept( 'mouse1', self.mouseButtonPress )
  
  def disable(self):
    if self.enabled:
      self.ignoreAll()
      
      for i in xrange(len(MODEL_MODIFICATION_MODES_FUNCTIONS)):
        self.modelModeNodes[i].removeNode()
        self.modelModeNodes[i].detachNode()
      
      self.objectAxisCube.removeNode()
      self.objectAxisCube.detachNode()
      
      self.mouseRayNodePath.removeNode()
      self.mouseRayNodePath.detachNode()
      self.mouseRayCameraNodePath.removeNode()
      self.mouseRayCameraNodePath.detachNode()
      
      self.destroyCollisionPicker()
  
  def onWindowFocusChange( self ):
    """Used if the focused window has changed."""
    if len(WindowManager.windows) == 1: return
    if WindowManager.activeWindow == None:
      self.mouseRayCameraNodePath.detachNode()
      self.editorPickerNodePath.detachNode()
    else:
      self.mouseRayCameraNodePath.reparentTo(WindowManager.activeWindow.camera)
      self.editorPickerNodePath.reparentTo(WindowManager.activeWindow.camera)
    self.updatePickerRay()
  
  def mouseButtonPress( self ):
    if self.enabled:
      pickedObj = self.getMouseOverNode()
      if DEBUG:
        print "I: modelController.mouseButtonPress: pickedObj", pickedObj
      editModel = self.getMouseOverObjectModel(pickedObj)
      editToolSelection = self.getMouseOverObjectTool(pickedObj)
      editTool = self.getMouseOverObjectTool(pickedObj)
      if editTool:
        if DEBUG:
          print "  - editTool selected", editTool
        self.editToolSetup( editTool )
      elif editModel:
        if DEBUG:
          print "  - editModel selected", editModel
        self.selectModel( editModel )
      else:
        if DEBUG:
          print "  - deselect"
        self.selectModel( None )
  
  def editToolSetup( self, editTool ):
    messenger.send(EVENT_MODELCONTROLLER_EDITTOOL_SELECTED)
    transX, transY, rotX, rotY, scaleX, scaleY = MODEL_MODIFICATION_FUNCTIONS[editTool]
    task = Task(self.editToolTask)
    
    if DEBUG:
      print "I: modelController.editToolSetup:"
      print "   - selected:", self.__selectedModel
      print "   - relative:", self.__relativeModificationTo
    
    if self.__relativeModificationTo == self.__selectedModel:
      self.__modificationNode = self.__selectedModel
    else:
      # we are moving relative to some other node
      self.__origModelParent = self.__selectedModel.getParent()
      self.__modificationNode = self.__relativeModificationTo.attachNewNode( 'dummyNode' )
      self.__modificationNode.setPos( self.__selectedModel.getPos() )
      self.__selectedModel.wrtReparentTo( self.__modificationNode )
    
    taskMgr.add( task, 'editToolTask', extraArgs = [task,transX, transY, rotX, rotY, scaleX, scaleY], uponDeath=self.editToolCleanup )
    self.accept( 'mouse1-up', taskMgr.remove, ['editToolTask'] )
    mouseHandler.toggleMouseFixed( True )
  def editToolTask( self, task, transX, transY, rotX, rotY, scaleX, scaleY ):
    if task.frame: # dont run on first frame (mouse is not centered yet)
      #print "editToolTask", transX, transY, rotX, rotY, scaleX, scaleY
      mx,my = mouseHandler.getMousePos()
      dt = 0.1 #globalClock.getDt() * 10
      dPosX   = transX * mx * dt * 250
      dPosY   = transY * my * dt * 250
      dRotX   = rotX   * mx * dt * 250
      dRotY   = rotY   * my * dt * 250
      dScaleX = scaleX * mx * dt
      dScaleY = scaleY * my * dt
      
      self.__modificationNode.setPos( self.__modificationNode, dPosX )
      self.__modificationNode.setPos( self.__modificationNode, dPosY )
      self.__modificationNode.setHpr( self.__modificationNode, dRotX )
      self.__modificationNode.setHpr( self.__modificationNode, dRotY )
      self.__modificationNode.setScale( self.__modificationNode.getScale() + dScaleX )
      self.__modificationNode.setScale( self.__modificationNode.getScale() + dScaleY )
      
      messenger.send( EVENT_MODELCONTROLLER_FAST_REFRESH )
      
      self.objectAxisCube.setScale( self.__modificationNode.getPos(render) )
    return task.cont
  def editToolCleanup( self, task ):
    messenger.send(EVENT_MODELCONTROLLER_EDITTOOL_DESELECTED)
    # the modification node needs to be destroyed if it's not the __selectedModel
    if self.__modificationNode != self.__selectedModel:
        self.__selectedModel.wrtReparentTo( self.__origModelParent )
        self.__modificationNode.detachNode()
        self.__modificationNode.removeNode()
    
    mouseHandler.toggleMouseFixed( False )
    self.__setMode()
    messenger.send( EVENT_MODELCONTROLLER_FULL_REFRESH )
  
  def selectNodePath( self, nodePath ):
    if DEBUG:
      print "I: modelController.selectNodePath: nodePath", nodePath
    modelId = modelIdManager.getObjectId( nodePath )
    object = modelIdManager.getObject( modelId )
    self.selectModel( object )
  
  def selectModel( self, model=None ):
    if DEBUG:
      print "I: modelController.selectModel", model
    if model is None:
      # no object has been selected
      if DEBUG:
        print "  - deselect model"
      self.__unsetMode()
      self.__deselectModel()
      self.__selectedModel = None
      messenger.send( EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, [model] )
    else:
      if model == self.__selectedModel:
        # the current model has been clicked again
        if DEBUG:
          print "  - clicked same object again", self.__modelMode
        self.__unsetMode()
        curModelMode = MODEL_MODIFICATION_MODES.index( self.__modelMode )
        newModelMode = MODEL_MODIFICATION_MODES[(curModelMode+1) % len(MODEL_MODIFICATION_MODES)]
        self.__modelMode = newModelMode
        self.__setMode()
        messenger.send( EVENT_MODELCONTROLLER_SELECT_MODEL_AGAIN, [model] )
      else:
        # a new / different model has been clicked
        if DEBUG:
          print "  - clicked new / different object"
        self.__unsetMode()
        self.__deselectModel()
        self.__selectedModel = model
        self.__modelMode = MODEL_MODIFICATION_MODES[0]
        self.__selectModel()
        self.__setMode()
        messenger.send( EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, [model] )
  
  def getSelectedModel( self ):
    return self.__selectedModel
  
  def __selectModel( self ):
    if self.__selectedModel:
      self.__selectedModel.startEdit()
      #self.modelModificatorsNode.detachNode()
      
      self.objectAxisCube.reparentTo( render )
      self.objectAxisCube.setScale( self.__selectedModel.getPos(render) )
  
  def __deselectModel( self ):
    if self.__selectedModel:
      self.__selectedModel.stopEdit()
      #self.modelModificatorsNode.hide()
      self.objectAxisCube.detachNode()
  
  def __setMode( self ):
    if self.__selectedModel:
      if self.__modelMode == MODEL_MODIFICATION_MODE_TRANSLATE_LOCAL:
        self.modelModeNode = self.modelModeNodes[0]
        self.__relativeModificationTo = self.__selectedModel
      elif self.__modelMode == MODEL_MODIFICATION_MODE_TRANSLATE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[0]
        self.__relativeModificationTo = render
      elif self.__modelMode == MODEL_MODIFICATION_MODE_ROTATE_LOCAL:
        self.modelModeNode = self.modelModeNodes[1]
        self.__relativeModificationTo = self.__selectedModel
      elif self.__modelMode == MODEL_MODIFICATION_MODE_ROTATE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[1]
        self.__relativeModificationTo = render
      elif self.__modelMode == MODEL_MODIFICATION_MODE_SCALE_LOCAL:
        self.modelModeNode = self.modelModeNodes[2]
        self.__relativeModificationTo = self.__selectedModel
      elif self.__modelMode == MODEL_MODIFICATION_MODE_SCALE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[2]
        self.__relativeModificationTo = render
      else:
        if DEBUG:
          print "modelControllerClass.__setMode: unknown mode", self.__modelMode
      
      # get the objects radius
      try:
        r = self.__selectedModel.model.getBounds().getRadius()
      except:
        r = 1
      #print "object radius", r
      
      if False:
        #self.modelModeNode.reparentTo( render )
        # only keep the position / rotation on the model modificators
        self.modelModeNode.setMat( render, Mat4().identMat() )
        self.modelModeNode.setPos( render, self.__selectedModel.getPos(render) )
        self.modelModeNode.setHpr( render, self.__selectedModel.getHpr(self.__relativeModificationTo) )
        self.modelModeNode.setScale( render, r / 4. )
        self.modelModeNode.wrtReparentTo( self.__selectedModel )
        
        self.modelModeNode.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
        self.modelModeNode.show()
      else:
        # the object's radius is changed when something is attached
        self.modelModeNode.detachNode()
        #r = self.__selectedModel.getBounds().getRadius()
        
        self.modelModeNode.reparentTo( render )
        self.modelModeNode.setMat( render, Mat4().identMat() ) #self.__selectedModel.getMat(render) )
        
        self.modelModeNode.setPos( render, self.__selectedModel.getPos( render ) )
        
        if self.__selectedModel == self.__relativeModificationTo:
          #print "self"
          if self.__relativeModificationTo == render:
            hpr = self.__selectedModel.getHpr()
          else:
            hpr = self.__selectedModel.getHpr( render )
        elif self.__relativeModificationTo == render:
          #print "vec3(0,0,0)"
          hpr = Vec3(0,0,0)
        #else:
          #print "parent"
          #hpr = self.__selectedModel.getHpr( render )
        self.modelModeNode.setHpr( render, hpr )
        self.modelModeNode.wrtReparentTo( self.__selectedModel )
        
        self.modelModeNode.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
        self.modelModeNode.show()
  
  def __unsetMode( self ):
    if self.modelModeNode is not None:
      self.modelModeNode.hide()
      self.modelModeNode.reparentTo( render )
      self.modelModeNode.setCollideMask( BitMask32.allOff() )
  
  def createCollisionPicker( self ):
    #print "editor.editorClass.createCollisionPicker"
    self.editorCollTraverser    = CollisionTraverser()
    self.editorCollHandler      = CollisionHandlerQueue()
    self.editorPickerNode       = CollisionNode('mouseRay')
    if WindowManager.getDefaultCamera() != None:
      self.editorPickerNodePath   = WindowManager.getDefaultCamera().attachNewNode(self.editorPickerNode)
    else:
      self.editorPickerNodePath   = NodePath(self.editorPickerNode)
    self.editorPickerRay        = CollisionRay()
    self.editorPickerNode.addSolid( self.editorPickerRay )
    self.editorPickerNode.setFromCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
    self.editorPickerNode.setIntoCollideMask( BitMask32.allOff() )
    if DEBUG: self.editorPickerNodePath.show()
    self.editorCollTraverser.addCollider( self.editorPickerNodePath, self.editorCollHandler )
  
  def destroyCollisionPicker( self ):
    self.editorCollTraverser.removeCollider( self.editorPickerNodePath )
    self.editorPickerNode.setFromCollideMask( BitMask32.allOff() )
    self.editorPickerNode.setIntoCollideMask( BitMask32.allOff() )
    del self.editorPickerRay
    self.editorPickerNodePath.detachNode()
    del self.editorPickerNodePath
    del self.editorPickerNode
    del self.editorCollHandler
    del self.editorCollTraverser
  
  def updatePickerRay( self ):
    #print "editor.editorClass.updatePickerRay"
    mx,my = mouseHandler.getMousePos()
    if WindowManager.getDefaultCamera() != None:
      self.editorPickerRay.setFromLens(WindowManager.getDefaultCamera().node(), mx, my)
    else:
      pass # How to unset it?
    return True
  
  def getMouseOverNode( self ):
    ''' get a object under the mouse
    '''
    if self.updatePickerRay():
      self.editorCollTraverser.traverse(render)
      #assume for simplicity's sake that myHandler is a CollisionHandlerQueue
      if self.editorCollHandler.getNumEntries() > 0:
        self.editorCollHandler.sortEntries() #this is so we get the closest object
        pickedObj=self.editorCollHandler.getEntry(0).getIntoNodePath()
        return pickedObj
    return None
  
  def getMouseOverObjectModel( self, pickedObj ):
    #print "editor.editorClass.getMouseOverObject"
    ''' get a object under the mouse
    '''
    #pickedObj = self.getMouseOverNode()
    if pickedObj:
      pickedObjTaggedParent=pickedObj.findNetTag(EDITABLE_OBJECT_TAG)
#      print "- found tag", pickedObjTaggedParent
      if not pickedObjTaggedParent.isEmpty():
        objectId = pickedObjTaggedParent.getNetTag(EDITABLE_OBJECT_TAG)
        object = modelIdManager.getObject( objectId )
#        print "- found:", objectId, object
        return object
    return None
  
  def getMouseOverObjectTool( self, pickedObj ):
    if pickedObj:
      pickedObjTaggedParent=pickedObj.findNetTag(MODEL_MODIFICATOR_TAG)
      if not pickedObjTaggedParent.isEmpty():
        objectId = pickedObjTaggedParent.getNetTag(MODEL_MODIFICATOR_TAG)
        return objectId # modelIdManager.getObject( objectId )
    return None
  
  def getPickerRayDirection( self, mousePos=None ): #posX, posY ):
    #print "editor.editorClass.getPickerRayDirection"
    ''' return the direction of the ray sent trought the mouse
    '''
    # the pickerRay cannot be changed anyway once it has been set in a frame (BUG?)
    if self.updatePickerRay():
      # get the mouse-ray direction
      direction = self.editorPickerRay.getDirection()
      mouseRayDirection = Vec3(direction.getX(), direction.getY(), direction.getZ())
      # and normalize it
      mouseRayDirection.normalize()
      return mouseRayDirection
  # --- old version stuff - end ---


modelController = ModelController()




if __name__ == '__main__':
  print "testing2"
  class dummy:
    def __init__( self, name ):
      self.name = name
    def __repr__( self ):
      return self.name
    def highlight( self, state ):
      print "highlight", self.name, state
  obj1 = dummy('a')
  obj2 = dummy('b')
  obj3 = dummy('c')
  modelController.selectModel( obj1 )
  modelController.selectModel( obj1 )
  modelController.selectModel( obj1 )
  modelController.selectModel( obj2 )
  modelController.selectModel( None )
  modelController.selectModel( obj3 )
  modelController.selectModel( obj3 )
  modelController.selectModel( None )
