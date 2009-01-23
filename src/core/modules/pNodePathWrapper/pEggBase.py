__all__=['ObjectEggBase']

from pandac.PandaModules import *

from core.pTreeNode import *
from core.pConfigDefs import *

class ObjectEggBase(TreeNode):
  def __init__(self, parent, modelWrapper, name='EggBase'):
    self.modelWrapper = modelWrapper
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
  
  def setEditmodeEnabled(self, recurseException=[]):
    TreeNode.setEditmodeEnabled(self, recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    TreeNode.setEditmodeDisabled(self, recurseException)
  
  def startEdit(self):
    if TreeNode.isEditmodeEnabled(self):
      # disable the 3d window object selection
      TreeNode.startEdit(self)
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
    else:
      print "W: ObjectEggBase.startEdit: editmode not enabled"
    
  def stopEdit(self):
    if TreeNode.isEditmodeEnabled(self):
      TreeNode.stopEdit(self)
      # enable the 3d window object selection
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
    else:
      print "W: ObjectEggBase.stopEdit: editmode not enabled"
  
  def destroy(self):
    TreeNode.destroy(self)
