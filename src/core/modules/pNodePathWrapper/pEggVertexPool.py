from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggVertexPool(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggVertexPool):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggVertexPool')
    self.eggVertexPool = eggVertexPool
  
  def destroy(self):
    self.eggVertexPool = None
    self.modelWrapper = None
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
  
