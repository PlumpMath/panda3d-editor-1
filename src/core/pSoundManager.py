import traceback

from direct.showbase import Audio3DManager
from pandac.PandaModules import *

class SoundManager:
  def __init__(self):
    base.enableAllAudio()
    base.enableMusic(True) #bEnableMusic)
    base.enableSoundEffects(True) #bEnableSoundEffects)
    self.sound3dListener = NodePath('3dSoundListener')
    self.sound3dListener.reparentTo(render)
    self.sound3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], self.sound3dListener)
  
  def stuff(self):
    # this is not actually used, it's here for reference, what features we may implement
    '''
    self.sound3d.setDistanceFactor(scale)
    self.sound3d.setDropOffFactor(scale)
    '''
  
  def createListener(self):
    pass
  
  def get3dManager(self):
    return self.sound3d
  
  def setDoppler(self, sound):
    try:
      self.sound3d.setSoundVelocityAuto(sound)
      self.sound3d.setListenerVelocityAuto()
    except:
      print "W: SoundManager.setDoppler: sound invalid"
      traceback.print_exc()

soundManager = SoundManager()