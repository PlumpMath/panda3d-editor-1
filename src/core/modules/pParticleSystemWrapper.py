import traceback

from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

PARTICLES_ENABLED = False

DEBUG = False

class ParticleSystemWrapper(VirtualNodeWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    objectInstance = super(VirtualNodeWrapper, self).onCreateInstance(parent, filepath)
    objectInstance.setParticleConfig(filepath)
    #objectInstance.setTransparency(True)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__( self, parent=None, name=None ):
    global PARTICLES_ENABLED
    if not PARTICLES_ENABLED:
      base.enableParticles()
      PARTICLES_ENABLED = True
    # define the name of this object
    VirtualNodeWrapper.__init__(self, parent, name, PARTICLE_WRAPPER_DUMMYOBJECT)
    
    self.particleSystem = ParticleEffect()
  
  def setParticleConfig(self, filepath):
    if filepath is not None:
      # check if model file is in pandaModelPath
      filepath = str(Filename.fromOsSpecific(filepath))
      
      # add the model path to the panda-path
      pandaPath = None
      from pandac.PandaModules import getModelPath
      for searchPath in str(getModelPath()).split():
        if searchPath == filepath:
          pandaPath = searchPath
      if pandaPath is None:
        pandaPath = '/'.join(filepath.split('/')[:-1])
        from pandac.PandaModules import getModelPath
        getModelPath().appendPath( pandaPath )
    
    self.particleFilename = filepath
    try:
      #Start of the code from steam.ptf
      self.particleSystem.loadConfig(Filename(filepath))
    except:
      print "W: particleSystemWrapper.setParticleConfig: Error loading file"
      print "  -", filepath
      traceback.print_exc()
      
      print "  - Creating dummy particle Effect"
      # create new one if loading failed (particlepanel requires at least one particle)
      particles = Particles()
      particles.setBirthRate(0.02)
      particles.setLitterSize(10)
      particles.setLitterSpread(0)
      particles.setFactory("PointParticleFactory")
      particles.setRenderer("PointParticleRenderer")
      particles.setEmitter("SphereVolumeEmitter")
      particles.enable()
      self.particleSystem.addParticles(particles)
    #Sets particles to birth relative to the teapot, but to render at toplevel
    self.particleSystem.start(self)
  
  def destroy( self ):
    # destroy this object
    VirtualNodeWrapper.destroy( self )
  
  def getSaveData(self, relativeTo):
    objectInstance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.particleFilename, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setParticleConfig(extRefFilename)
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeCopy(self, original):
    objectInstance = super(ParticleSystemWrapper, self).makeCopy(original)
    objectInstance.setParticleConfig(original.particleFilename)
    return objectInstance
  makeCopy = classmethod(makeCopy)
  
