__all__=['DirectionalLightNodeWrapper']

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pConfigDefs import *

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None, name='DirectionalLight'):
    # define the name of this object
    name = 'DirectionalLight'
    LightNodeWrapper.__init__(self, parent, name, DIRECTIONALLIGHT_WRAPPER_DUMMYOBJECT, DirectionalLight)
    
    self.mutableParameters['specularColor'] = [ Vec4,
      self.light.getSpecularColor,
      self.light.setSpecularColor,
      None,
      None ]
