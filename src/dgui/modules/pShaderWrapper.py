from dgui.modules.pBaseWrapper import BaseWrapper

class ShaderWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.append('mixmap')
    self.mutableParametersSorting.append('detailmap1')
    self.mutableParametersSorting.append('tex1scale')
    self.mutableParametersSorting.append('detailmap2')
    self.mutableParametersSorting.append('tex2scale')
    self.mutableParametersSorting.append('detailmap3')
    self.mutableParametersSorting.append('tex3scale')
    self.mutableParametersSorting.append('update')
    self.mutableParametersSorting.append('paintColor')
    self.mutableParametersSorting.append('paintSize')
