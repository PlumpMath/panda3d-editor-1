import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class PointLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None, name='PointLight'):
    # define the name of this object
    name = 'PointLight'
    LightNodeWrapper.__init__(self, parent, name, POINTLIGHT_WRAPPER_DUMMYOBJECT, PointLight)
    
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
