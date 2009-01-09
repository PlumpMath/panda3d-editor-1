from pandac.PandaModules import *

class ObjectEggVertexPool:
  def __init__(self, eggVertexPool, modelWrapper):
    self.eggVertexPool = eggVertexPool
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
  
  def destroy(self):
    self.eggVertexPool = None
    self.modelWrapper = None
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
  
