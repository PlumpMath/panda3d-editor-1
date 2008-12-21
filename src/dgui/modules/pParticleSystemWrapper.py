import traceback

from dgui.modules.pBaseWrapper import *

PARTICLESYSTEMWRAPPER_SHOW_PARTICLEPANEL = True

TKINTER_AVAILABLE = False
if PARTICLESYSTEMWRAPPER_SHOW_PARTICLEPANEL:
  try:
    import _tkinter
    TKINTER_AVAILABLE = True
    base.startTk()
    from direct.tkpanels.ParticlePanel import ParticlePanel
  except:
    print "W: dgui.ParticleSystemWrapper: tkInter is not installed, editing particlesystems impossible"

class ParticleSystemWrapper( BaseWrapper ):
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    if TKINTER_AVAILABLE:
      self.particlePanel = ParticlePanel( self.object.particleSystem )
  def stopEdit(self):
    # the object is deselected from being edited
    BaseWrapper.stopEdit(self)
    if TKINTER_AVAILABLE:
      try:
        self.particlePanel.destroy()
      except:
        print "W: dgui.ParticleSystemWrapper.stopEdit: particelPanel destroy failed"
        traceback.print_exc()