from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggData(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggData):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggData')
    self.eggData = eggData
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggData = None
    self.modelWrapper = None
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
