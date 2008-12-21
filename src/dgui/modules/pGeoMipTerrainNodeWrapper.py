from dgui.modules.pBaseWrapper import BaseWrapper

class GeoMipTerrainNodeWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.append('minlevel')
