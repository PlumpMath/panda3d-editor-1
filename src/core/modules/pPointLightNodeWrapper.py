__all__=['PointLightNodeWrapper']

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pConfigDefs import *

class PointLightNodeWrapper(LightNodeWrapper):
  className = 'PointLight'
  def __init__(self, parent=None, name='PointLight'):
    # define the name of this object
    name = 'PointLight'
    LightNodeWrapper.__init__(self, parent, name, POINTLIGHT_WRAPPER_DUMMYOBJECT, PointLight)
    
    self.mutableParameters['attenuation'] = [ Vec3,
        self.light.getAttenuation,
        self.light.setAttenuation,
        None,
        None,
        True ]
    self.mutableParameters['specularColor'] = [ Vec4,
        self.light.getSpecularColor,
        self.light.setSpecularColor,
        None,
        None,
        True ]
