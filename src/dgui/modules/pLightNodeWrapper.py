from dgui.modules.pBaseWrapper import *

class LightNodeWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.append('priority')
    self.mutableParametersSorting.append('specularColor')
    self.mutableParametersSorting.append('attenuation')
