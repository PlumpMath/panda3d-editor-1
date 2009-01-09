from pandac.PandaModules import *

from modules import *

#import objectEditorModules

class ObjectEditor:
  def __init__(self):
    self.editObject = None
  
  def setEditObject(self, editObject):
    if type(editObject) == NodePathWrapper:
      self.editObject = objectEditorModules.getObjectEditor(editObject)
    else:
      print "I: ObjectEditor.getEditable: unknown type, cannot edit", type(editObject)
  
  def getEditable(self):
    return self.editObject.getEditable()
  
  def startEdit(self, objectPart):
    self.editObject.startEdit(objectPart)
  
  def stopEdit(self):
    self.editObject.stopEdit()
    self.editObject = None
  
  def saveChanges(self):
    if self.editModule:
      self.editModule.getEggData()
  
  #def disableEditor(self):
  #  self.editObject.stopEdit()
  
  def getTextureLayers(self):
    if self.editObject:
      return getTextureLayers(self.editObject)
    return []
  
  def separateModel(self):
    ''' creates a new separate model from the selected object
    '''
    pass

objectEditor = ObjectEditor()