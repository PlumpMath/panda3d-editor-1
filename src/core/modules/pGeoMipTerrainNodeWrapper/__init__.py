__all__=['GeoMipTerrainNodeWrapper']

from pandac.PandaModules import *

from direct.showbase.DirectObject import DirectObject

from core.pWindow import WindowManager
#from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pGeoMipTerrainNodeWrapper.pGeomMipTerrainHeightfield import *
from core.modules.pBaseWrapper import *
from core.pConfigDefs import *

DEBUG = False


class GeoMipTerrainNodeWrapper(BaseWrapper, DirectObject):
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
  
  def __init__(self, parent=None, name=None):
    BaseWrapper.__init__(self, parent, name)
    self.terrain = GeoMipTerrain("GeoMipTerrainNodeWrapper")
    
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
    # this doesnt work with 1.6 anymore (getFactor missing)
    self.terrainFactor = 1.0
    self.mutableParameters['factor'] = [ float,
      self.getFactor,
      self.setFactor,
      None,
      None ]
    
    self.mutableParameters['blocksize'] = [ int,
      self.terrain.getBlockSize,
      self.terrain.setBlockSize,
      None,
      None ]
    # defines the maximum update rate of the terrain
    self.maxTerrainUpdateRate = 30
    # stores the last update time
    self.lastTerrainUpdateTime = globalClock.getRealTime()
    self.mutableParameters['update rate'] = [ float,
      self.getMaxTerrainUpdateRate,
      self.setMaxTerrainUpdateRate,
      None,
      None]
  
  def getFactor(self):
    return self.terrainFactor
  def setFactor(self, factor):
    self.terrainFactor = factor
    self.terrain.setFactor(self.terrainFactor)
  
  def setEditmodeEnabled(self):
    BaseWrapper.setEditmodeEnabled(self)
    self.getNodepath().setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
    self.accept(EVENT_CAMERAPIVOT_POSITION, self.cameraFocusUpdate)
  
  def setEditmodeDisabled(self):
    self.ignore(EVENT_CAMERAPIVOT_POSITION)
    BaseWrapper.setEditmodeDisabled(self)
    self.getNodepath().setCollideMask(BitMask32.allOff())
  
  def startEdit(self):
    ''' the object is selected to be edited
    creates a directFrame to edit this object '''
    BaseWrapper.startEdit(self)
    if self.isEditmodeEnabled():
      self.updateHighlightModel()
  
  def stopEdit(self):
    ''' the object is deselected from being edited '''
    if self.isEditmodeEnabled():
      if self.highlightModel is not None:
        self.highlightModel.removeNode()
        self.highlightModel = None
    BaseWrapper.stopEdit(self)
  
  # --- helper functions to find pixel position of the heightfield ---
  def getPixelPos(self, pos):
    ''' convert a global position into the pixel coordinates of the terrain '''
    pixelPos = self.terrain.getRoot().getRelativePoint(render, pos)
    return pixelPos
  
  def getPixelPosScaled(self, pos):
    ''' some fix for a bug in geomipterrain '''
    pixelPos = self.getPixelPos(pos)
    hf = self.terrain.heightfield()
    pixelPos = Point2(
        pixelPos.getX() / (hf.getXSize()-1)*100,
        pixelPos.getY() / (hf.getYSize()-1)*100
      )
    return pixelPos
  
  def getMaxTerrainUpdateRate(self):
    return self.maxTerrainUpdateRate
  def setMaxTerrainUpdateRate(self, rate):
    # limit from 1 (every second) to 100 (100 times per second)
    rate = max(0.01, min(100, rate))
    self.maxTerrainUpdateRate = rate
  
  def cameraFocusUpdate(self, focusPoint):
    ''' update the focus point of the terrain, focusPoint must be relative to render
    update rate is limited by the maxTerrainUpdateRate
    '''
    pixelPos = self.getPixelPosScaled(focusPoint)
    self.terrain.setFocalPoint(pixelPos)
    currentTime = globalClock.getRealTime()
    if (currentTime - self.lastTerrainUpdateTime) > 1./self.maxTerrainUpdateRate:
      self.lastTerrainUpdateTime = currentTime
      changed = self.terrain.update()
      if changed and self.isEditmodeEnabled():
        self.updateHighlightModel()
  
  def getHeight(self, playerPos):
    ''' get elevation of the terrain at the given position
    '''
    if type(playerPos) in [Vec3, Vec2, Point3, Point2]:
      pixelPos = self.getPixelPos(Vec3(playerPos.getX(), playerPos.getY(), 0))
      baseElevation = self.terrain.getElevation(pixelPos.getX(), pixelPos.getY())
      elevation = render.getRelativePoint( self.terrain.getRoot(), Vec3(0,0,baseElevation) ).getZ()
    else:
      return None
    return elevation
  
  def updateHighlightModel(self):
    ''' update the wireframe model of the heightfield '''
    if self.isEditmodeStarted():
      if self.highlightModel is not None:
        self.highlightModel.removeNode()
      self.highlightModel = self.terrain.getRoot().copyTo(self.getNodepath())
      self.highlightModel.setRenderModeWireframe(True)
      self.highlightModel.setLightOff(1000)
      self.highlightModel.setFogOff(1000)
      self.highlightModel.setTextureOff(1000)
      self.highlightModel.setShaderOff(1000)
      self.highlightModel.setColorScaleOff(1000)
      self.highlightModel.setColorOff(1000)
      self.highlightModel.setColor(HIGHLIGHT_COLOR[0], HIGHLIGHT_COLOR[1], HIGHLIGHT_COLOR[2], 1000)
  
  def setTerrain(self, filepath):
    ''' define a new heightmap '''
    parent = self
    heightfield = filepath
    node = self
    self.geoMipTerrainHeightfield = GeoMipTerrainHeightfield(parent, node)
    self.geoMipTerrainHeightfield.setHeightfield(heightfield)
    self.update()
  
  def update(self):
    ''' update the terrain using the new/modified heighfield '''
    self.terrain.setHeightfield(Filename(self.geoMipTerrainHeightfield.heightfield))
    if self.terrain.getRoot() is not None:
      self.terrain.getRoot().detachNode()
    #self.terrain.getRoot() = self.terrain.getRoot()
    self.terrain.getRoot().reparentTo(self.getNodepath())
    hf = self.terrain.heightfield()
    self.terrain.getRoot().setScale(1./(hf.getXSize()-1)*100, 1./(hf.getYSize()-1)*100, 1.)
    self.terrain.update()
  
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

