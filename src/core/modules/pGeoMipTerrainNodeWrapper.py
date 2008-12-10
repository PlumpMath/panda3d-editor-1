from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

DEBUG = False

class GeoMipTerrainNodeWrapper(BaseWrapper):
  def onCreateInstance(self, parent, filepath):
    if filepath != ' ' and filepath != None:
      print "I: GeoMipTerrainNodeWrapper:", filepath
      filepath = str(Filename.fromOsSpecific(filepath))
      
      # create instance of this class
      objectInstance = self(parent, filepath)
      # enable editing of this object
      objectInstance.enableEditmode()
      
      return objectInstance
    return None
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = os.path.join(filepath,str(referencedFilename))
      objectInstance = self.onCreateInstance(parent, filename)
      objectInstance.setLoadData(eggGroup)
      return objectInstance
    else:
      print "I: PgmmNodeWrapper.loadFromEggGroup: no externalReference found in"
      print "  -", eggGroup
    return None
#    objectInstance = self.onCreateInstance(parent, filepath)
#    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def enableEditmode(self):
    # enables the edit methods of this object
    # makes it pickable etc.
    # edit mode is enabled
    BaseWrapper.enableEditmode(self)
    self.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def disableEditmode(self):
    # disables the edit methods of this object
    # -> performance increase
    # edit mode is disabled
    BaseWrapper.disableEditmode( self )
    self.setCollideMask(BitMask32.allOff())
  
  def __init__(self, parent, filepath):
    name = "GeoMipTerrain-"+filepath.split('/')[-1]
    BaseWrapper.__init__(self, name, parent)
    self.terrainImageFilepath = filepath
    terrain = GeoMipTerrain("mySimpleTerrain")
    terrain.setHeightfield(Filename(filepath))
    terrain.getRoot().reparentTo(self)
    terrain.getRoot().setSz(25)
    terrain.generate()
  
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
  def setLoadData(self, eggGroup):
    BaseWrapper.setLoadData(self, eggGroup)
