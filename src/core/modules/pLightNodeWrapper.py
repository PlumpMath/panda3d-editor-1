import pickle

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class LightNodeWrapper(VirtualNodeWrapper):
  def __init__(self, name, lightType, *args, **kwargs):
    VirtualNodeWrapper.__init__(self, *args, **kwargs)
    
    # create a instance of the light
    self.light = lightType(name)
    self.lightNodePath = self.attachNewNode(self.light)
    # create the light
    render.setLight(self.lightNodePath)
  
  def getColor(self, *args, **kwargs):
    return self.light.getColor(*args, **kwargs)
  def setColor(self, *args, **kwargs):
    return self.light.setColor(*args, **kwargs)
  def hasColor(self, *args, **kwargs):
    # basewrapper only includes the color of objects if hasColor returns true
    return True
  
  def getPriority(self, *args, **kwargs):
    return self.light.getPriority(*args, **kwargs)
  def setPriority(self, *args, **kwargs):
    return self.light.setPriority(*args, **kwargs)
  def hasPriority(self, *args, **kwargs):
    return True
  
  def getAttenuation(self, *args, **kwargs):
    return self.light.getAttenuation(*args, **kwargs)
  def setAttenuation(self, *args, **kwargs):
    return self.light.setAttenuation(*args, **kwargs)
  def hasAttenuation(self, *args, **kwargs):
    return True
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    instance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if self.hasAttenuation():
      parameters['attenuation'] = [self.getAttenuation()[0], self.getAttenuation()[1], self.getAttenuation()[2]]
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment('LightNodeWrapper-params', str(parameters))
      instance.addChild(comment)
    return instance
  def setLoadData(self, eggGroup):
    VirtualNodeWrapper.setLoadData(self, eggGroup)
    data = dict()
    for child in eggGroup.getChildren():
      if type(child) == EggComment:
        if child.getName() == 'LightNodeWrapper-params':
          exec("data = %s" % child.getComment())
    if data.has_key('attenuation'):
      self.setAttenuation(Vec3(*data['attenuation']))
