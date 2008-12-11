from dgui.modules.pBaseWrapper import *

class LightNodeWrapper(BaseWrapper):
  def __init__(self, object):
    BaseWrapper.__init__(self, object)
    self.mutableParameters['Attenuation'] = ['point3', 'getAttenuation', 'setAttenuation', None]
    self.mutableParametersSorting.append('Attenuation')