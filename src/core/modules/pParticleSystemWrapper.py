import traceback

from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *
from core.pCommonPath import *

DEBUG = False

class ParticleSystemWrapper(VirtualNodeWrapper):
  def onCreateInstance(self, parent, filepath):
    print "I: ParticleSystemWrapper.onCreateInstance:"
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
      print "  - adding to pandapath:", pandaPath
      getModelPath().appendPath( pandaPath )
    
    # create instance of this class
    objectInstance = self(filepath, parent)
    # enable editing of this object
    objectInstance.enableEditmode()
    # set as active object be the editor
    #modelController.selectModel( objectInstance )
    # update the scenegraph
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
    
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  # parent, filepath
  def loadFromEggGroup( self, eggGroup, parent, eggfileFilepath ):
    if DEBUG:
      print "I: ParticleSystemWrapper.loadFromEggGroup:"
    eggExternalReference = eggGroup.getChildren()[0]
    referencedFilename = eggExternalReference.getFilename()
    filepath = os.path.join(eggfileFilepath,str(referencedFilename))
    print "I: ParticleSystemWrapper.loadFromEggGroup:"
    print "  - referencedFilename:", referencedFilename
    print "  - filepath:", filepath
    print "  - parent:", parent
    objectInstance = self.onCreateInstance(parent, filepath)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  '''def loadFromEggGroup(self, eggGroup, parent, filepath):
    eggComment = eggGroup.getChildren()[0]
    objectInstance = self(parent, filepath)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)'''
  
  def __init__( self, filepath, parent=None ):
    print "I: ParticleSystemWrapper.__init__:"
    print "  - filepath", filepath
    print "  - parent", parent
    # define the name of this object
    name = filepath.split('/')[-1]
    VirtualNodeWrapper.__init__(self, PARTICLE_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.particleFilename = filepath
    
    base.enableParticles()
    self.particleSystem = ParticleEffect()
    self.loadParticleConfig( filepath )
  
  def loadParticleConfig(self, filepath):
    try:
      #Start of the code from steam.ptf
      self.particleSystem.loadConfig(Filename(filepath))
    except:
      print "W: particleSystemWrapper.loadParticleConfig: Error loading file", filepath
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
    instance = EggGroup( nodeName+"-Group" )
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    # userdata is not written to the eggFile
    className = self.__class__.__name__
    instance.setTag( MODEL_WRAPPER_TYPE_TAG, className )
    # convert to a relative path
    filepath = relpath( relativeTo, os.path.abspath(self.particleFilename) )
    # add the reference to the egg-file
    ext = EggExternalReference( nodeName+"-EggExternalReference", filepath )
    instance.addChild(ext)
    return instance
  

