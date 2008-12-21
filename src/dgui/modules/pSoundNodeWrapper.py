from dgui.modules.pBaseWrapper import *

class SoundNodeWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.append('loop')
    self.mutableParametersSorting.append('loopCount')
    self.mutableParametersSorting.append('volume')
    self.mutableParametersSorting.append('playRate')
    self.mutableParametersSorting.append('priority')
    self.mutableParametersSorting.append('minDistance')
    self.mutableParametersSorting.append('maxDistance')
