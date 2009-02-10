__all__=['SoundNodeWrapper']

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pConfigDefs import *
from core.pSoundManager import soundManager

DEBUG = False

class SoundNodeWrapper(VirtualNodeWrapper):
  className = '3dSound'
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'NodePath'
    objectInstance = super(SoundNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setSound(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent, name):
    VirtualNodeWrapper.__init__(self, parent, name, SOUNDNODE_WRAPPER_DUMMYOBJECT)
    
    self.soundEffect = None
    self.soundFilepath = None
    
    self.mutableParameters['volume']    = [ float,
        self.getVolume,
        self.setVolume,
        None,
        None,
        True ]
    '''self.mutableParameters['loop']      = [ bool,
      self.getLoop,
      self.setLoop,
      None,
      None ]
    self.mutableParameters['loopCount'] = [ int,
      self.getLoopCount,
      self.setLoopCount,
      None,
      None ]'''
    self.mutableParameters['playRate']  = [ float,
        self.getPlayRate,
        self.setPlayRate,
        None,
        None,
        True ]
    self.mutableParameters['priority']  = [ int,
        self.getPriority,
        self.setPriority,
        None,
        None,
        True ]
    self.mutableParameters['minDistance']  = [ float,
        self.getSoundMinDistance,
        self.setSoundMinDistance,
        None,
        None,
        True ]
    self.mutableParameters['maxDistance']  = [ float,
        self.getSoundMaxDistance,
        self.setSoundMaxDistance,
        None,
        None,
        True ]
  
  def getVolume(self, *args, **kwargs):
    self.soundEffect.getVolume(*args, **kwargs)
  def setVolume(self, *args, **kwargs):
    self.soundEffect.setVolume(*args, **kwargs)
  
  '''def getLoop(self, *args, **kwargs):
    self.soundEffect.getLoop(*args, **kwargs)
  def setLoop(self, *args, **kwargs):
    self.soundEffect.setLoop(*args, **kwargs)
  
  def getLoopCount(self, *args, **kwargs):
    self.soundEffect.getLoopCount(*args, **kwargs)
  def setLoopCount(self, *args, **kwargs):
    self.soundEffect.setLoopCount(*args, **kwargs)'''
  
  def getPlayRate(self, *args, **kwargs):
    self.soundEffect.getPlayRate(*args, **kwargs)
  def setPlayRate(self, *args, **kwargs):
    self.soundEffect.setPlayRate(*args, **kwargs)
  
  def getPriority(self, *args, **kwargs):
    self.soundEffect.getPriority(*args, **kwargs)
  def setPriority(self, *args, **kwargs):
    self.soundEffect.setPriority(*args, **kwargs)
  
  def play(self, *args, **kwargs):
    self.soundEffect.play()
  
  def getSoundMinDistance(self, *args, **kwargs):
    soundManager.get3dManager().getSoundMinDistance(self.soundEffect, *args, **kwargs)
  def setSoundMinDistance(self, *args, **kwargs):
    soundManager.get3dManager().setSoundMinDistance(self.soundEffect, *args, **kwargs)
  
  def getSoundMaxDistance(self, *args, **kwargs):
    soundManager.get3dManager().getSoundMaxDistance(self.soundEffect, *args, **kwargs)
  def setSoundMaxDistance(self, *args, **kwargs):
    soundManager.get3dManager().setSoundMaxDistance(self.soundEffect, *args, **kwargs)
  
  def setSound(self, soundFilepath):
    # if there is already a model defined, remove it
    if self.soundEffect is not None:
      self.soundEffect.remove()
    
    if soundFilepath is not None:
      filepath = str(Filename.fromOsSpecific(soundFilepath))
      # add the model path to the panda-path
      pandaPath = None
      from pandac.PandaModules import getModelPath
      for searchPath in str(getModelPath()).split():
        if searchPath == filepath:
          pandaPath = searchPath
      if pandaPath is None:
        pandaPath = '/'.join(filepath.split('/')[:-1])
        from pandac.PandaModules import getModelPath
        getModelPath().appendPath(pandaPath)
      
      # the path to the model we handle
      self.soundFilepath = soundFilepath
      self.setFilepath(soundFilepath)
      # load the model
      self.soundEffect = soundManager.get3dManager().loadSfx(soundFilepath)
    
    # if the model loading fails or no path given, use a dummy object
    if self.soundEffect is None:
      print "W: NodePathWrapper.setModel: model could not be loaded, loading dummy"
      self.soundEffect = soundManager.get3dManager().loadSfx(SOUND_NOT_FOUND_SOUND)
    # make the model visible
    soundManager.get3dManager().attachSoundToObject( self.soundEffect, self )
    
    self.soundEffect.setLoop(True)
    self.soundEffect.play()
    soundManager.get3dManager().setSoundVelocityAuto( self.soundEffect )
  
  def destroy(self):
    # destroy this object
    soundManager.get3dManager().detachSound(self.soundEffect)
    self.soundEffect.stop()
    del self.soundEffect
    self.soundEffect = None
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.soundFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setSound(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
