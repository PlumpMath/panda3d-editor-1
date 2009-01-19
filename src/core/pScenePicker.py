#__all__ = ['modelController']

from direct.showbase.DirectObject import DirectObject
#from direct.fsm.FSM import FSM
from pandac.PandaModules import *
from direct.task.Task import Task

from pWindow import WindowManager
from core.pConfigDefs import *
from core.pModelIdManager import modelIdManager
from core.pMouseHandler import mouseHandler
from core.modules.pBaseWrapper import *
from core.pModelModificator import *
from core.pModelController import *

DEBUG = False

class ScenePicker(DirectObject):
  ''' gives the model in the 3d screen, when pressed on it
  '''
  def __init__(self):
    # if this function has been initialized (so it's functioning)
    self.editmodeEnabled = False
    
    # if modelSelectionActive models can be selected in the visual representation
    # if it's inactive pressing mouse button while having a object underneath
    # will not change the selected object
    # calling selectmodel will still change the selected object!
    self.__3dModelSelectionActive = False
    self.accept(EVENT_SCENEPICKER_MODELSELECTION_DISABLE, self.toggleObjectSelection, [False])
    self.accept(EVENT_SCENEPICKER_MODELSELECTION_ENABLE, self.toggleObjectSelection, [True])
    
    # the modelmodificator is the visual and colliding object to
    # move/rotate/scale objects
    #self.modelModificator = ModelModificator(self)
    
    self.accept(EVENT_WINDOW_FOCUS_CHANGE, self.onWindowFocusChange)
  
  def toggleEditmode(self, state=None):
    if state is None:
      state = not self.editmodeEnabled
    if state:
      self.enableEditmode()
    else:
      self.disableEditmode()
    self.editmodeEnabled = state
  
  def enableEditmode(self):
    if not self.editmodeEnabled:
      self.modelModeNode = NodePath('temp')
      
      self.createCollisionPicker()
      
#      self.modelModificator.enableEditmode()
      
      # create another ray which copy's the mouseray of the camera
      # using the real mouseray can cause problems
      self.mouseRayCameraNodePath = NodePath('editorMouseRayNodePath')
      if WindowManager.getDefaultCamera() != None:
        self.mouseRayCameraNodePath.reparentTo(WindowManager.getDefaultCamera())
      self.mouseRayNodePath = NodePath('editorMouseRayNodePath')
      self.mouseRayNodePath.reparentTo(self.mouseRayCameraNodePath)
      
      self.__3dModelSelectionActive = True
      
      self.accept('mouse1', self.mouseButtonPress)
  
  def disableEditmode(self, deselect = True):
    if self.editmodeEnabled:
      self.ignoreAll()
      
#      self.modelModificator.disableEditmode()
      
      self.mouseRayNodePath.removeNode()
      self.mouseRayNodePath.detachNode()
      self.mouseRayCameraNodePath.removeNode()
      self.mouseRayCameraNodePath.detachNode()
      
      self.destroyCollisionPicker()
  
  def toggleObjectSelection(self, newState=None):
    ''' toggle if pressing button1, over a model in the 3d window, selects it
    or not
    '''
    if newState is None:
      newState = not self.__3dModelSelectionActive
    
    self.__3dModelSelectionActive = newState
  
  def onWindowFocusChange(self):
    """Used if the focused window has changed."""
    if len(WindowManager.windows) == 1: return
    if WindowManager.activeWindow == None:
      self.mouseRayCameraNodePath.detachNode()
      self.editorPickerNodePath.detachNode()
    else:
      self.mouseRayCameraNodePath.reparentTo(WindowManager.activeWindow.camera)
      self.editorPickerNodePath.reparentTo(WindowManager.activeWindow.camera)
    self.updatePickerRay()
  
  def mouseButtonPress(self):
    if self.editmodeEnabled:
      pickedObjects = self.getMouseOverNodesList()
