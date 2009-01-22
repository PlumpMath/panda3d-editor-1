#__all__ = ['modelController']

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task.Task import Task

from pWindow import WindowManager
from core.pConfigDefs import *

DEBUG = False

class ModelController(DirectObject):
  ''' activities:
  - stores the currently selected model
    - enables/disabled the editing mode of the selected models
    - assigns the modelModificators to the active model
  '''
  def __init__(self):
    # currently selected object (can be of nodepath type or other types (eggNodes))
    self.__selectedModel = None
    self.defaultObject = None
    
    self.accept(EVENT_MODELCONTROLLER_SELECT_OBJECT, self.selectObject)
    
    # set default object (when nothing is selected -> sceneRoot)
    self.accept(EVENT_SCENEGRAPH_CHANGE_ROOT, self.setDefault)
  
  def setDefault(self, defaultObject):
    self.defaultObject = defaultObject
  
  def selectObject(self, newObject=None):
    if newObject is None:
      newObject = self.defaultObject
    if newObject is None:
      # no object has been selected
      #self.__deselectModel()
      print "E: ModelController.selectObject: newObject is None"
      #messenger.send(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE, [newObject])
    else:
      # only select the object if it's editMode is enabled
      if newObject.isEditmodeEnabled():
        if newObject == self.__selectedModel:
          # the current model has been clicked again
          messenger.send(EVENT_MODELCONTROLLER_SELECTED_OBJECT_AGAIN, [newObject])
        else:
          # a new / different model has been clicked
          self.__deselectModel()
          self.__selectedModel = newObject
          self.__selectedModel.startEdit()
          messenger.send(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE, [newObject])
      else:
        print "W: ModelController.selectObject: object not in editmode", newObject
  
  def getSelectedObject(self):
    return self.__selectedModel
  
  def __deselectModel(self):
    if self.__selectedModel:
      self.__selectedModel.stopEdit()
      self.__selectedModel = None

modelController = ModelController()
