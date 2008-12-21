from dgui.modules.pLightNodeWrapper import LightNodeWrapper

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, *args, **kwargs):
    LightNodeWrapper.__init__(self, *args, **kwargs)
