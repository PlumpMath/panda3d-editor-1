__all__=['GeoMipTerrainNodeWrapper']

import gc

from pandac.PandaModules import *

from direct.showbase.DirectObject import DirectObject

from core.pWindow import WindowManager
#from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pGeoMipTerrainNodeWrapper.pGeomMipTerrainHeightfield import *
from core.modules.pBaseWrapper import *
from core.pConfigDefs import *

DEBUG = False

GEOMIPTERRAIN_USE_HIGHLIGHTMODEL = False

class GeoMipTerrainNodeWrapper(BaseWrapper, DirectObject):
  className = 'GeoMipTerrain'
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'GeoMipTerrain'
    objectInstance = super(GeoMipTerrainNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setHeightfield(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent=None, name=None):
    BaseWrapper.__init__(self, parent, name)
    # the actual geomipterrainheightfield
    self.terrain = GeoMipTerrain("GeoMipTerrainNodeWrapper")
    self.terrain.getRoot().reparentTo(self.getNodepath())
    
    # model used to show highlighting of this node
    self.highlightModel = None
    
    # node which we use to paint the heightfield
    self.geoMipTerrainHeightfield = GeoMipTerrainHeightfield(parent=self, geoMipTerrain=self)
    
    self.mutableParameters['minlevel'] = [ int,
        self.terrain.getMinLevel,
        self.terrain.setMinLevel,
        None,
        None,
        True ]
    self.mutableParameters['bruteforce'] = [ bool,
        self.terrain.getBruteforce,
        self.terrain.setBruteforce,
        None,
        None,
        True ]
    
    # panda version 1.5 and below
    if PandaSystem.getMinorVersion() < 6:
      # this doesnt work with 1.6 anymore (getFactor missing)
      self.terrainFactor = 1.0
      self.mutableParameters['factor'] = [ float,
          self.getFactor,
          self.setFactor,
          None,
          None,
          True ]
    else:
      # this doesnt work with 1.6 anymore (getFactor missing)
      self.terrainNear = 10
      self.mutableParameters['terrainNear'] = [ float,
          self.getTerrainNear,
          self.setTerrainNear,
          None,
          None,
          True ]
      self.terrainFar = 25
      self.mutableParameters['terrainFar'] = [ float,
          self.getTerrainFar,
          self.setTerrainFar,
          None,
          None,
          True ]
    
    self.mutableParameters['blocksize'] = [ int,
        self.terrain.getBlockSize,
        self.terrain.setBlockSize,
        None,
        None,
        True ]
    
    self.mutableParameters['heightfield'] = [ Filepath,
        self.getHeightfield,
        self.setHeightfield,
        None,
        None,
        True ]
    
    # defines the maximum update rate of the terrain
    self.maxTerrainUpdateRate = 10
    # stores the last update time
    self.lastTerrainUpdateTime = globalClock.getRealTime()
    self.mutableParameters['update rate'] = [ float,
        self.getMaxTerrainUpdateRate,
        self.setMaxTerrainUpdateRate,
        None,
        None,
        True ]
  
  if PandaSystem.getMinorVersion() < 6:
    def getFactor(self):
      return self.terrainFactor
    def setFactor(self, factor):
      self.terrainFactor = factor
      self.terrain.setFactor(self.terrainFactor)
  else:
    def getTerrainNear(self):
      return self.terrainNear
    def setTerrainNear(self, terrainNear):
      self.terrainNear = terrainNear
      self.terrain.setNear(terrainNear)
    def getTerrainFar(self):
      return self.terrainFar
    def setTerrainFar(self, terrainFar):
      self.terrainFar = terrainFar
      self.terrain.setFar(terrainFar)
  
  def setEditmodeEnabled(self):
    BaseWrapper.setEditmodeEnabled(self)
    self.getNodepath().setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
    self.accept(EVENT_CAMERAPIVOT_POSITION_CHANGE, self.cameraFocusUpdate)
    self.geoMipTerrainHeightfield.setEditmodeEnabled()
  
  def setEditmodeDisabled(self):
    self.ignore(EVENT_CAMERAPIVOT_POSITION_CHANGE)
    BaseWrapper.setEditmodeDisabled(self)
    self.getNodepath().setCollideMask(BitMask32.allOff())
    self.geoMipTerrainHeightfield.setEditmodeDisabled()
  
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
    # XXX TODO i dont know and i dont care anymore
    # it's ridiculously slow
    if True:
      # the code that i'd like to use
      currentTime = globalClock.getRealTime()
      if (currentTime - self.lastTerrainUpdateTime) > 1./self.maxTerrainUpdateRate:
        self.lastTerrainUpdateTime = currentTime
        
        pixelPos = self.getPixelPosScaled(focusPoint)
        self.terrain.setFocalPoint(pixelPos)
        
        changed = self.terrain.update()
        if changed:
          self.updateHighlightModel()
        
        # some bugfix try, 
        #self.terrain.getRoot().setScale(self.terrain.getRoot().getScale())
    else:
      # code to figure out what's slowing down the application
      pixelPos = self.getPixelPosScaled(focusPoint)
      #t1 = globalClock.getRealTime()
      self.terrain.setFocalPoint(pixelPos)
      #self.terrain.setFocalPoint(Point2(0.3,0.1))
      #t2 = globalClock.getRealTime()
      self.terrain.update()
      #self.updateHighlightModel()
      #t3 = globalClock.getRealTime()
      #del focusPoint
      #del pixelPos
      #print "I: GeoMipTerrainNodeWrapper.cameraFocusUpdate:", focusPoint, t2-t1, t3-t2
  
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
    if self.isEditmodeStarted() and GEOMIPTERRAIN_USE_HIGHLIGHTMODEL:
      print "I: GeoMipTerrainNodeWrapper.updateHighlightModel:"
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
  
  def setHeightfield(self, filepath):
    ''' define a new heightmap '''
    
    if filepath:
      # it's a absolute filepath, convert it to a relative
      if filepath[0] == '/':
        relativePath = posixpath.dirname(self.getParentFilepath())
        filepath = relpath(relativePath, posixpath.abspath(filepath))
    
    #if self.geoMipTerrainHeightfield:
    #  self.geoMipTerrainHeightfield.destroy()
    #self.geoMipTerrainHeightfield = GeoMipTerrainHeightfield(parent=self, geoMipTerrain=self)
    self.geoMipTerrainHeightfield.heightfield = filepath
    self.update()
    
    #if self.isEditmodeEnabled():
    #  self.geoMipTerrainHeightfield.setEditmodeEnabled()
  
  def getHeightfield(self):
    if self.geoMipTerrainHeightfield:
      return self.geoMipTerrainHeightfield.heightfield
    # in case there was no valid heightfield on creation
    return ''
  
  def update(self):
    ''' update the terrain using the new/modified heighfield '''
    print "I: GeoMipTerrainNodeWrapper.update"
    fullHeightfieldPath = posixpath.join(posixpath.dirname(self.getParentFilepath()), self.geoMipTerrainHeightfield.heightfield)
    self.terrain.setHeightfield(Filename(fullHeightfieldPath))
    
    # destroy a old terrain
    #if self.terrain.getRoot() is not None:
    #  self.terrain.getRoot().detachNode()
    
    # reparent to our node
    #self.terrain.getRoot().reparentTo(self.getNodepath())
    
    # scale so it's 100x100 units large and of 10 units height
    hf = self.terrain.heightfield()
    self.terrain.getRoot().setScale(1./(hf.getXSize()-1)*100, 1./(hf.getYSize()-1)*100, 10.)
    
    self.terrain.generate()
    
    self.updateHighlightModel()
  
  def duplicate(self, original):
    objectInstance = super(GeoMipTerrainNodeWrapper, self).duplicate(original)
    #objectInstance.setTerrain(original.geoMipTerrainHeightfield.heightfield)
    return objectInstance
  duplicate = classmethod(duplicate)

