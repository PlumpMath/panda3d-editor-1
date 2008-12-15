from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

DEBUG = False

class GeoMipTerrainNodeWrapper(BaseWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'GeoMipTerrain'
    objectInstance = super(GeoMipTerrainNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setTerrain(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def enableEditmode(self):
    BaseWrapper.enableEditmode(self)
    self.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def disableEditmode(self):
    BaseWrapper.disableEditmode(self)
    self.setCollideMask(BitMask32.allOff())
  
  def __init__(self, parent=None, name=None):
    #name = "GeoMipTerrain-"+filepath.split('/')[-1]
    BaseWrapper.__init__(self, parent, name)
    self.terrainNode = None
  
  def setTerrain(self, filepath):
    if self.terrainNode is not None:
      self.terrainNode.detachNode()
    self.terrainImageFilepath = filepath
    self.terrain = GeoMipTerrain("mySimpleTerrain")
    self.terrain.setHeightfield(Filename(filepath))
    self.terrain.getRoot().reparentTo(self)
    self.terrain.getRoot().setSz(25)
    self.terrainNode = self.terrain.generate()
  
  def getSaveData(self, relativeTo):
    ''' link the egg-file into the egg we save
    '''
    name = self.getName()
    instance = BaseWrapper.getSaveData(self, relativeTo)
    # convert to a relative path
    terrainImageFilepath = relpath(relativeTo, os.path.abspath(self.terrainImageFilepath))
    if DEBUG:
      print "I: GeoMipTerrainNodeWrapper.getSaveData: modelFilepath:", terrainImageFilepath, self.terrainImageFilepath, relativeTo
    # add the reference to the egg-file
    ext = EggExternalReference(name+"-EggExternalReference", terrainImageFilepath)
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
      filename = os.path.join(filepath,str(referencedFilename))
      self.setTerrain(filename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)

