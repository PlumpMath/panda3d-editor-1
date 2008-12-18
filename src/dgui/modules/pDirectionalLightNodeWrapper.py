from dgui.modules.pLightNodeWrapper import *

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, *args, **kwargs):
    LightNodeWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.remove('Attenuation')
