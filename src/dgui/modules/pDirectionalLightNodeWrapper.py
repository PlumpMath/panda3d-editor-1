from dgui.modules.pLightNodeWrapper import *

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, object):
    LightNodeWrapper.__init__(self, object)
    self.mutableParametersSorting.remove('Attenuation')
