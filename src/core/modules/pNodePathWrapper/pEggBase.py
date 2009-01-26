__all__=['ObjectEggBase']

from pandac.PandaModules import *

from core.pTreeNode import *
from core.pConfigDefs import *

class ObjectEggBase(TreeNode):
  className = 'EggBase'
  def __init__(self, parent, modelWrapper, name='EggBase'):
    self.modelWrapper = modelWrapper
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    
    self.possibleFunctions = []
    self.possibleChildren = [
        'ObjectEggGroup',
        'ObjectEggPolygon',
        'ObjectEggTexture',
        'ObjectEggVertexPool',
      ]
  
  def setEditmodeEnabled(self):
    TreeNode.setEditmodeEnabled(self)
  
  def setEditmodeDisabled(self):
    TreeNode.setEditmodeDisabled(self)
  
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
  
  def revert(self):
    ''' reverts to the model on the disk '''
    print "I: ObjectEggBase.revert: todo"
  
  def update(self):
    ''' refeshes the visual output of this model, using the modifed settings '''
    print "I: ObjectEggBase.update: todo"
  
  def destroy(self):
    TreeNode.destroy(self)
