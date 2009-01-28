__all__=['GeoMipTerrainNodeWrapper']

from pandac.PandaModules import *

#from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pGeoMipTerrainNodeWrapper.pGeomMipTerrainHeightfield import *
from core.modules.pBaseWrapper import *
from core.pConfigDefs import *

DEBUG = False


class GeoMipTerrainNodeWrapper(BaseWrapper):
  className = 'GeoMipTerrain'
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
  
  def setEditmodeEnabled(self):
    BaseWrapper.setEditmodeEnabled(self)
    self.getNodepath().setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def setEditmodeDisabled(self):
    BaseWrapper.setEditmodeDisabled(self)
    self.getNodepath().setCollideMask(BitMask32.allOff())
  
  def __init__(self, parent=None, name=None):
    BaseWrapper.__init__(self, parent, name)
    self.terrain = GeoMipTerrain("GeoMipTerrainNodeWrapper")
    self.terrainNode = None
    
    # model used to show highlighting of this node
    self.highlightModel = None
    
    self.mutableParameters['minlevel'] = [ int,
      self.terrain.getMinLevel,
      self.terrain.setMinLevel,
      None,
      None ]
    self.mutableParameters['bruteforce'] = [ bool,
      self.terrain.getBruteforce,
      self.terrain.setBruteforce,
      None,
      None ]
    self.mutableParameters['factor'] = [ float,
      self.terrain.getFactor,
      self.terrain.setFactor,
      None,
      None ]
    self.mutableParameters['blocksize'] = [ int,
      self.terrain.getBlockSize,
      self.terrain.setBlockSize,
      None,
      None ]
  
  def startEdit(self):
    print "I: GeoMipTerrainNodeWrapper.startEdit:"
    print "  - terrain", self.terrain.heightfield()
    print "  - scale", self.terrainNode.getScale(render)
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    if self.isEditmodeEnabled():
      if self.highlightModel is None:
        self.highlightModel = self.terrainNode.copyTo(self.getNodepath())
      self.highlightModel.setRenderModeWireframe(True)
      self.highlightModel.setLightOff(1000)
      self.highlightModel.setFogOff(1000)
      self.highlightModel.setTextureOff(1000)
      self.highlightModel.clearColorScale()
      self.highlightModel.setColor(HIGHLIGHT_COLOR[0], HIGHLIGHT_COLOR[1], HIGHLIGHT_COLOR[2], 1000)
  
  def stopEdit(self):
    # the object is deselected from being edited
    if self.isEditmodeEnabled():
      if self.highlightModel is not None:
        self.highlightModel.removeNode()
        self.highlightModel = None
    BaseWrapper.stopEdit(self)
  
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
    self.terrain.getRoot().reparentTo(self.getNodepath())
    hf = self.terrain.heightfield()
    self.terrain.getRoot().setScale(1./(hf.getXSize()-1)*100, 1./(hf.getYSize()-1)*100, 1.)
    self.terrain.generate()
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.geoMipTerrainHeightfield.heightfield, relativeTo, objectInstance)
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

