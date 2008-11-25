import traceback

from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *
from core.pCommonPath import *

class ParticleSystemWrapper(VirtualNodeWrapper):
  def onCreateInstance( self, parent, filename ):
    # check if model file is in pandaModelPath
    from pandac.PandaModules import getModelPath
    pandaPath = None
    filename = str(Filename.fromOsSpecific(filename))
    '''
    for searchPath in str(getModelPath()).split():
        if searchPath in filename:
            pandaPath = searchPath
            print "I: model found in pandaModelPath %s" % pandaPath
            break
    if pandaPath is None:
        pandaPath = '/'.join(filename.split('/')[:-1])
        print "W: adding %s to pandaModelPath" % pandaPath
        from pandac.PandaModules import getModelPath, getTexturePath, getSoundPath
        getModelPath( ).appendPath( pandaPath )
        getTexturePath( ).appendPath( pandaPath )
        getSoundPath( ).appendPath( pandaPath )
    filename = filename.replace( pandaPath, '.' )
    '''
    objectInstance = self(filename, parent)
    #
    objectInstance.enableEditmode()
    # set as active object be the editor
    modelController.selectModel( objectInstance )
    #
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__( self, particleFilename, parent=None ):
    print "I: NodePathWrapper.__init__:", particleFilename
    # define the name of this object
    name = particleFilename.split('/')[-1]
    VirtualNodeWrapper.__init__(self, PARTICLE_WRAPPER_DUMMYOBJECT, name, parent)
    #BaseWrapper.__init__( self, name, parent )
    
    self.particleFilename = particleFilename
    
    base.enableParticles()
    self.particleSystem = ParticleEffect()
    self.loadParticleConfig( self.particleFilename )
  
  def loadParticleConfig(self,file):
    try:
      #Start of the code from steam.ptf
      self.particleSystem.loadConfig(Filename(file))
    except:
      print "W: particleSystemWrapper.loadParticleConfig: Error loading file", file
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
  
  '''def enableEditmode( self ):
    # enables the edit methods of this object
    # makes it pickable etc.
    # create a collision for the object
    center = Point3(0,0,0)
    radius = 1
    cs = CollisionSphere( center, radius )
    self.modelCollisionNodePath = self.attachNewNode(CollisionNode('cnode'))
    self.modelCollisionNodePath.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG,'')
    self.modelCollisionNodePath.node().addSolid(cs)
    # edit mode is enabled
    BaseWrapper.enableEditmode( self )
    self.modelCollisionNodePath.node().setIntoCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
    self.modelCollisionNodePath.node().setFromCollideMask( BitMask32.allOff() )
    self.modelCollisionNodePath.reparentTo( self )
    # load a dummy model
    self.model = loader.loadModel( PARTICLE_WRAPPER_DUMMYOBJECT )
    # set the model invisible in the scenegraphbrowser
    self.model.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG,'')
    self.model.setLightOff()
    # keep the model at a fixed scale
    effect=CompassEffect.make(render, CompassEffect.PScale)
    self.model.setEffect( effect )
    # make the model visible
    self.model.reparentTo( self )#.parent )
    #self.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
  def disableEditmode( self ):
    # disables the edit methods of this object
    # -> performance increase
    # edit mode is disabled
    BaseWrapper.disableEditmode( self )
    #self.setCollideMask( BitMask32.allOff() )
    self.modelCollisionNodePath.node().setIntoCollideMask( BitMask32.allOff() )
    self.modelCollisionNodePath.node().setFromCollideMask( BitMask32.allOff() )
    self.modelCollisionNodePath.removeNode()
    self.modelCollisionNodePath.detachNode()
    # hide the pivot
    self.model.removeNode()
    self.model.detachNode()'''
  
  '''def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit( self )
  def stopEdit( self ):
    # the object is deselected from being edited
    BaseWrapper.stopEdit( self )'''
  
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
    particleFilename = relpath( relativeTo, os.path.abspath(self.particleFilename) )
    # add the reference to the egg-file
    ext = EggExternalReference( nodeName+"-EggExternalReference", particleFilename )
    instance.addChild(ext)
    return instance
  