#      print "I: ModelController.mouseButtonPress: found", len(pickedObjects)
      if len(pickedObjects) > 0:
        editModel = self.getMouseOverObjectModel(pickedObjects[0])
        editTool = self.getMouseOverObjectTool(pickedObjects)
        if editTool:
          messenger.send(EVENT_MODELCONTROLLER_EDITTOOL_SELECTED, [editTool])
        elif editModel:
          if self.__3dModelSelectionActive:
            modelId = modelIdManager.getObjectId(editModel)
            object = modelIdManager.getObject(modelId)
            messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [object])
      else:
        # no object was clicked on
        messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [None])
  
  def createCollisionPicker(self):
    self.editorCollTraverser    = CollisionTraverser()
    self.editorCollHandler      = CollisionHandlerQueue()
    self.editorPickerNode       = CollisionNode('mouseRay')
    if WindowManager.getDefaultCamera() != None:
      self.editorPickerNodePath   = WindowManager.getDefaultCamera().attachNewNode(self.editorPickerNode)
    else:
      self.editorPickerNodePath   = NodePath(self.editorPickerNode)
    self.editorPickerRay        = CollisionRay()
    self.editorPickerNode.addSolid(self.editorPickerRay)
    self.editorPickerNode.setFromCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
    self.editorPickerNode.setIntoCollideMask(BitMask32.allOff())
    if DEBUG: self.editorPickerNodePath.show()
    self.editorCollTraverser.addCollider(self.editorPickerNodePath, self.editorCollHandler)
  
  def destroyCollisionPicker(self):
    self.editorCollTraverser.removeCollider(self.editorPickerNodePath)
    self.editorPickerNode.setFromCollideMask(BitMask32.allOff())
    self.editorPickerNode.setIntoCollideMask(BitMask32.allOff())
    del self.editorPickerRay
    self.editorPickerNodePath.detachNode()
    del self.editorPickerNodePath
    del self.editorPickerNode
    del self.editorCollHandler
    del self.editorCollTraverser
  
  def updatePickerRay(self):
    mx,my = mouseHandler.getMousePos()
    if WindowManager.getDefaultCamera() != None:
      self.editorPickerRay.setFromLens(WindowManager.getDefaultCamera().node(), mx, my)
    else:
      pass # How to unset it?
    return True
  
  def getMouseOverNodesList(self):
    ''' get all objects under the mouse, in the order of theyr appearance
    '''
    pickedObjects = list()
    if self.updatePickerRay():
      self.editorCollTraverser.traverse(render)
      if self.editorCollHandler.getNumEntries() > 0:
        self.editorCollHandler.sortEntries() #this is so we get the closest object
        for i in xrange(self.editorCollHandler.getNumEntries()):
          pickedObj=self.editorCollHandler.getEntry(i).getIntoNodePath()
#          print "I: ModelController.getMouseOverNodesList", i, pickedObj
          pickedObjects.append(pickedObj)
    return pickedObjects
  
  def getMouseOverObjectModel(self, pickedObj):
    ''' get a object under the mouse
    '''
    if pickedObj:
      pickedObjTaggedParent=pickedObj.findNetTag(EDITABLE_OBJECT_TAG)
      if not pickedObjTaggedParent.isEmpty():
        objectId = pickedObjTaggedParent.getNetTag(EDITABLE_OBJECT_TAG)
        object = modelIdManager.getObject(objectId)
        return object
    return None
  
  def getMouseOverObjectTool(self, pickedObjects):
    for i in xrange(len(pickedObjects)):
      pickedObj = pickedObjects[i]
      pickedObjTaggedParent=pickedObj.findNetTag(MODEL_MODIFICATOR_TAG)
      if not pickedObjTaggedParent.isEmpty():
        objectId = pickedObjTaggedParent.getNetTag(MODEL_MODIFICATOR_TAG)
        return objectId # modelIdManager.getObject(objectId)
    return None
  
  def getPickerRayDirection(self, mousePos=None): #posX, posY):
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

scenePicker = ScenePicker()
