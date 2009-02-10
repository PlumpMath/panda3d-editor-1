from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task.Task import Task

from pWindow import WindowManager
from core.pConfigDefs import *
from core.pModelIdManager import modelIdManager
#from core.pCameraController import cameraController
from core.pMouseHandler import mouseHandler
from core.modules.pBaseWrapper import *
from core.pModelController import *

# for simplicity, we crate the axiscube every time the editor is loaded
import pCreateAxisCube

DEBUG = False

class ModelModificator(DirectObject):
  ''' a modificator attached to the object, which allows moving/rotating/scaling
  '''
  def __init__(self): #, modelController):
    "I: ModelModificator.__init__:"
    self.__modelModificationMode = MODEL_MODIFICATION_MODES[1]
    
    self.selectedObjectParent = None
    self.selectedObjectDistance = 0
    self.selectedObjectRelativePos = Vec3(0,0,0)
    self.__relativeModificationTo = None
    self.modelModeNode = None
    
    self.editmodeEnabled = False
    
    # a different model has been selected
    self.accept(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE, self.selectNode)
    # the same object has been selected again
    self.accept(EVENT_MODELCONTROLLER_SELECTED_OBJECT_AGAIN, self.changeMode)
    
    # we start modifying a object when our edittool has been selected
    self.accept(EVENT_MODELCONTROLLER_EDITTOOL_SELECTED, self.editToolSetup)
  
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
      
      # load axisCube, if that fails generate it and quit
      self.objectAxisCube = loader.loadModel(MODELCONTROLLER_AXISCUBE_MODEL)
      if not self.objectAxisCube:
        print "E: axiscube.bam does not exist, createAxisCube should have done that actually..."
        sys.exit()
      self.objectAxisCube.setLightOff()
      # axiscube can be hidden otherwise
      self.objectAxisCube.setBin('fixed', 39)
      
      # arrows for movement, rotation and scaling
      modificatorsNode = loader.loadModel(MODEL_MODIFICATION_MODEL)
      self.modelModeNodes = list()
      for i in xrange(len(MODEL_MODIFICATION_MODES_FUNCTIONS)):
        parent = NodePath('modelModificationNode-%i' % i)
        parent.setLightOff()
        self.modelModeNodes.append(parent)
        for nameTag in MODEL_MODIFICATION_MODES_FUNCTIONS[i]:
          searchTag = '**/%s' % nameTag
          modificator = modificatorsNode.find(searchTag)
          modificator.reparentTo(parent)
          modificator.setTag(MODEL_MODIFICATOR_TAG, nameTag)
          modelIdManager.setObject(modificator, nameTag)
          # arrows are hidden otherwise
          modificator.setBin('fixed', 40)
          # make arrows show trough everything
          modificator.setDepthTest(False)
          modificator.setDepthWrite(False)
      
      self.__relativeModificationTo = render
  
  def disableEditmode(self, deselect = True):
    if self.editmodeEnabled:
      
      self.ignoreAll()
      
      for i in xrange(len(MODEL_MODIFICATION_MODES_FUNCTIONS)):
        self.modelModeNodes[i].removeNode()
        self.modelModeNodes[i].detachNode()
      
      self.objectAxisCube.removeNode()
      self.objectAxisCube.detachNode()
  
  def selectNode(self, wrapper):
    ''' a different model has been selected '''
    # select the model and set to first modification type
    self.changeMode(wrapper, MODEL_MODIFICATION_MODES[1])
  
  def changeMode(self, wrapper=None, newMode=None):
    ''' change the mode of the modificator '''
    hasNodePath = BaseWrapper in wrapper.__class__.__mro__
    self.__unsetMode()
    if hasNodePath:
      if newMode is None:
        # select next modification tool
        modeIndex = MODEL_MODIFICATION_MODES.index(self.__modelModificationMode)
        newMode = MODEL_MODIFICATION_MODES[(modeIndex+1) % len(MODEL_MODIFICATION_MODES)]
      
      assert(newMode in MODEL_MODIFICATION_MODES)
      
      self.__modelModificationMode = newMode
      self.__setMode()
  
  def __unsetMode(self):
    if self.modelModeNode is not None:
      self.modelModeNode.hide()
      self.modelModeNode.detachNode()
      #self.modelModeNode.reparentTo(render)
      self.modelModeNode.setCollideMask(BitMask32.allOff())
      self.__relativeModificationTo = None
  
  def __setMode(self):
    if modelController.getSelectedObject():
      if self.__modelModificationMode == MODEL_MODIFICATION_MODE_TRANSLATE_LOCAL:
        self.modelModeNode = self.modelModeNodes[0]
        self.__relativeModificationTo = modelController.getSelectedObject()
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_TRANSLATE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[0]
        self.__relativeModificationTo = render
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_ROTATE_LOCAL:
        self.modelModeNode = self.modelModeNodes[1]
        self.__relativeModificationTo = modelController.getSelectedObject()
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_ROTATE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[1]
        self.__relativeModificationTo = render
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_SCALE_LOCAL:
        self.modelModeNode = self.modelModeNodes[2]
        self.__relativeModificationTo = modelController.getSelectedObject()
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_SCALE_GLOBAL:
        self.modelModeNode = self.modelModeNodes[2]
        self.__relativeModificationTo = render
      elif self.__modelModificationMode == MODEL_MODIFICATION_MODE_DISABLED:
        pass
      else:
        print "E: ModelModificator.__setMode: unknown mode", self.__modelModificationMode
      
      # when disabled we dont activate the modificators
      if self.__modelModificationMode != MODEL_MODIFICATION_MODE_DISABLED:
        self.modelModeNode.reparentTo(render)
        self.modelModeNode.setMat(render, Mat4().identMat())
        
        self.modelModeNode.setPos(render, modelController.getSelectedObject().getNodepath().getPos(render))
        
        if modelController.getSelectedObject() == self.__relativeModificationTo:
          if self.__relativeModificationTo == render:
            hpr = modelController.getSelectedObject().getNodepath().getHpr()
          else:
            hpr = modelController.getSelectedObject().getNodepath().getHpr(render)
        elif self.__relativeModificationTo == render:
          hpr = Vec3(0,0,0)
        self.modelModeNode.setHpr(render, hpr)
        self.modelModeNode.wrtReparentTo(modelController.getSelectedObject().getNodepath())
        
        self.modelModeNode.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
        self.modelModeNode.show()
  
  def editToolSetup(self, editTool):
    ''' the modificator tool has been pressed, it's now starting the task
    to modify the node '''
    #messenger.send(EVENT_MODELCONTROLLER_EDITTOOL_SELECTED)
    transX, transY, rotX, rotY, scaleX, scaleY = MODEL_MODIFICATION_FUNCTIONS[editTool]
    task = Task(self.editToolTask)
    
    selectedObject = modelController.getSelectedObject()
    if self.__relativeModificationTo == selectedObject:
      self.__modificationNode = selectedObject.getNodepath()
    else:
      # we are moving relative to some other node
      self.__origModelParent = selectedObject.getNodepath().getParent()
      self.__modificationNode = self.__relativeModificationTo.attachNewNode('dummyNode')
      self.__modificationNode.setPos(selectedObject.getNodepath().getPos())
      selectedObject.getNodepath().wrtReparentTo(self.__modificationNode)
    
    if type(self.__modificationNode) == NodePath:
      taskMgr.add(task, 'editToolTask', extraArgs = [task,transX, transY, rotX, rotY, scaleX, scaleY], uponDeath=self.editToolCleanup)
      self.accept('mouse1-up', taskMgr.remove, ['editToolTask'])
      mouseHandler.toggleMouseFixed(True)
    else:
      print "E: ModelModificator.editToolSetup: invalid node"
      print "  -", type(self.__modificationNode), self.__modificationNode.__class__.__name__
  
  def editToolTask(self, task, transX, transY, rotX, rotY, scaleX, scaleY):
    ''' task in which the edittool is active and modifying the model
    '''
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
      
      self.__modificationNode.setPos(self.__modificationNode, dPosX)
      self.__modificationNode.setPos(self.__modificationNode, dPosY)
      self.__modificationNode.setHpr(self.__modificationNode, dRotX)
      self.__modificationNode.setHpr(self.__modificationNode, dRotY)
      self.__modificationNode.setScale(self.__modificationNode.getScale() + dScaleX)
      self.__modificationNode.setScale(self.__modificationNode.getScale() + dScaleY)
      
      # send event that the object has been modified
      messenger.send(EVENT_MODELCONTROLLER_FAST_REFRESH)
      
      self.objectAxisCube.setScale(self.__modificationNode.getPos(render))
    return task.cont
  
  def editToolCleanup(self, task):
    ''' stop editing using the edittool (the mouse button has been released)
    '''
    messenger.send(EVENT_MODELCONTROLLER_EDITTOOL_DESELECTED)
    # the modification node needs to be destroyed if it's not the __selectedModel
    if self.__modificationNode != modelController.getSelectedObject().getNodepath():
        modelController.getSelectedObject().getNodepath().wrtReparentTo(self.__origModelParent)
        self.__modificationNode.detachNode()
        self.__modificationNode.removeNode()
    
    mouseHandler.toggleMouseFixed(False)
    self.__setMode()
    messenger.send(EVENT_MODELCONTROLLER_FULL_REFRESH)

modelModificator = ModelModificator()