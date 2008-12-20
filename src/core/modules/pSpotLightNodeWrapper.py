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
    
    self.mutableParameters['attenuation'] = [ Vec3,
      self.light.getAttenuation,
      self.light.setAttenuation,
      None,
      None ]
    self.mutableParameters['specularColor'] = [ Vec4,
      self.light.getSpecularColor,
      self.light.setSpecularColor,
      None,
      None ]
    self.mutableParameters['fov'] = [ Vec2,
      self.lens.getFov,
      self.lens.setFov,
      None,
      None ]
    self.mutableParameters['near'] = [ float,
      self.lens.getNear,
      self.lens.setNear,
      None,
      None ]
    self.mutableParameters['far'] = [ float,
      self.lens.getFar,
      self.lens.setFar,
      None,
      None ]
    self.mutableParameters['exponent'] = [ float,
      self.light.getExponent,
      self.setExponent,
      None,
      None ]
  
  def setExponent(self, value):
    # prevent a crash by limiting the value
    value = min(127.0, max(0.0, value))
    return self.light.setExponent(value)
