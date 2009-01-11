__all__=['ObjectEggBase']

from pandac.PandaModules import *

from core.pTreeNode import *

class ObjectEggBase(TreeNode):
  def __init__(self, parent, modelWrapper, name='EggBase'):
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
    TreeNode.__init__(self, name, self)
    TreeNode.reparentTo(self, parent)
  
  def save(self):
    print "I: ObjectEggBase.save"
    if self.editModule:
      print "  - saving"
      self.getEditable()[0].writeEgg('test.egg')
      self.editModule.destroy()
      self.editModule = None
  
  def destroy(self):
    pass
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
