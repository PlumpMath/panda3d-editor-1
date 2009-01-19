__all__=['ObjectEggBase']

from pandac.PandaModules import *

from core.pTreeNode import *
from core.pConfigDefs import *

class ObjectEggBase(TreeNode):
  def __init__(self, parent, modelWrapper, name='EggBase'):
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
    self.name = name # is duplicate should be removed and treeName in TreeNode used instead, also pBaseWrapper has this duplicate
    TreeNode.__init__(self, name, self)
    TreeNode.reparentTo(self, parent)
  
  def enableEditmode(self):
    pass
  
  def disableEditmode(self):
    pass
  
  def startEdit(self):
    # disable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
    
  def stopEdit(self):
    # enable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
  
  def save(self):
    print "I: ObjectEggBase.save"
    if self.editModule:
      print "  - saving"
      self.getEditable()[0].writeEgg('test.egg')
      self.editModule.destroy()
      self.editModule = None
  
  def destroy(self):
    TreeNode.detachNode(self)
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
