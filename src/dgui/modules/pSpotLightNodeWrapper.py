from dgui.modules.pLightNodeWrapper import *

class SpotLightNodeWrapper(LightNodeWrapper):
  def __init__(self, *args, **kwargs):
    LightNodeWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.extend( [
      'exponent', 'near', 'far', 'fov'] )
