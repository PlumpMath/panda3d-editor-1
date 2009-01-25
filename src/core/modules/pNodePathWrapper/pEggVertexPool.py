from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggVertexPool(ObjectEggBase):
  className = 'EggVertexPool'
  def __init__(self, parent, modelWrapper, eggVertexPool):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggVertexPool')
    self.eggVertexPool = eggVertexPool
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggVertexPool = None
    self.modelWrapper = None
