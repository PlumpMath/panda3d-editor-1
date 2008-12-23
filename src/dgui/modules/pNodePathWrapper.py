from dgui.modules.pBaseWrapper import BaseWrapper
from core.pTexturePainter import texturePainter, getTextureAndStage

class NodePathWrapper(BaseWrapper):
  def startEdit(self):
    BaseWrapper.startEdit(self)
    
    texStages = getTextureAndStage(self.object.model)
    
    if len(texStages) > 0:
      texturePainter.startEdit(self.object.model, texStages[0][1])
  
  def stopEdit(self):
    texturePainter.stopEdit()
    BaseWrapper.stopEdit(self)