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
    
    #                       name        = [ varType, 'getFuncName', 'setFuncName', 'hasFuncName' ]
    self.mutableParameters['volume']    = [ float,
      SoundNodeWrapper.getVolume,
      SoundNodeWrapper.setVolume,
      True ]
    self.mutableParameters['loop']      = [ bool,
      SoundNodeWrapper.getLoop,
      SoundNodeWrapper.setLoop,
      True ]
    self.mutableParameters['loopCount'] = [ int,
      SoundNodeWrapper.getLoopCount,
      SoundNodeWrapper.setLoopCount,
      True ]
    self.mutableParameters['playRate']  = [ float,
      SoundNodeWrapper.getPlayRate,
      SoundNodeWrapper.setPlayRate,
      True ]
    self.mutableParameters['priority']  = [ int,
      SoundNodeWrapper.getPriority,
      SoundNodeWrapper.setPriority,
      True ]
    
  
  def setSound(self, filepath):
    self.soundFilepath = filepath
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)
  
  # must be handled by ourself (saving)
  def getVolume(self, *args, **kwargs):
    return self.soundEffect.getVolume(*args, **kwargs)
  def setVolume(self, *args, **kwargs):
    return self.soundEffect.setVolume(*args, **kwargs)
  
  def getLoop(self, *args, **kwargs):
    return self.soundEffect.getLoop(*args, **kwargs)
  def setLoop(self, *args, **kwargs):
    return self.soundEffect.setLoop(*args, **kwargs)
  
  def getLoopCount(self, *args, **kwargs):
    return self.soundEffect.getLoopCount(*args, **kwargs)
  def setLoopCount(self, *args, **kwargs):
    return self.soundEffect.setLoopCount(*args, **kwargs)
  
  def getPlayRate(self, *args, **kwargs):
    return self.soundEffect.getPlayRate(*args, **kwargs)
  def setPlayRate(self, *args, **kwargs):
    return self.soundEffect.setPlayRate(*args, **kwargs)
  
  def getPriority(self, *args, **kwargs):
    return self.soundEffect.getPriority(*args, **kwargs)
  def setPriority(self, *args, **kwargs):
    return self.soundEffect.setPriority(*args, **kwargs)
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.soundFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setSound(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)