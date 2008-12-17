import traceback, posixpath

from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *
from core.pCommonPath import *

base.enableParticles()

DEBUG = False

class ParticleSystemWrapper(VirtualNodeWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    objectInstance = super(VirtualNodeWrapper, self).onCreateInstance(parent, filepath)
    objectInstance.setParticleConfig(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__( self, parent=None, name=None ):
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
        if DEBUG:
          print "I: ParticleSystemWrapper.setParticleConfig: adding to pandapath:"
          print "  -", pandaPath
        getModelPath().appendPath( pandaPath )
    
    self.particleFilename = filepath
    try:
      #Start of the code from steam.ptf
      self.particleSystem.loadConfig(Filename(filepath))
    except:
      print "W: particleSystemWrapper.setParticleConfig: Error loading file"
      print "  -", filepath
      print "  - Creating dummy particle Effect"
      traceback.print_exc()
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
  
  def getSaveData( self, relativeTo ):
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
        for y in xrange(4):
            nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    nodeName = self.getName()
    instance = EggGroup( nodeName )
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    # userdata is not written to the eggFile
    className = self.__class__.__name__
    instance.setTag( MODEL_WRAPPER_TYPE_TAG, className )
    # convert to a relative path
    filepath = relpath( relativeTo, posixpath.abspath(self.particleFilename) )
    # add the reference to the egg-file
    ext = EggExternalReference( nodeName+"-EggExternalReference", filepath )
    instance.addChild(ext)
    return instance
  
  def loadFromData(self, eggGroup, filepath):
    # search for a external reference
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    # read the reference if it is found
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = posixpath.join(filepath,str(referencedFilename))
      self.setParticleConfig(filename)
    else:
      print "I: NodePathWrapper.loadFromData: no externalReference found in"
      print "  -",eggGroup
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
