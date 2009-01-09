from pandac.PandaModules import *

class ObjectEggData:
  def __init__(self, eggData, modelWrapper):
    self.eggData = eggData
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
  
  def destroy(self):
    self.eggData = None
    self.modelWrapper = None
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
