from dgui.modules.pBaseWrapper import BaseWrapper

class ShaderWrapper(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.append('mixmap')
    self.mutableParametersSorting.append('detailmap1')
    self.mutableParametersSorting.append('tex1scale')
    self.mutableParametersSorting.append('tex1 mag filter')
    self.mutableParametersSorting.append('tex1 min filter')
    self.mutableParametersSorting.append('detailmap2')
    self.mutableParametersSorting.append('tex2scale')
    self.mutableParametersSorting.append('tex2 mag filter')
    self.mutableParametersSorting.append('tex2 min filter')
    self.mutableParametersSorting.append('detailmap3')
    self.mutableParametersSorting.append('tex3scale')
    self.mutableParametersSorting.append('tex3 mag filter')
    self.mutableParametersSorting.append('tex3 min filter')
    self.mutableParametersSorting.append('detailmap4')
    self.mutableParametersSorting.append('tex4scale')
    self.mutableParametersSorting.append('tex4 mag filter')
    self.mutableParametersSorting.append('tex4 min filter')
    self.mutableParametersSorting.append('update')
