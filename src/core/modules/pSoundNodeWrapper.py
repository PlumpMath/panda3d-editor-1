from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *
from core.pSoundManager import soundManager

class SoundNodeWrapper(VirtualNodeWrapper):
  def __init__(self, parent, name):
    VirtualNodeWrapper.__init__(self, parent, name, SOUNDNODE_WRAPPER_DUMMYOBJECT)
    
    self.soundEffect = None
    self.soundFilepath = None
    
    self.mutableParameters['volume']    = [ float,
      self.soundEffect.getVolume,
      self.soundEffect.setVolume,
      None,
      None ]
    self.mutableParameters['loop']      = [ bool,
      self.soundEffect.getLoop,
      self.soundEffect.setLoop,
      None,
      None ]
    self.mutableParameters['loopCount'] = [ int,
      self.soundEffect.getLoopCount,
      self.soundEffect.setLoopCount,
      None,
      None ]
    self.mutableParameters['playRate']  = [ float,
      self.soundEffect.getPlayRate,
      self.soundEffect.setPlayRate,
      None,
      None ]
    self.mutableParameters['priority']  = [ int,
      self.soundEffect.getPriority,
      self.soundEffect.setPriority,
      None,
      None ]
  
  def setSound(self, filepath):
    self.soundFilepath = filepath
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.soundFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setSound(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
