from dgui.modules.pBaseWrapper import BaseWrapper
from core.pTexturePainter import texturePainter, getTextureAndStage

class NodePathWrapper(BaseWrapper):
  def startEdit(self):
    BaseWrapper.startEdit(self)
    
    texStages = getTextureAndStage(self.object.model)
    
    self.paintModel = None
    if len(texStages) > 0:
      self.paintModel = texturePainter.startEdit(self.object.model, texStages[0][1])
  
  def stopEdit(self):
    if self.paintModel:
      texturePainter.stopEdit(self.paintModel)
    BaseWrapper.stopEdit(self)