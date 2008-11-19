from dgui.modules.pBaseWrapper import *

TKINTER_AVAILABLE = False
if PARTICLESYSTEMWRAPPER_SHOW_PARTICLEPANEL:
  try:
    import _tkinter
    TKINTER_AVAILABLE = True
    base.startTk()
    from direct.tkpanels.ParticlePanel import ParticlePanel
  except:
    print "W: ParticleSystemWrapper: tkInter is not installed, editing particlesystems impossible"

class ParticleSystemWrapper( BaseWrapper ):
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    self.model.showBounds()
    BaseWrapper.startEdit( self )
    if TKINTER_AVAILABLE:
      self.particlePanel = ParticlePanel( self.particleSystem )
  def stopEdit( self ):
    # the object is deselected from being edited
    self.model.hideBounds()
    BaseWrapper.stopEdit( self )
    if TKINTER_AVAILABLE:
      try:
        self.particlePanel.destroy()
      except:
        print "W: ParticleSystemWrapper.stopEdit:"