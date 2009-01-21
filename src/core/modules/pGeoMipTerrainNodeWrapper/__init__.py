__all__=['GeoMipTerrainNodeWrapper']

from pandac.PandaModules import *

#from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pGeoMipTerrainNodeWrapper.pGeomMipTerrainHeightfield import *
from core.modules.pBaseWrapper import *
from core.pConfigDefs import *

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
  
  def setEditmodeEnabled(self, recurseException=[]):
    BaseWrapper.setEditmodeEnabled(self, recurseException)
    self.nodePath.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def setEditmodeDisabled(self, recurseException=[]):
    BaseWrapper.setEditmodeDisabled(self, recurseException)
    self.nodePath.setCollideMask(BitMask32.allOff())
  
  def __init__(self, parent=None, name=None):
    #name = "GeoMipTerrain-"+filepath.split('/')[-1]
    BaseWrapper.__init__(self, parent, name)
    self.terrain = GeoMipTerrain("mySimpleTerrain")
    self.terrainNode = None
    
    self.mutableParameters['minlevel'] = [ int,
      self.terrain.getMinLevel,
      self.terrain.setMinLevel,
      None,
      None ]
  
  def setTerrain(self, filepath):
    parent = self
    heightfield = filepath
    node = self
    self.geoMipTerrainHeightfield = GeoMipTerrainHeightfield(parent, node)
    self.geoMipTerrainHeightfield.setHeightfield(heightfield)
    self.update()
  
  def update(self):
    self.terrain.setHeightfield(Filename(self.geoMipTerrainHeightfield.heightfield))
    if self.terrainNode is not None:
      self.terrainNode.detachNode()
    self.terrainNode = self.terrain.getRoot()
    self.terrain.getRoot().reparentTo(self.nodePath)
    self.terrain.getRoot().setSz(25)
    self.terrain.generate()
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.terrainImageFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setTerrain(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeInstance(self, original):
    objectInstance = super(GeoMipTerrainNodeWrapper, self).makeInstance(original)
    objectInstance.setTerrain(original.geoMipTerrainHeightfield.heightfield)
    return objectInstance
  makeInstance = classmethod(makeInstance)

