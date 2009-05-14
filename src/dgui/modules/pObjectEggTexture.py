from dgui.modules.pBaseWrapper import BaseWrapper

class ObjectEggTexture(BaseWrapper):
  def __init__(self, *args, **kwargs):
    BaseWrapper.__init__(self, *args, **kwargs)
    self.mutableParametersSorting.extend( [
        'polygonGroup',
        'texture filename',
        'u wrap mode',
        'v wrap mode',
        'min filter',
        'mag filter',
        'env type',
        'combine mode',
        'c. mode channel',
        'combine operand',
        'c. operand channel',
        'c. operand number',
        'combine source',
        'c. Source channel',
        'c. source number',
      ] )