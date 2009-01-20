from dgui.modules.pBaseWrapper import BaseWrapper

class ObjectEggGroup(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting=list()
    self.mutableParametersSorting.append('collision_solid_type')
    self.mutableParametersSorting.append('collide_flags')
    self.mutableParametersSorting.append('dcs_type')
    self.mutableParametersSorting.append('billaboard_type')
