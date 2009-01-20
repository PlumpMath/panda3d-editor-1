__all__=['ObjectEggBase']

from pandac.PandaModules import *

from core.pTreeNode import *
from core.pConfigDefs import *

class ObjectEggBase(TreeNode):
  def __init__(self, parent, modelWrapper, name='EggBase'):
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
    TreeNode.__init__(self, name, self)
    TreeNode.reparentTo(self, parent)
  
  def setEditmodeEnabled(self, recurseException=[]):
    TreeNode.setEditmodeEnabled(self, recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    TreeNode.setEditmodeDisabled(self, recurseException)
  
  def startEdit(self):
    # disable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
    
  def stopEdit(self):
    # enable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
  
  def destroy(self):
    TreeNode.detachNode(self)
