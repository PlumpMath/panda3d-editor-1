import pickle

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class LightNodeWrapper(VirtualNodeWrapper):
  def __init__(self, name, lightType, *args, **kwargs):
    VirtualNodeWrapper.__init__(self, *args, **kwargs)
    
    self.light = lightType(name)
    self.lightNodePath = self.attachNewNode(self.light)
    # create the light
    render.setLight(self.lightNodePath)

  def getColor(self, *args, **kwargs):
    return self.light.getColor(*args, **kwargs)
  
  def getPriority(self, *args, **kwargs):
    return self.light.getPriority(*args, **kwargs)
  
  def setColor(self, *args, **kwargs):
    return self.light.setColor(*args, **kwargs)
  
  def setPriority(self, *args, **kwargs):
    return self.light.setPriority(*args, **kwargs)
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    instance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'LightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance
