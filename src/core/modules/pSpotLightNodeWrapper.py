import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class SpotLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None, name='SpotLight'):
    LightNodeWrapper.__init__(self, parent, name, SPOTLIGHT_WRAPPER_DUMMYOBJECT, Spotlight)
    self.lens = PerspectiveLens()
    self.light.setLens(self.lens)
  
  def getNear(self, *args, **kwargs):
    return self.lens.getNear(*args, **kwargs)
  def setNear(self, *args, **kwargs):
    return self.lens.setNear(*args, **kwargs)
  
  def getFar(self, *args, **kwargs):
    return self.lens.getFar(*args, **kwargs)
  def setFar(self, *args, **kwargs):
    return self.lens.setFar(*args, **kwargs)
  
  def getFov(self, *args, **kwargs):
    return self.lens.getFov(*args, **kwargs)
  def setFov(self, *args, **kwargs):
    return self.lens.setFov(*args, **kwargs)
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    parameters['fov'] = [self.getFov()[0], self.getFov()[1]]
    parameters['near'] = self.getNear()
    parameters['far'] = self.getFar()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment('SpotLightNodeWrapper-params', str(parameters))
      instance.addChild(comment)
    return instance
  def loadFromData(self, eggGroup, filepath):
    LightNodeWrapper.loadFromData(self, eggGroup, filepath)
    data = dict()
    for child in eggGroup.getChildren():
      if type(child) == EggComment:
        if child.getName() == 'SpotLightNodeWrapper-params':
          exec("data = %s" % child.getComment())
    if data.has_key('fov'):
      self.setFov(Vec2(*data['fov']))
    if data.has_key('near'):
      self.setNear(data['near'])
    if data.has_key('far'):
      self.setFar(data['far'])
