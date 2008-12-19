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
    
    self.mutableParameters['fov']      = [ Vec2, 'getFov', 'setFov', True]
    self.mutableParameters['near']     = [ float, 'getNear', 'setNear', True]
    self.mutableParameters['far']      = [ float, 'getFar', 'setFar', True]
    self.mutableParameters['exponent'] = [ float, 'getExponent', 'setExponent', True]
  
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
  
  def getExponent(self, *args, **kwargs):
    return self.light.getExponent(*args, **kwargs)
  def setExponent(self, value):
    # prevent a crash by limiting the value
    value = min(127.0, max(0.0, value))
    return self.light.setExponent(value)
