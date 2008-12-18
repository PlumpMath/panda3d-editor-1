from dgui.modules.pBaseWrapper import *

class LightNodeWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParameters['Attenuation'] = ['point3', 'getAttenuation', 'setAttenuation', None]
    self.mutableParametersSorting.append('Attenuation')
    self.mutableParameters['Priority'] = ['int', 'getPriority', 'setPriority', None]
    self.mutableParametersSorting.append('Priority')
    self.mutableParameters['SpecLight'] = ['vec4', 'getSpecularColor', 'setSpecularColor', None]
    self.mutableParametersSorting.append('SpecLight')