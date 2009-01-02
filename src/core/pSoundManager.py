import traceback

from direct.showbase import Audio3DManager
from pandac.PandaModules import *

class SoundManager:
  def __init__(self):
    self.enabled = False
  
  def enable(self):
    if not self.enabled:
      base.enableAllAudio()
      base.enableMusic(True) #bEnableMusic)
      base.enableSoundEffects(True) #bEnableSoundEffects)
      self.sound3dListener = NodePath('3dSoundListener')
      self.sound3dListener.reparentTo(render)
      self.sound3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], self.sound3dListener)
    
    self.enabled = True
  
  def disable(self):
    self.enabled = False
  
  def createListener(self):
    pass
  
  def get3dManager(self):
    if self.enabled:
      return self.sound3d
    print "E: SoundManager.get3dManager: is not enabled"
  
  def setDoppler(self, sound):
    if self.enabled:
      try:
        self.sound3d.setSoundVelocityAuto(sound)
        self.sound3d.setListenerVelocityAuto()
      except:
        print "W: SoundManager.setDoppler: sound invalid"
        traceback.print_exc()
    else:
      print "E: SoundManager.setDoppler: is not enabled"

soundManager = SoundManager()